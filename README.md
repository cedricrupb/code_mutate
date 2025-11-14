# Code Mutate
> Fast mutation of Python programs

code.mutate is a mutation tool for Python that tries to replicate mutation operators of [MutPy](https://github.com/mutpy/mutpy). MutPy is a popular mutation testing tool that is sadly not longer maintained. The goal of the package is to port the main functionalities of MutPy, while integrating advances of modern mutation testing tools.

> [!NOTE]
> This project is in a very early state. APIs and functionalities might change drastically.

## Installation
The package is tested under Python 3.10. It can be installed via:
```bash
git clone git@github.com:cedricrupb/code_mutate.git
pip install -e code_mutate
```

## Example
Assume we are in folder with the main code (`calculator.py`) we will mutate:
```python
def mul(x, y):
    return x * y
```

Test (`test_calculation.py`) to check its quality (**WIP - Test runner are not supported right now**):
```python
from unittest import TestCase
from calculator import mul

class CalculatorTest(TestCase):

    def test_mul(self):
        self.assertEqual(mul(2, 2), 4)
```

Now we can run code.mutate in the same directory where we have the source files:
```bash
cmutate -t calculator
```
This command will produce the following output:
```
[#0] Mutation
- [AOR] calculator.mul
-----------------------------------------------
--- calculator.py
+++ calculator.py
@@ -1,2 +1,2 @@
 def mul(x, y):
-    return x * y
+    return x / y
-----------------------------------------------

[#1] Mutation
- [AOR] calculator.mul
-----------------------------------------------
--- calculator.py
+++ calculator.py
@@ -1,2 +1,2 @@
 def mul(x, y):
-    return x * y
+    return x // y
-----------------------------------------------

[#2] Mutation
- [AOR] calculator.mul
-----------------------------------------------
--- calculator.py
+++ calculator.py
@@ -1,2 +1,2 @@
 def mul(x, y):
-    return x * y
+    return x ** y
-----------------------------------------------
```
code.mutate supports a few parameters. The most important are:
- `-t` - the target module or file to mutate
- `--scope` - a filter to filter out mutation below module level, e.g. `--scope calculator.mul` to only mutate the mul function.

Both `-t` and `--scope` allow wildcards. For example, use `calculator.*` to match all high-level functions and classes in `calculator`. Use `calculator.**.mul` to match any `mul` function that is in the `calculator` module. 

## Supported operations from MutPy
List of supported MutPy mutation operators sorted by alphabetical order:

- AOD - arithmetic operator deletion
- AOR - arithmetic operator replacement
- ASR - assignment operator replacement
- BCR - break continue replacement
- COD - conditional operator deletion
- COI - conditional operator insertion
- CRP - constant replacement
- DDL - decorator deletion
- EHD - exception handler deletion
- EXS - exception swallowing
- IHD - hiding variable deletion
- IOD - overriding method deletion
- ~~IOP - overridden method calling position change~~
- LCR - logical connector replacement
- LOD - logical operator deletion
- LOR - logical operator replacement
- ROR - relational operator replacement
- SCD - super calling deletion
- SCI - super calling insert
- SIR - slice index remove

## Project Info
The goal of this project is to port MutPy for mutation testing of Python code. This is currently developed as a helper library for internal research projects. Therefore, it will only be updated
as needed.

Feel free to open an issue if anything unexpected
happens. 

Distributed under the MIT license. See ``LICENSE`` for more information.