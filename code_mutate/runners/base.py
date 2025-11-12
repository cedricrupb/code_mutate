import sys
from typing import Tuple

import importlib
from importlib.abc import Loader, MetaPathFinder

from contextlib import contextmanager

from ..mutation import Mutation


class TestResult:
    pass


class BaseTestRunner:

    def run_tests_with_mutant(self, module_name : str, mutation : Mutation, timeout : int = -1) -> TestResult:
        with mutate_imports(module_name, mutation):
            return self.run_tests(module_name, timeout = timeout)
        
    def run_tests(self, target_name : str, timeout : int = -1) -> TestResult:
        raise NotImplementedError()


# Mutation loader -------------------------------------

class MutationLoader(Loader):

    def __init__(self, module_name : str, origin: str, mutation : Mutation):
        self.module_name = module_name
        self.origin = origin
        self.mutation = mutation

    def create_module(self, spec):
        return None
    
    def exec_module(self, module):
        origin = self.origin
        with open(origin, "r") as f:
            source_code = f.read()

        target_source_code, _ = self.mutation.apply(source_code)
        target_code_obj = compile(target_source_code, origin, "exec")
        exec(target_code_obj, module.__dict__)


class MutationEntryFinder(MetaPathFinder):

    def __init__(self, module_prefix : str, mutation : Mutation):
        self.module_prefix = module_prefix
        self.mutation = mutation

    def find_spec(self, fullname, path, target = None):
        if not self.module_prefix or not fullname.startswith(self.module_prefix):
            return None
        
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if not spec or not spec.origin or spec.origin == "builtin":
            return None
        
        if spec.loader and isinstance(spec.loader, importlib.machinery.SourceFileLoader):
            spec.loader = MutationLoader(
                fullname, spec.origin, self.mutation
            )
            return spec
        
        return None
    

@contextmanager
def mutate_imports(module_name, mutation):
    finder = MutationEntryFinder(module_name, mutation)

    # Evict all already loaded modules to force reload
    to_evict = [name for name in list(sys.modules)
                if name.startswith(module_name)]
    for name in to_evict:
        del sys.modules[name]

    # Inject custom mutation loader
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        try:
            sys.meta_path.remove(finder)
        except ValueError:
            pass
            
        for name in list(sys.modules):
            if name.startswith(module_name):
                del sys.modules[name]