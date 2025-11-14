from .base import MutationOperator
from ..mutation import ASTMutation

from code_ast import ASTVisitor


def init_inheritance_operator(source_ast, op):

    if op == "IHD": return HidingVariableDeletion(source_ast)
    if op == "IOD": return OverridingMethodDeletion(source_ast)
    if op == "IOP": return OverridenMethodCallingPositionChange(source_ast)
    if op == "SCD": return SuperCallingDeletion(source_ast)
    if op == "SCI": return SuperCallingInsertion(source_ast)
    
    raise ValueError(f"Unknown inheritance mutation operator {op}")


class BaseOverridenElementMutation(MutationOperator):

    def _is_class_next_parent(self, node):
        current = node.parent
        while current:
            if current.type == "class_definition": break
            if "_definition" in current.type: return False
            current = current.parent

        return True
    
    def _find_superclasses(self, node, superclasses):
        module = node.parent
        while module.type != "module":
            module = module.parent
        
        def _find_superclasses(node):
            if node.type == "class_definition":
                name = node.child_by_field_name("name")
                return name.text.decode() in superclasses
            return False
        
        return find_ast_nodes(module, _find_superclasses)

    def is_overridden(self, node, name = None):
        if not self._is_class_next_parent(node):
            return False

        if not name:
            name = node.text.decode()

        parent = node.parent
        while parent:
            if parent.type == "class_definition": break
            parent = parent.parent

        superclasses = []
        superclasses_node = parent.child_by_field_name("superclasses")
        if superclasses_node:
            if superclasses_node.type == "identifier":
                superclasses.append(superclasses_node.text.decode())
            elif superclasses_node.type == "argument_list":
                for identifier in superclasses_node.children:
                    if identifier.type == "identifier":
                        superclasses.append(identifier.text.decode())
        
        superclasses = self._find_superclasses(node, superclasses)
        
        def _is_assigment_to(node):
            if node.type == "assignment":
                left = node.child_by_field_name("left")
                if left.type == "identifier": 
                    return left.text.decode() == name
                elif left.type == "pattern_list":
                    return name in left.text.decode()

            if node.type == "function_definition":
                fn_name = node.child_by_field_name("name").text.decode()
                return fn_name == name
            
            return False

        for superclass_node in superclasses:
            for node in find_ast_nodes(superclass_node, _is_assigment_to,
                                       lambda node: node.type in ["function_definition"]):
                return True

        return False

        


class HidingVariableDeletion(BaseOverridenElementMutation):

    def mutate_assignment(self, node):

        if (node.child_by_field_name("left").type == "identifier" 
            and self.is_overridden(node.child_by_field_name("left"))):
            return ASTMutation(node, "pass", op_type = "IHD")
        
        if node.child_by_field_name("left").type == "pattern_list":
            if node.child_by_field_name("right").type != "expression_list":
                return
            return self.mutate_unpack(node)
    
    def mutate_unpack(self, node):
        targets = [n for n in node.child_by_field_name("left").children
                   if n.type == "identifier"]
        values = node.child_by_field_name("right")
        values = [v for v in values.children if v.type != ","]

        new_targets = []
        new_values = []
        for target, value in zip(targets, values):
            if not self.is_overridden(target):
                new_targets.append(target)
                new_values.append(value)

        if len(new_targets) != len(new_values): return

        if not new_targets:
            return ASTMutation(node, "pass", op_type = "IHD")
        elif len(new_targets) == 1:
            left = new_targets[0].text.decode()
            right = new_values[0].text.decode()
            return ASTMutation(node, f"{left} = {right}", op_type = "IHD")
        else:
            left  = ", ".join(t.text.decode() for t in new_targets)
            right = ", ".join(v.text.decode() for v in new_values)
            return ASTMutation(node, f"{left} = {right}", op_type = "IHD")
        

class OverridingMethodDeletion(BaseOverridenElementMutation):

    def mutate_function_definition(self, node):
        if self.is_overridden(node, node.child_by_field_name("name").text.decode()):
            return ASTMutation(node, "pass", op_type = "IOD")

         
# Super calling modifications -----------------

class BaseSuperCallingMutation(MutationOperator):

    def _is_class_next_parent(self, node):
        current = node.parent
        while current:
            if current.type == "class_definition": break
            if "_definition" in current.type: return False
            current = current.parent

        return True

    def is_super_call(self, node, stmt):
        if stmt.type != "expression_statement": return False
        stmt = stmt.children[0]
        if stmt.type != "assignment": return False
        
        value = stmt.child_by_field_name("right")
        if  value.type != "call": return False
        
        function = value.child_by_field_name("function")
        if function.type == "attribute" and function.child_by_field_name("object").type == "call":
            call = function.child_by_field_name("object")
            if call.child_by_field_name("function").text.decode() != "super":
                return False
            attribute = function.child_by_field_name("attribute")
            target = node.child_by_field_name("name").text.decode()
            return target == attribute.text.decode()

        return False

    def should_mutate(self, node):
        return self._is_class_next_parent(node)
    
    def get_super_call(self, node):
        body = node.child_by_field_name("body")

        for i, child in enumerate(body.children):
            if self.is_super_call(node, child):
                break
        else:
            return None, None
        return i, child


class OverridenMethodCallingPositionChange(BaseSuperCallingMutation):

    def should_mutate(self, node):
        return super().should_mutate(node) and len(node.child_by_field_name("body").children) > 1

    def mutate_function_definition(self, node):
        if not self.should_mutate(node): return

        index, stmt = self.get_super_call(node)
        if index is None: return

        raise NotImplementedError()


class SuperCallingDeletion(BaseSuperCallingMutation):

    def mutate_function_definition(self, node):
        if not self.should_mutate(node): return
        index, stmt = self.get_super_call(node)
        if index is None:
            return
        return ASTMutation(stmt, "pass", op_type = "SCD")
    

class SuperCallingInsertion(BaseSuperCallingMutation, BaseOverridenElementMutation):

    def should_mutate(self, node):
        return super().should_mutate(node) and self.is_overridden(node, node.child_by_field_name("name").text.decode())
    
    def _construct_super_call(self, node):
        name = node.child_by_field_name("name").text.decode()

        args = []
        for parameter in node.child_by_field_name("parameters").children:
            if parameter.type == "identifier":
                args.append(parameter.text.decode())
            if parameter.type in ["typed_default_parameter", "default_parameter"]:
                args.append(parameter.child_by_field_name("name").text.decode())
            if parameter.type in ["list_splat_pattern", "dictionary_splat_pattern"]:
                args.append(parameter.text.decode())
            
        return f"super().{name}({', '.join(args)})"

    def mutate_function_definition(self, node):
        if not self.should_mutate(node):
            return
        
        index, _ = self.get_super_call(node)
        if index is not None:
            return
        
        super_call = self._construct_super_call(node)        
        first_child = node.child_by_field_name("body").children[0]

        insertion = first_child.start_point[1]
        return ASTMutation(first_child, f"{super_call}\n{' '*insertion}{first_child.text.decode()}", op_type = "SCI")



# Helper ---------------

def find_ast_nodes(root_node, fn, stop_fn = None):

    class Finder(ASTVisitor):

        def __init__(self):
            self.nodes = []
        
        def visit(self, node):
            if fn(node): self.nodes.append(node)
            if stop_fn and stop_fn(node):
                return False
    
    finder = Finder()
    finder.walk(root_node)
    return finder.nodes