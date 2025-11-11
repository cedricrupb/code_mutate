from .base import MutationOperator
from ..mutation import ASTMutation


def init_logical_operator(source_ast, op):

    if op == "COD": return ConditionalOperatorDeletion(source_ast)
    if op == "COI": return ConditionalOperatorInsertion(source_ast)
    if op == "LCR": return LogicalConnectorReplacement(source_ast)
    if op == "LOD": return LogicalOperatorDeletion(source_ast)
    if op == "LOR": return LogicalOperatorReplacement(source_ast)
    if op == "ROR": return RelationalOperatorReplacement(source_ast)
    
    raise ValueError(f"Unknown logical mutation operator {op}")



class ConditionalOperatorDeletion(MutationOperator):
    
    def mutate_comparison_operator(self, node):
        for children in node.children:
            if "not" in children.type and self.ast.match(children) == "not":
                return ASTMutation(children, "", op_type = "COD")


class ConditionalOperatorInsertion(MutationOperator):

    def _not_mutation(self, condition):
        if condition.type == "comparison_operator" and "in" in condition.children[1].type:
            return None

        return ASTMutation(condition, f"not ({self.ast.match(condition)})", op_type = "COI")
    
    def mutate_while_statement(self, node):
        return self._not_mutation(node.child_by_field_name("condition"))

    def mutate_if_statement(self, node):
        return self._not_mutation(node.child_by_field_name("condition"))

    def mutate_comparison_operator(self, node):
        if len(node.children) == 3 and node.children[1].type == "in":
            return ASTMutation(node.children[1], "not in", op_type = "COI")

class LogicalConnectorReplacement(MutationOperator):
    
    def mutate_and(self, node):
        return ASTMutation(node, "or", op_type = "LCR")
    
    def mutate_or(self, node):
        return ASTMutation(node, "and", op_type = "LCR")
    
# logical operators ----------------

class LogicalOperatorDeletion(MutationOperator):
    
    def mutate_unary_operator(self, node):
        if node.children[0].type == "~":
            return ASTMutation(node.children[0], "")


class LogicalOperatorReplacement(MutationOperator):
    
    REPLACEMENTS = {
        "&": ["|"],
        "|": ["&"],
        "^": ["&"],
        "<<": [">>"],
        ">>": ["<<"],
    }

    def mutate_binary_operator(self, node):
        operator = node.children[1]

        if operator.type in LogicalOperatorReplacement.REPLACEMENTS:
            return [ASTMutation(operator, replacement, op_type = "LOR") 
                    for replacement in LogicalOperatorReplacement.REPLACEMENTS[operator.type]]
        


# relational --------------

class RelationalOperatorReplacement(MutationOperator):
    
    REPLACEMENTS = {
        "<": [">", "<="],
        ">": ["<", ">="],
        "<=": [">=", "<"],
        ">=": ["<=", ">"],
        "==": ["!="],
        "!=": ["=="],
    }

    def mutate_comparison_operator(self, node):
        operator = node.children[1]

        if operator.type in RelationalOperatorReplacement.REPLACEMENTS:
            return [ASTMutation(operator, replacement, op_type = "LOR") 
                    for replacement in RelationalOperatorReplacement.REPLACEMENTS[operator.type]]
        
