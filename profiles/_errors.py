# -*- coding: utf-8 -*-

"""
Copyright (C) 2018  Daniele Giudice
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
