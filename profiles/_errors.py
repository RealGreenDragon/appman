
class AppManException(Exception):
    """
    Base class for exceptions thrown by AppMan.
    """
    pass

class ProgramDBException(AppManException):
    """
    Something was wrong in the ProgramDB management.
    """
    pass

class ProfileException(AppManException):
    """
    Base class for exceptions thrown by profile classes.
    """
    pass

class InvalidPathException(ProfileException):
    """
    A path given (or part of it) is invalid.
    """
    pass

class HTTPRequestException(ProfileException):
    """
    Something was wrong in an HTTP request.
    """
    pass

class ExtractException(ProfileException):
    """
    Something was wrong in the extraction.
    """
    pass

class ImplementationError(ProfileException):
    """
    Something was wrong in the specific methods implementation.
    """
    pass
