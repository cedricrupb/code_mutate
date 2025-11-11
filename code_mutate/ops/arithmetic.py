from .base import MutationOperator
from ..mutation import ASTMutation


def init_arithmetic_operator(source_ast, op):

    if op == "AOD": return ArithmeticOperatorDeletion(source_ast)
    if op == "AOR": return ArithmeticOperatorReplacement(source_ast)
    
    raise ValueError(f"Unknown arithmetic mutation operator {op}")


class ArithmeticOperatorDeletion(MutationOperator):

    def mutate_unary_operator(self, node):
        return ASTMutation(node.children[0], "", op_type = "AOD")


class ArithmeticOperatorReplacement(MutationOperator):

    REPLACEMENTS = {
        "+": ["-"],
        "-": ["+"],
        "*": ["/", "//", "**"],
        "/": ["*", "//"],
        "//": ["/", "*"],
        "%": ["*"],
    }

    def mutate_binary_operator(self, node):
        operator = node.children[1]

        if operator.type in ArithmeticOperatorReplacement.REPLACEMENTS:
            return [ASTMutation(operator, replacement, op_type = "AOR") 
                    for replacement in ArithmeticOperatorReplacement.REPLACEMENTS[operator.type]]
        
    def mutate_unary_operator(self, node):
        operator = node.children[0]

        if operator.type in ArithmeticOperatorReplacement.REPLACEMENTS:
            return [ASTMutation(operator, replacement, op_type = "AOR") 
                    for replacement in ArithmeticOperatorReplacement.REPLACEMENTS[operator.type]]