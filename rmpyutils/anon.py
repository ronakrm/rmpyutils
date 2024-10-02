import os
import sys
import traceback
import re
from functools import wraps
from io import StringIO
from importlib.abc import MetaPathFinder, Loader
from importlib.util import spec_from_loader

class PathAnonymizer:
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        # print(f"PathAnonymizer initialized with root_dir: {self.root_dir}")

    def anonymize_path(self, path):
        if '[ROOT]' in path or '[EXTERNAL]' in path:
            return path
        try:
            abs_path = os.path.abspath(path)
            if abs_path.startswith(self.root_dir):
                rel_path = os.path.relpath(abs_path, self.root_dir)
                return f'[ROOT]/{rel_path}'
            else:
                return f'[EXTERNAL]/{os.path.basename(abs_path)}'
        except Exception as e:
            print(f"Error in anonymize_path: {str(e)}")
            return path

    def anonymize_text(self, text):
        def replace_path(match):
            path = match.group(1) or match.group(0)
            anonymized = self.anonymize_path(path)
            return f'"{anonymized}"' if match.group(1) else anonymized

        pattern = r'"([^"]+)"|(?<=[\'"\s:])(/(?:[^\s\'"]+/)*[^\s\'"]+)'
        anonymized = re.sub(pattern, replace_path, text)
        
        anonymized = anonymized.replace('"<string>"', '"[EXTERNAL]/<string>"')
        anonymized = anonymized.replace('<string>', '[EXTERNAL]/<string>')
        return anonymized

class AnonymizedStderr:
    def __init__(self, real_stderr, anonymizer):
        self.real_stderr = real_stderr
        self.anonymizer = anonymizer
        self.buffer = StringIO()

    def write(self, s):
        anonymized = self.anonymizer.anonymize_text(s) if self.anonymizer else s
        self.real_stderr.write(anonymized)
        self.buffer.write(anonymized)

    def flush(self):
        self.real_stderr.flush()
        self.buffer.flush()

    def getvalue(self):
        return self.buffer.getvalue()

    def __getattr__(self, attr):
        return getattr(self.real_stderr, attr)

_anonymizer = None
_original_stderr = sys.stderr
_anonymized_stderr = None

def patch_traceback_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str):
            return _anonymizer.anonymize_text(result) if _anonymizer else result
        elif isinstance(result, list):
            return [_anonymizer.anonymize_text(line) if isinstance(line, str) and _anonymizer else line for line in result]
        return result
    return wrapper

def custom_excepthook(exc_type, exc_value, exc_traceback):
    global _anonymized_stderr
    if _anonymizer and _anonymized_stderr:
        # print("Custom excepthook called")
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        anonymized_tb = [_anonymizer.anonymize_text(line) for line in tb_lines]
        anonymized_output = ''.join(anonymized_tb)
        _anonymized_stderr.write(anonymized_output)
        _anonymized_stderr.flush()
    else:
        print("Custom excepthook called, but _anonymizer or _anonymized_stderr is None")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

class AnonymizingFinder(MetaPathFinder):
    def __init__(self, original_pathfinder):
        self.original_pathfinder = original_pathfinder

    def find_spec(self, fullname, path, target=None):
        spec = self.original_pathfinder.find_spec(fullname, path, target)
        if spec and spec.origin:
            spec.origin = _anonymizer.anonymize_path(spec.origin) if _anonymizer else spec.origin
        return spec

def patch_import_system():
    for i, finder in enumerate(sys.meta_path):
        if hasattr(finder, 'find_spec'):
            sys.meta_path[i] = AnonymizingFinder(finder)

def setup_anonymization(root_dir=None):
    global _anonymizer, _anonymized_stderr
    if root_dir is None:
        root_dir = os.environ.get('ANONYMIZATION_ROOT_DIR', os.getcwd())
    root_dir = os.path.abspath(root_dir)
    # print(f"Setting up anonymization with root_dir: {root_dir}")
    _anonymizer = PathAnonymizer(root_dir)
    _anonymized_stderr = AnonymizedStderr(sys.stderr, _anonymizer)
    sys.stderr = _anonymized_stderr
    sys.excepthook = custom_excepthook

    traceback.print_exception = patch_traceback_function(traceback.print_exception)
    traceback.format_exception = patch_traceback_function(traceback.format_exception)
    traceback.format_exc = patch_traceback_function(traceback.format_exc)

    patch_import_system()

    os.environ['ANONYMIZATION_ROOT_DIR'] = root_dir

    # print(f"Path anonymization set up for root directory: {root_dir}")

def configure_anonymization(root_dir=None):
    global _anonymizer
    if root_dir is None:
        root_dir = os.environ.get('ANONYMIZATION_ROOT_DIR', os.getcwd())
    root_dir = os.path.abspath(root_dir)
    if _anonymizer is not None and _anonymizer.root_dir == root_dir:
        return
    reset_anonymization()
    setup_anonymization(root_dir)

def reset_anonymization():
    global _anonymizer, _anonymized_stderr
    _anonymizer = None
    sys.stderr = _original_stderr
    _anonymized_stderr = None
    sys.excepthook = sys.__excepthook__

def get_anonymized_stderr():
    global _anonymized_stderr
    if _anonymized_stderr is None:
        setup_anonymization()
    return _anonymized_stderr

def debug_anonymize(text):
    if _anonymizer:
        return _anonymizer.anonymize_text(text)
    else:
        print("Warning: Anonymizer not initialized. Returning original text.")
        return text

def get_root_dir():
    global _anonymizer
    return _anonymizer.root_dir if _anonymizer else None

# Set up anonymization as early as possible
setup_anonymization()
