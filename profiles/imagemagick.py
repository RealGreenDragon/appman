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

from ._base import Base_Profile
from ._utils import *

class ImageMagick_Manager(Base_Profile):

    program_name = 'ImageMagick'

    default_path = 'C:\\Portable\\imagemagick\\'

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

        dl_page = self._http_get_req('https://www.imagemagick.org/script/download.php')
        last_ver = dl_page.split('-portable-Q16-x86.zip')[0].split('ImageMagick-')[-1].strip()
        self.dl_url = 'https://www.imagemagick.org/download/binaries/ImageMagick-{}-portable-Q16-x{}.zip' \
        .format(last_ver, '86' if self._arch == '32' else '64')
        return last_ver

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

        Postconditions:
            - The returned value will be available into 'self._dl_data_list' attribute

        Returns:
            list: DownloadData objects list (or a single DownloadData object if the download is only one)
        """

        return dl_get(
                os.path.join(self._tmp_dir, 'imagemagick_latest.zip'),
                self.dl_url
            )

    def _extract_latest_version(self):
        """
        If needed, extract the file downloaded

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

        self._extract(self._dl_data_list[0].path)

        # Remove the downloaded file
        self._delete_file(self._dl_data_list[0].path)

    def _update_program(self):
        """
        Perform actions to update the program and clean temporary files.
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

        pass

    def _install_program(self):
        """
        Perform actions to install the program and clean temporary files.
        This method is called when you exec the command "appman install [program_name]".

        Advices:
            - The logger interface is in 'self._logger'
            - Simply call "self._update_program()" if the operations are the same
            - Use 'self._latest_version' attribute
            - Use 'self._path' attribute
            - Use 'self._dl_data_list' attribute
            - Use OS Utility methods to work with files/folders
            - Remember to delete temporary files/folder (such as those created
                in 'self._extract_latest_version(...) method

        Returns:
            None
        """

        self._update_program()

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

        return self._path

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

        pass
