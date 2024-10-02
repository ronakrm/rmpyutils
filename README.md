# rmpyutils
A bunch of miscellaneous python utilities. All typical pronunciations current acceptable.

## Anonymized Tracing
If you ever wanted to more freely copy and paste outputs to the internet/LLMs/etc...
```python
import rmpyutils.anon

import matplotlib.pyplot as plt
plt.figure('slkdjfs', 2)
```
Will result in:
```
Traceback (most recent call last):
  File "[ROOT]/.venv/lib/python3.12/site-packages/numpy/_core/__init__.py", line 23, in <module>
    from . import multiarray
  File "[ROOT]/.venv/lib/python3.12/site-packages/numpy/_core/multiarray.py", line 10, in <module>
    from . import overrides
  File "[ROOT]/.venv/lib/python3.12/site-packages/numpy/_core/overrides.py", line 8, in <module>
    from numpy._core._multiarray_umath import (
ImportError: [ROOT]/.venv/lib/python3.12/site-packages/numpy/_core/_multiarray_umath.cpython-312-x86_64-linux-gnu.so: cannot open shared object file: No such file or directory
...
```
I'm not sure if this was a good idea or not, especially with how insane the implementation for this is (plus tests). But here it is.
