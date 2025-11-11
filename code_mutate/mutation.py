from typing import Tuple
from difflib import unified_diff

class Mutation:

    def __init__(self, source_pos : Tuple[int, int, int, int], target_text: str, op_type = None, scope = None):
        self.source_pos  = source_pos
        self.target_text = target_text
        self.op_type = op_type
        self.scope = scope

        assert self.source_pos[0] <= self.source_pos[2], "Start line needs to smaller equal to target line"
        assert self.source_pos[0] != self.source_pos[2] or self.source_pos[1] < self.source_pos[3]

    def apply(self, source_code):
        source_lines = source_code.splitlines(True)
        start_line, start_pos, end_line, end_pos = self.source_pos

        source_area = source_lines[start_line : end_line + 1]
        
        if start_line == end_line:
            target_text = source_area[0][start_pos : end_pos]
        else:
            target_text = "".join(
                [source_area[0][start_pos:]] + source_area[1:-1] + [source_area[-1][:end_pos]]
            )
        
        target_lines = (source_lines[:start_line] + 
                        [
                            source_area[0][:start_pos] 
                            + self.target_text 
                            + source_area[-1][end_pos:]
                        ]
                        + source_lines[end_line+1:])

        return "".join(target_lines), Mutation(self.source_pos, target_text)

    def unified_diff(self, source_code, fromfile = '', tofile = '', n = 3, lineterm = "\n"):
        target_code, _ = self.apply(source_code)
        return "".join(unified_diff(source_code.splitlines(True), 
                                 target_code.splitlines(True),
                                 fromfile = fromfile,
                                 tofile = tofile,
                                 n=n, 
                                 lineterm=lineterm))

    def __repr__(self):
        start_line, start_pos, end_line, end_pos = self.source_pos
        scope = f"@{self.scope}" if scope else ""
        return f"{self.op_type or 'MUT'}{scope}({start_line}:{start_pos} - {end_line}:{end_pos}) -> {self.target_text}"
    

class ASTMutation(Mutation):

    def __init__(self, source_node, target_text, **kwargs):
        self.source_node = source_node
        position = source_node.start_point + source_node.end_point

        super().__init__(
            position, target_text, 
            scope = _identify_scope(source_node), **kwargs
        )


# Identify scope ---------------------------

def _identify_scope(source_node):
    scopes = []

    current = source_node
    while current.parent != current:
        if current.type == "function_definition":
            scopes.append(_function_name(current))
        elif current.type == "class_definition":
            scopes.append(_class_name(current))
        current = current.parent

    return ".".join(scopes[::-1])

def _function_name(function_node):
    return function_node.child_by_field_name("name").text.decode()

def _class_name(class_node):
    return class_node.child_by_field_name("name").text.decode()


# Helper -------------------------------------

def match_span(source_tree, source_lines):
    """
    Greps the source text represented by the given source tree from the original code

    Parameters
    ----------
    source_tree : tree-sitter node object
        Root of the AST which should be used to match the code
    
    source_lines : list[str]
        Source code as a list of source lines

    Returns
    -------
    str
        the source code that is represented by the given source tree
    
    """
    
    start_line, start_char = source_tree.start_point
    end_line,   end_char   = source_tree.end_point

    assert start_line <= end_line
    assert start_line != end_line or start_char <= end_char

    source_area     = source_lines[start_line:end_line + 1]
    
    if start_line == end_line:
        return source_area[0][start_char:end_char]
    else:
        source_area[0]  = source_area[0][start_char:]
        source_area[-1] = source_area[-1][:end_char]
        return "\n".join(source_area)