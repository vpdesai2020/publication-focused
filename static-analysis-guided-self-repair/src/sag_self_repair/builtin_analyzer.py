from __future__ import annotations

import ast
from pathlib import Path

from .schema import AnalyzerRun, ToolFinding


def analyze_python_file(path: Path) -> AnalyzerRun:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError) as exc:
        return AnalyzerRun(
            tool="builtin-python",
            exit_code=1,
            findings=(),
            error=str(exc),
        )

    visitor = _PythonSecurityVisitor(path)
    visitor.visit(tree)
    return AnalyzerRun(
        tool="builtin-python",
        exit_code=1 if visitor.findings else 0,
        findings=tuple(visitor.findings),
    )


class _PythonSecurityVisitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.findings: list[ToolFinding] = []
        self._function_validation_stack: list[bool] = []
        self._url_validation_stack: list[bool] = []
        self._function_args_stack: list[set[str]] = []
        self._function_name_stack: list[str] = []
        self._sql_tainted_names_stack: list[set[str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_validation_stack.append(_contains_path_validation(node))
        self._url_validation_stack.append(_contains_url_validation(node))
        self._function_args_stack.append({arg.arg for arg in node.args.args})
        self._function_name_stack.append(node.name)
        self._sql_tainted_names_stack.append(set())
        self.generic_visit(node)
        self._sql_tainted_names_stack.pop()
        self._function_name_stack.pop()
        self._function_args_stack.pop()
        self._url_validation_stack.pop()
        self._function_validation_stack.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        if _assigns_hardcoded_secret(node):
            self.findings.append(
                self._finding(
                    node,
                    "python.hardcoded-secret",
                    "Avoid hard-coded credentials or API keys.",
                    "CWE-798",
                    "high",
                )
            )
        if self._sql_tainted_names_stack and _is_sql_string_builder(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._sql_tainted_names_stack[-1].add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _call_name(node.func)
        if call_name == "eval":
            self.findings.append(
                self._finding(
                    node,
                    "python.eval-dynamic-code",
                    "Avoid eval on untrusted input.",
                    "CWE-094",
                    "high",
                )
            )
        if call_name == "os.system":
            self.findings.append(
                self._finding(
                    node,
                    "python.os-system",
                    "Avoid os.system for command execution with user-controlled input.",
                    "CWE-078",
                    "high",
                )
            )
        if call_name.startswith("subprocess.") and _keyword_is_true(node, "shell"):
            self.findings.append(
                self._finding(
                    node,
                    "python.subprocess.shell-true",
                    "Avoid shell=True with subprocess calls.",
                    "CWE-078",
                    "high",
                )
            )
        if call_name == "hashlib.md5":
            self.findings.append(
                self._finding(
                    node,
                    "python.hashlib.md5",
                    "Avoid MD5 for security-sensitive hashing.",
                    "CWE-327",
                    "medium",
                )
            )
        if call_name in {"random.randint", "random.randrange", "random.random", "random.choice"}:
            self.findings.append(
                self._finding(
                    node,
                    "python.random.security-token",
                    "Use secrets instead of random for security-sensitive tokens.",
                    "CWE-330",
                    "medium",
                )
            )
        if call_name == "yaml.load":
            self.findings.append(
                self._finding(
                    node,
                    "python.yaml.unsafe-load",
                    "Use yaml.safe_load instead of yaml.load.",
                    "CWE-502",
                    "high",
                )
            )
        if (
            call_name in {"requests.get", "requests.post"}
            and _call_has_tainted_argument(node)
            and not _current_function_has_validation(self._url_validation_stack)
        ):
            self.findings.append(
                self._finding(
                    node,
                    "python.requests.unvalidated-url",
                    "Validate outbound URLs before making server-side requests.",
                    "CWE-918",
                    "high",
                )
            )
        if call_name.endswith(".redirect") or call_name == "redirect":
            if _call_has_tainted_argument(node):
                self.findings.append(
                    self._finding(
                        node,
                        "python.redirect.unvalidated-target",
                        "Validate redirect targets before redirecting users.",
                        "CWE-601",
                        "medium",
                    )
                )
        if call_name.endswith(".execute") and _execute_uses_tainted_sql(node, self._sql_tainted_names_stack):
            self.findings.append(
                self._finding(
                    node,
                    "python.sql.string-query",
                    "Use parameterized SQL queries instead of string-built SQL.",
                    "CWE-089",
                    "high",
                )
            )
        if call_name.endswith(".read_text") and not _current_function_has_validation(self._function_validation_stack):
            self.findings.append(
                self._finding(
                    node,
                    "python.path.unvalidated-read",
                    "Validate resolved paths before reading user-selected files.",
                    "CWE-022",
                    "high",
                )
            )
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        if (
            isinstance(node.value, ast.Name)
            and self._function_args_stack
            and node.value.id in self._function_args_stack[-1]
            and "url" in self._function_name_stack[-1].lower()
            and not _current_function_has_validation(self._url_validation_stack)
        ):
            self.findings.append(
                self._finding(
                    node,
                    "python.redirect.unvalidated-target",
                    "Validate URL redirect targets before returning them to callers.",
                    "CWE-601",
                    "medium",
                )
            )
        self.generic_visit(node)

    def _finding(
        self,
        node: ast.AST,
        rule_id: str,
        message: str,
        cwe: str,
        severity: str,
    ) -> ToolFinding:
        return ToolFinding(
            tool="builtin-python",
            rule_id=rule_id,
            message=message,
            path=self.path.name,
            line=getattr(node, "lineno", None),
            severity=severity,
            cwe=cwe,
        )


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _keyword_is_true(node: ast.Call, name: str) -> bool:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value is True
    return False


def _current_function_has_validation(stack: list[bool]) -> bool:
    return bool(stack and stack[-1])


def _contains_path_validation(node: ast.FunctionDef) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr in {"resolve", "relative_to"}:
            return True
        if isinstance(child, ast.Call) and _call_name(child.func) == "os.path.commonpath":
            return True
    return False


def _contains_url_validation(node: ast.FunctionDef) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr in {"hostname", "netloc", "scheme"}:
            return True
        if isinstance(child, ast.Call) and _call_name(child.func) == "urlparse":
            return True
    return False


def _is_sql_string_builder(node: ast.AST) -> bool:
    if isinstance(node, ast.JoinedStr):
        return _contains_sql_keyword(node)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return _contains_sql_keyword(node)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        return _contains_sql_keyword(node)
    return False


def _contains_sql_keyword(node: ast.AST) -> bool:
    sql_keywords = ("SELECT", "INSERT", "UPDATE", "DELETE")
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            if any(keyword in child.value.upper() for keyword in sql_keywords):
                return True
    return False


def _execute_uses_tainted_sql(node: ast.Call, stack: list[set[str]]) -> bool:
    if not node.args:
        return False
    query_arg = node.args[0]
    if _is_sql_string_builder(query_arg):
        return True
    if isinstance(query_arg, ast.Name) and stack and query_arg.id in stack[-1]:
        return True
    return False


def _call_has_tainted_argument(node: ast.Call) -> bool:
    return bool(node.args and isinstance(node.args[0], ast.Name))


def _assigns_hardcoded_secret(node: ast.Assign) -> bool:
    if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
        return False
    if len(node.value.value) < 8:
        return False
    secret_words = ("key", "token", "secret", "password", "credential")
    for target in node.targets:
        if isinstance(target, ast.Name) and any(word in target.id.lower() for word in secret_words):
            return True
    return False
