"""
Error logic for exception types in the Bootstrap module.
"""

class BootsTrapError(Exception):
    """Base exception for all Bootstrap-related errors."""
    def __init__(self, message: str = "Bootstrap error occurred"):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return self.message

class ModuleNotFound(BootsTrapError, ImportError):
    """Exception for modules that are not found."""
    def __init__(self, module: str):
        self.module = module
        message = f"Module '{module}' not found or not available"
        super().__init__(message)
    
    def __str__(self):
        return f"ModuleNotFound: {self.message}"

class ProcessError(BootsTrapError, RuntimeError):
    """Exception for errors during process execution."""
    def __init__(self, message: str):
        self.process_message = message
        super().__init__(message)
    
    def __str__(self):
        return f"ProcessError: {self.message}"

class ConfigurationError(BootsTrapError):
    """Exception for configuration errors."""
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")

class FileNotFoundError(BootsTrapError):
    """Exception for files that are not found."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        message = f"File not found: {filepath}"
        super().__init__(message)
    
    def __str__(self):
        return f"FileNotFoundError: {self.message}"

class CompilationError(BootsTrapError):
    """Exception for CSS compilation errors."""
    def __init__(self, message: str):
        super().__init__(f"Compilation error: {message}")

class ValidationError(BootsTrapError):
    """Exception for validation errors."""
    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}")