import code_ast as ca
from code_ast.visitor import ResumingVisitorComposition

from itertools import chain

from .ops import init_mutation_operator

STANDARD_OPERATORS = {
    "python": [
        "AOD", 
        "AOR", 
        "ASR", 
        "BCR", 
        "COD", 
        "COI", 
        "CRP", 
        "DDL",
       # "EHD", 
       # "EXS", 
       # "IHD", 
       # "IOD", 
       # "IOP", 
        "LCR", 
        "LOD", 
        "LOR",
        "ROR", 
       # "SCD", 
       # "SCI", 
        "SIR",
    ]
}

def mutate(source_code_or_ast, ops = None, lang = "guess", **kwargs):
    
    if isinstance(source_code_or_ast, str):
        source_ast = ca.ast(source_code_or_ast, lang = lang, **kwargs)
    else:
        source_ast = source_code_or_ast

    assert lang in STANDARD_OPERATORS, f"{lang} is currently not supported for mutation"
    if ops is None: ops = STANDARD_OPERATORS[lang]

    mutation_visitor = ResumingVisitorComposition(
        *[init_mutation_operator(source_ast, op) for op in ops]
    )
    source_ast.visit(mutation_visitor)

    return chain.from_iterable(v.mutations for v in mutation_visitor.visitors)
    

