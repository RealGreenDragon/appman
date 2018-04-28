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

# This import is necessary for get Base_Profile
from ._base import Base_Profile

# This import makes available all models and functions contained in '_utils.py'
from ._utils import *

'''
This is an example of a program profile.
A program profile is a model useful to intall/update/remove automatically a program.

All meta-profile classes MUST inherit 'Base_Profile'.

To implement a meta profile, you must implement the following methods of 'Base_Profile':
- _get_latest_version
- _get_download_data
- _extract_latest_version
- _install_program
- _get_executables
- _remove_program

Read the methods documentation for implmentation instructions.

The methods call order in the 'install' mode is:
- _get_latest_version
- _get_download_data
- _extract_latest_version
- _install_program
- _get_executables

The methods call order in the 'update' mode is:
- _get_latest_version
- _get_download_data
- _extract_latest_version
- _update_program

The methods call order in the 'remove' mode is:
- _remove_program
'''

class Example_Profile(Base_Profile):
    '''
    Program Name

    The value of this attribute MUST be specified
    '''

    # Type here the program name (str)
    program_name = 'Example'

    '''
    Attributes (basic profile settings)

    You would specify them in the pofiles only their values is different than default.
    '''

    # Type here the default install path (str)
    # If you work with an exernal installer, you can leave the default
    default_path = ''

    # Dependences (set of program names)
    dependences = set([])

    # Indicate here if the program is portable or not.
    # If is enabled, the program path will be deleted automatically, otherwinse no.
    # A non portable program would be uninstalled calling the uninstaller.
    is_portable = True

    # Indicate here if the program can be autoupdated or not.
    # If is enabled, the program can be updated, otherwise "self.update()" does nothing.
    # The update would be disabled if, once installed, the program update itself.
    can_update = True

    # Indicate here if the program is available only on x64 systems or not.
    # If is enabled and the system is x86, the installation will be skipped, otherwise it proceeds normally.
    x64_only = False

    '''
    Methods

    Here you can specify the install/update/remove actions implementing the methods.
    '''

    # Not touch the method signature and the first row
    def __init__(self, **prog_data):
        super(self.__class__, self).__init__(**prog_data)
        # Here you can add other inits useful for the profile

    def _get_latest_version(self):
        """
        Parse program latest version.

        Advices:
            - The logger interface is in 'self._logger'
            - Use 'self._mode' attribute ('install' or 'update')
            - Use 'self._http_*(...)' methods

        Postconditions:
            - The returned value will be available into 'self._latest_version' attribute

        Returns:
            str : Latest version
        """

        raise NotImplementedError('You must implement "_get_latest_version" method!')

    def _get_download_data(self):
        """
        Get download data for latest version of the program.
        For each file that need to be downloaded, a DownloadData(...) must be returned.
        If the download is only one, you can return directly the DownloadData,
        otherwise return a DownloadData list.

        Advices:
            - The logger interface is in 'self._logger'
            - Use 'self._mode' attribute ('install' or 'update')
            - Use 'self._latest_version' attribute
            - Use 'self._path' attribute
            - Use 'self._http_*(...)' methods
            - Use 'self.dl_*(...)' methods (shortcus to create a DownloadData object)

        Postconditions:
            - The returned value will be available into 'self._dl_data_list' attribute

        Returns:
            list: DownloadData objects list (or a single DownloadData object if the download is only one)
        """

        raise NotImplementedError('You must implement "_get_download_data" method!')

    def _extract_latest_version(self):
        """
        Extract the files downloaded (if needed).

        Advices:
            - The logger interface is in 'self._logger'
            - Use 'self._mode' attribute ('install' or 'update')
            - Use 'self._latest_version' attribute
            - Use 'self._path' attribute
            - Use 'self._dl_data_list' attribute
            - Use 'self._extract(...)' method
            - Save into attributes all data needed at the next method

        Returns:
            None
        """

        raise NotImplementedError('You must implement "_extract_latest_version" method!')

    def _update_program(self):
        """
        Perform actions needed to update the program and clean temporary files.
        This method is called when you exec the command "appman update [program_name]/all".

        Advices:
            - The logger interface is in 'self._logger'
            - Use 'self._latest_version' attribute
            - Use 'self._path' attribute
            - Use 'self._dl_data_list' attribute
            - Use OS Utility methods to work with files/folders
            - Remember to delete temporary files/folder (such as those created
                in 'self._extract_latest_version(...) method'

        Returns:
            None
        """

        raise NotImplementedError('You must implement "_update_program" method!')

    def _install_program(self):
        """
        Perform actions to install the program and clean temporary files.
        This method is called when you exec the command "appman install [program_name]".

        Advices:
            - The logger interface is in 'self._logger'
            - Use 'self._latest_version' attribute
            - Use 'self._path' attribute
            - Use 'self._dl_data_list' attribute
            - Use OS Utility methods to work with files/folders
            - Remember to delete temporary files/folder (such as those created
                in 'self._extract_latest_version(...) method

        Returns:
            None
        """

        raise NotImplementedError('You must implement "_install_program" method!')

    def _get_executables(self):
        """
        Return the list of all executable folders, so the folders that contains almost
        an executable you will want to call directly from command line.
        All paths must be absolute.

        The program path is NOT taken by default, so if it is useful you have to add it.

        Advices:
            - The logger interface is in 'self._logger'
            - Use 'self._path' attribute
            - Use 'self._list_files(...)' method

        Returns:
            list: folders absolute path list (or a single absolute path if the folder is only one)
        """

        raise NotImplementedError('You must implement "_get_executables" method!')

    def _remove_program(self):
        """
        Perform the actions to uninstall the program.
        This method is called when you exec the command "appman remove [program_name]".

        Operations automatically executed after this method (so that you don't have to do):
        - If 'is_portable' flag is enabled, the self._path folder will be removed with all its content (if it exists).
        - All links to the executables will be deleted

        Advices:
            - The logger interface is in 'self._logger'
            - Use OS Utility methods to work with files/folders'

        Returns:
            None
        """

        raise NotImplementedError('You must implement "_remove_program" method!')
