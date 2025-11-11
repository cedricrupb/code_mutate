from code_ast import ASTVisitor

class MutationOperator(ASTVisitor):

    def __init__(self, ast):
        super().__init__()
        self.ast = ast
        self.mutations = []

    def mutate(self, node):
        return None

    def on_visit(self, node):
        if super().on_visit(node):
            mutations = self.on_mutate(node)
            if mutations:
                try:
                    self.mutations.extend(mutations)
                except TypeError:
                    self.mutations.append(mutations)
            return True
        return False
    
    def on_mutate(self, node):
        mutate_fn = getattr(self, "mutate_%s" % node.type, self.mutate)
        return mutate_fn(node)
    

class CallableMutationOperator(MutationOperator):

    def __init__(self, ast, callable):
        super().__init__(ast)
        self.callable = callable

    def mutate(self, node):
        return self.callable(node)