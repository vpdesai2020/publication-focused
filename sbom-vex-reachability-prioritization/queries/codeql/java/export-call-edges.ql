/**
 * @name Export Java/Kotlin call edges
 * @description Emits caller-to-callee edges for lightweight reachability experiments.
 * @kind problem
 * @problem.severity recommendation
 * @id java/export-call-edges
 */

import java

from Call call, Callable caller, Callable callee
where
  caller = call.getEnclosingCallable() and
  callee = call.getCallee()
select call, caller.getQualifiedName() + " -> " + callee.getQualifiedName()

