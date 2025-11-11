from .base import MutationOperator
from ..mutation import ASTMutation


def init_decorator_operator(source_ast, op):

    if op == "DDL": return DecoratorDeletion(source_ast)
    
    raise ValueError(f"Unknown decorator mutation operator {op}")


class DecoratorDeletion(MutationOperator):

    def mutate_decorator(self, node):
        return ASTMutation(node, "", op_type = "DDL")


