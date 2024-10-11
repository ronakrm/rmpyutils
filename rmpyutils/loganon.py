import os
import sys
from typing import Optional


class PathAnonymizingInterceptor:
    def __init__(self, original_stream, root_path: str):
        self.original_stream = original_stream
        self.root_path = os.path.normpath(root_path)

    def write(self, string):
        anonymized = self.anonymize_paths(string)
        self.original_stream.write(anonymized)

    def flush(self):
        self.original_stream.flush()

    def anonymize_paths(self, string):
        string = string.replace(self.root_path, "[ANONYMIZED]")
        string = string.replace(sys.prefix, "[ANONYMIZED]")
        return string

    def __getattr__(self, attr):
        return getattr(self.original_stream, attr)


class PathAnonymizingLogger:
    _instance = None
    _original_stdout = sys.stdout
    _original_stderr = sys.stderr

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PathAnonymizingLogger, cls).__new__(cls)
            cls._instance.root_path = os.getcwd()
            cls._instance.start()
        return cls._instance

    def start(self):
        sys.stdout = PathAnonymizingInterceptor(self._original_stdout, self.root_path)
        sys.stderr = PathAnonymizingInterceptor(self._original_stderr, self.root_path)

    @classmethod
    def stop(cls):
        sys.stdout = cls._original_stdout
        sys.stderr = cls._original_stderr
        cls._instance = None


def anonymize_paths(string: str, root_path: Optional[str] = None) -> str:
    root = root_path or os.getcwd()
    return string.replace(root, "[ANONYMIZED]")


def stop_interceptor():
    PathAnonymizingLogger.stop()


# Initialize the logger
_logger_instance = PathAnonymizingLogger()


# Ensure the logger is initialized when the module is imported
def __getattr__(name):
    global _logger_instance
    if name == "_logger_instance":
        if _logger_instance is None:
            _logger_instance = PathAnonymizingLogger()
        return _logger_instance
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
