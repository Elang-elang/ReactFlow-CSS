class GenerateIconErrors(Exception):
    """Base exception class for icon generation errors"""
    def __init__(self, message: str = "Generate error occurred"):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return self.message


class ModuleNotFound(GenerateIconErrors, ImportError):
    """Exception for modules that are not found."""
    def __init__(self, module: str):
        self.module = module
        message = f"ModuleNotFound: {module}"
        super().__init__(message)


class ProcessError(GenerateIconErrors, RuntimeError):
    """Exception for errors during process execution."""
    def __init__(self, message: str):
        self.process_message = message
        super().__init__(message)
    
    def __str__(self):
        return f"ProcessError: {self.message}"