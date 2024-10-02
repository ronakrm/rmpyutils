import pytest
import os
import sys
import subprocess
import traceback
from io import StringIO
from rmpyutils import anon

@pytest.fixture
def setup_test_environment(tmpdir):
    root_dir = str(tmpdir.mkdir("project"))
    sub_dir = str(tmpdir.mkdir("project/subdir"))
    test_file = str(tmpdir.join("project/subdir/test_file.py"))
    with open(test_file, 'w') as f:
        f.write("print('test')")

    anon.configure_anonymization(root_dir)

    yield root_dir, sub_dir, test_file

    anon.reset_anonymization()

def test_anonymize_path(setup_test_environment):
    root_dir, sub_dir, test_file = setup_test_environment

    anonymized = anon.debug_anonymize(f"Path: {test_file}")

    assert root_dir not in anonymized, f"Root directory '{root_dir}' found in anonymized path"
    assert '[ROOT]/subdir/test_file.py' in anonymized, f"Expected '[ROOT]/subdir/test_file.py' not found in anonymized path"

    # Test with quoted path
    quoted_anonymized = anon.debug_anonymize(f'Quoted path: "{test_file}"')

    assert root_dir not in quoted_anonymized, f"Root directory '{root_dir}' found in anonymized quoted path"
    assert '[ROOT]/subdir/test_file.py' in quoted_anonymized, f"Expected '[ROOT]/subdir/test_file.py' not found in anonymized quoted path"

def test_anonymize_stderr(setup_test_environment, capsys):
    root_dir, sub_dir, test_file = setup_test_environment

    anonymized_stderr = anon.get_anonymized_stderr()
    original_stderr = sys.stderr
    sys.stderr = anonymized_stderr

    try:
        print(f"Error in '{test_file}'", file=sys.stderr)
        sys.stderr.flush()  # Ensure all content is written

        stderr_output = anonymized_stderr.getvalue()

        assert root_dir not in stderr_output, f"Root directory '{root_dir}' found in stderr"
        assert '[ROOT]' in stderr_output, "'[ROOT]' not found in stderr"
        assert 'test_file.py' in stderr_output, "'test_file.py' not found in stderr"
    finally:
        sys.stderr = original_stderr

def test_anonymize_traceback(setup_test_environment):
    root_dir, sub_dir, test_file = setup_test_environment

    # Use the directory of the test file as the root directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    anon.configure_anonymization(test_dir)

    try:
        raise Exception("Test exception with /some/path/to/file.py")
    except Exception:
        tb = traceback.format_exc()

    assert test_dir not in tb, f"Test directory '{test_dir}' found in traceback"
    assert '[ROOT]' in tb, "'[ROOT]' not found in traceback"

    # Check that [EXTERNAL] is not used for the test file path
    assert 'File "[ROOT]' in tb, "'File \"[ROOT]' not found in traceback"

    # Check that the path in the exception message is anonymized
    assert '[EXTERNAL]/file.py' in tb, "'[EXTERNAL]/file.py' not found in traceback"

    assert "Test exception" in tb, "'Test exception' not found in traceback"

def test_uncaught_exception_anonymization(setup_test_environment, capsys):
    root_dir, sub_dir, test_file = setup_test_environment

    # Use the directory of the test file as the root directory
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Ensure we're using the correct root directory
    anon.configure_anonymization(test_dir)

    # Create a test file within the test directory
    test_script = os.path.join(test_dir, "test_script.py")
    with open(test_script, "w") as f:
        f.write("raise Exception('Test uncaught exception')")

    # Get the AnonymizedStderr
    anonymized_stderr = anon.get_anonymized_stderr()

    # Simulate an uncaught exception
    try:
        exec(open(test_script).read(), {'__file__': test_script})
    except Exception:
        sys.excepthook(*sys.exc_info())

    anonymized_traceback = anonymized_stderr.getvalue()


    assert test_dir not in anonymized_traceback, f"Test directory '{test_dir}' found in traceback"
    assert '[ROOT]' in anonymized_traceback, "'[ROOT]' not found in traceback"
    assert '[EXTERNAL]' in anonymized_traceback, "'[EXTERNAL]' not found in traceback"
    assert "Test uncaught exception" in anonymized_traceback, "'Test uncaught exception' not found in traceback"

    # Clean up the test script
    os.remove(test_script)

def test_integration_with_real_exception():
    # Create a temporary script
    test_script = "test_integration_script.py"
    with open(test_script, "w") as f:
        f.write("""
from rmpyutils import anon
from matplotlib.pyplot import plt

# Simulate an import error
plt.figure('aslkd', 2)
""")

    try:
        # Set up the environment for the subprocess
        env = os.environ.copy()
        env['ANONYMIZATION_ROOT_DIR'] = os.getcwd()

        # Run the script and capture the output
        result = subprocess.run([sys.executable, test_script],
                                capture_output=True, text=True, check=False,
                                env=env)
        output = result.stderr

        # Check that the actual paths are anonymized
        assert '/home/' not in output, "Unanonymized path found in output"
        assert '[ROOT]' in output or '[EXTERNAL]' in output, "No anonymized paths found in output"
        assert 'ImportError' in output, "Expected ImportError not found in output"

    finally:
        # Clean up the temporary script
        if os.path.exists(test_script):
            os.remove(test_script)

