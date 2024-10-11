import sys
from importlib import import_module


def auto_import():
    try:
        import_module("rmpyutils.loganon")
        print("rmpyutils.loganon has been auto-imported.")
    except ImportError:
        print("Warning: Failed to auto-import rmpyutils.loganon")


auto_import()
