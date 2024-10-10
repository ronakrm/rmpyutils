# rmpyutils
A bunch of miscellaneous python utilities. All typical pronunciations current acceptable.

## Setup/Install
Some command like this:
```
rye add git+https://github.com/ronakrm/rmpyutils.git
poetry add git+https://github.com/ronakrm/rmpyutils.git
```

# Use
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
  File "[ANONYMIZED]/tmp.py", line 10, in <module>
    plt.figure('slkdjfs', 2)
  File "[ANONYMIZED]/.venv/lib/python3.12/site-packages/matplotlib/pyplot.py", line 1027, in figure
    manager = new_figure_manager(
              ^^^^^^^^^^^^^^^^^^^
  File "[ANONYMIZED]/.venv/lib/python3.12/site-packages/matplotlib/pyplot.py", line 550, in new_figure_manager
    return _get_backend_mod().new_figure_manager(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "[ANONYMIZED]/.venv/lib/python3.12/site-packages/matplotlib/backend_bases.py", line 3506, in new_figure_manager
    fig = fig_cls(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "[ANONYMIZED]/.venv/lib/python3.12/site-packages/matplotlib/figure.py", line 2568, in __init__
    self.bbox_inches = Bbox.from_bounds(0, 0, *figsize)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Value after * must be an iterable, not int
```
