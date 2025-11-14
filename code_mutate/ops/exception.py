from .base import MutationOperator
from ..mutation import ASTMutation


def init_exception_operator(source_ast, op):

    if op == "EHD": return ExceptionHandlerDeletion(source_ast)
    if op == "EXS": return ExceptionSwallowing(source_ast)
    
    raise ValueError(f"Unknown exception mutation operator {op}")


class ExceptionMutation(MutationOperator):

    def _mutate_exception_body(self, clause_body):
        raise NotImplementedError()
    
    def mutate_except_clause(self, node):
        except_body = node.children[-1]
        return self._mutate_exception_body(except_body)


class ExceptionHandlerDeletion(ExceptionMutation):

    def _mutate_exception_body(self, clause_body):
        if clause_body.children and clause_body.children[0].type == "raise_statement":
            return
        return ASTMutation(clause_body, "raise", op_type = "EHD")


class ExceptionSwallowing(ExceptionMutation):

    def _mutate_exception_body(self, clause_body):
        if len(clause_body.children) == 1 and clause_body.children[0].type == "pass_statement":
            return
        return ASTMutation(clause_body, "pass", op_type = "EXS")
