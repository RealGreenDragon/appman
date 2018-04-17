from ._base import Base_Profile
from ._utils import *

class WebdriverFirefox_Manager(Base_Profile):

    program_name = 'Webdriver-Firefox'

    default_path = 'C:\\Portable\\webdrivers\\firefox\\'

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

        with self._http_head_req('https://github.com/mozilla/geckodriver/releases/latest') as r:
            return r.headers['Location'].split('/v')[-1].strip()

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

        url = 'https://github.com/mozilla/geckodriver/releases/download/v{ver}/geckodriver-v{ver}-win{arc}.zip' \
        .format(ver=self._latest_version, arc=self._arch)
        return dl_get(
                os.path.join(self._tmp_dir, 'webdriver_firefox_latest.zip'),
                url
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

        self._extract(self._dl_data_list[0].path, self._path)

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

        # Remove the downloaded file
        self._delete_file(self._dl_data_list[0].path)

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
