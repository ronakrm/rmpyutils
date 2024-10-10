import pytest
import sys
import os
import io
from unittest.mock import patch, mock_open
import importlib


# Add the parent directory to sys.path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def reset_environment():
    # Store original state
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    original_modules = set(sys.modules.keys())

    # Yield control to the test
    yield

    # Reset stdout and stderr
    sys.stdout = original_stdout
    sys.stderr = original_stderr

    # Remove any newly added modules
    for module in set(sys.modules.keys()) - original_modules:
        if module.startswith('rmpyutils'):
            del sys.modules[module]

    # If rmpyutils.psl was imported, stop the interceptor
    if 'rmpyutils.loganon' in sys.modules:
        import rmpyutils.loganon
        rmpyutils.loganon.stop_interceptor()

    # Force reload of rmpyutils.psl if it exists
    if 'rmpyutils.loganon' in sys.modules:
        importlib.reload(sys.modules['rmpyutils.loganon'])

@pytest.fixture
def root_path():
    return '/test/root/path'

@pytest.fixture
def test_string(root_path):
    return f"Log message with {root_path}/file.txt"

def test_auto_start(root_path, test_string):
    with patch('os.getcwd', return_value=root_path):
        import rmpyutils.loganon as loganon
        fake_out = io.StringIO()
        sys.stdout = loganon.PathAnonymizingInterceptor(fake_out, root_path)
        print(test_string)
        output = fake_out.getvalue()
        assert "[ANONYMIZED]/file.txt" in output, f"Expected anonymized output, got: {output}"

def test_auto_start_stderr(root_path, test_string):
    with patch('os.getcwd', return_value=root_path):
        import rmpyutils.loganon as loganon
        fake_err = io.StringIO()
        sys.stderr = loganon.PathAnonymizingInterceptor(fake_err, root_path)
        print(test_string, file=sys.stderr)
        output = fake_err.getvalue()
        assert "[ANONYMIZED]/file.txt" in output, f"Expected anonymized output, got: {output}"

def test_multiple_imports_single_instance():
    with patch('os.getcwd', return_value='/default/root'):
        import rmpyutils.loganon as l1
        first_instance = l1._logger_instance

        import rmpyutils.loganon as l2
        import rmpyutils.loganon as l3

        assert l1._logger_instance is first_instance
        assert l2._logger_instance is first_instance
        assert l3._logger_instance is first_instance

def test_stop_interceptor_idempotent():
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    import rmpyutils.loganon as loganon
    assert isinstance(sys.stdout, loganon.PathAnonymizingInterceptor)
    assert isinstance(sys.stderr, loganon.PathAnonymizingInterceptor)

    loganon.stop_interceptor()
    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr

    loganon.stop_interceptor()  # Should not raise any errors
    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr

def test_anonymized_paths(root_path, test_string):
    import rmpyutils.loganon as loganon
    anonymized = loganon.anonymize_paths(test_string, root_path)
    assert anonymized == "Log message with [ANONYMIZED]/file.txt"

def test_stop_interceptor(root_path, test_string):
    import rmpyutils.loganon as loganon
    loganon.stop_interceptor()
    with patch('sys.stdout', new=io.StringIO()) as fake_out:
        print(test_string)
        assert root_path in fake_out.getvalue()

def test_loganon_paths_default_root(root_path, test_string):
    import rmpyutils.loganon as loganon
    with patch('os.getcwd', return_value=root_path):
        anonymized = loganon.anonymize_paths(test_string)
        assert anonymized == "Log message with [ANONYMIZED]/file.txt"

