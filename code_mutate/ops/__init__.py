
from .base import CallableMutationOperator, MutationOperator
from .arithmetic import init_arithmetic_operator
from .decorator import init_decorator_operator
from .exception import init_exception_operator
from .inheritance import init_inheritance_operator
from .logical import init_logical_operator
from .misc import init_misc_operator


def init_mutation_operator(source_ast, op):
    if isinstance(op, MutationOperator): return op

    for initializer in [_init_callable_mutator, 
                        init_arithmetic_operator,
                        init_decorator_operator,
                        init_exception_operator,
                        init_inheritance_operator,
                        init_logical_operator,
                        init_misc_operator]:
        try:
            mutator = initializer(source_ast, op)
            if mutator: return mutator
        except ValueError:
            continue
    
    raise ValueError(f"Unknown mutation operator {op}")


def _init_callable_mutator(source_ast, op):
    if callable(op): return CallableMutationOperator(source_ast, op)
    raise ValueError("Mutation operator is not callable")

