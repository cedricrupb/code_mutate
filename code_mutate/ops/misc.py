from .base import MutationOperator
from ..mutation import ASTMutation


def init_misc_operator(source_ast, op):

    if op == "ASR": return AssignmentOperatorReplacement(source_ast)
    if op == "BCR": return BreakContinueReplacement(source_ast)
    if op == "CRP": return ConstantReplacement(source_ast)
    if op == "SIR": return SliceIndexRemove(source_ast)

    raise ValueError(f"Unknown misc mutation operator {op}")


class AssignmentOperatorReplacement(MutationOperator):

    REPLACEMENTS = {
        "+=": ["-="],
        "-=": ["+="],
        "*=": ["/=", "//=", "**="],
        "/=": ["*=", "//="],
        "//=": ["/=", "*="],
        "%=": ["*="],
    }

    def mutate_augmented_assignment(self, node):
        operator = node.children[1]

        if operator.type in AssignmentOperatorReplacement.REPLACEMENTS:
            return [ASTMutation(operator, replacement, op_type = "ASR") 
                    for replacement in AssignmentOperatorReplacement.REPLACEMENTS[operator.type]]


class BreakContinueReplacement(MutationOperator):
    
    def mutate_break_statement(self, node):
        return ASTMutation(node, "continue", op_type = "BCR")
    
    def mutate_continue_statement(self, node):
        return ASTMutation(node, "break", op_type = "BCR")



def is_docstring(node):
    if node.parent.type != "expression_statement": return False

    node = node.parent
    parent = node.parent
    if parent.type != "block" or parent.children[0] != node: return False

    grandparent = parent.parent
    return grandparent.type == "function_definition"


class ConstantReplacement(MutationOperator):
    
    def mutate_integer(self, node):
        try:
            number = int(self.ast.match(node))
            return ASTMutation(node, str(number + 1), op_type = "CRP")
        except ValueError:
            return
    
    def mutate_float(self, node):
        try:
            number = float(self.ast.match(node))
            return ASTMutation(node, str(number + 1), op_type = "CRP")
        except ValueError:
            return
    
    def mutate_string(self, node):
        if is_docstring(node): return

        text = self.ast.match(node)
        if text != "code_mutate":
            rep =  "'code_mutate'"
        else:
            rep = "'python'"
        
        return [ASTMutation(node, "", op_type = "CRP"), 
                ASTMutation(node, rep, op_type = "CRP") ]
    

# Slicing -----------------

class SliceIndexRemove(MutationOperator):
    
    def mutate_slice(self, node):
        lower, upper, step = "", "", ""
        
        state = 0
        for child in node.children:
            if child.type == ":": state += 1; continue
            if state == 0: 
                lower = self.ast.match(child)
            elif state == 1:
                upper = self.ast.match(child)
            else:
                step = self.ast.match(child)

        output = []

        if upper:
            if step:
                target = f"{lower}::{step}"
            else:
                target = f"{lower}:"
            output.append(ASTMutation(node, target, op_type = "SIR"))
        
        if lower:
            if step:
                target = f":{upper}:{step}"
            else:
                target = f":{upper}"

            output.append(ASTMutation(node, target, op_type = "SIR"))
        
        if step:
            target = f"{lower}:{upper}"
            output.append(ASTMutation(node, target, op_type = "SIR"))

        return output
        