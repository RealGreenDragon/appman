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

from ._errors import *
from ._utils import *

from html import escape as html_escape
from html import unescape as html_unescape
from urllib.parse import quote_plus as url_quote_plus
from urllib.parse import unquote_plus as url_unquote_plus
from urllib.parse import quote as url_quote
from urllib.parse import unquote as url_unquote
from urllib.parse import urlencode

from patoolib.util import PatoolError
from requests.exceptions import RequestException, Timeout

import base64
import glob
import logging
import math
import os
import re
import requests
import patoolib
import platform
import shlex
import shutil
import tempfile
import time
import traceback
import subprocess
import sys
import winsyspath

# AppMan 'bin' folder
BIN_FOLDER = os.path.join(
    os.path.abspath(os.path.join(os.path.split(__file__)[0], os.pardir)),
    'bin'
    )

BAT_LINK_FORMAT = '@echo off\n{} %*\n'

class Meta_Profile():
    """
    Base class for Meta-Programs profiles
    """

    # Meta-Program name
    meta_name = 'Generic_Meta_Profile'

    # Programs included into Meta_Profile (set of program names)
    programs = set([])

    def __repr__(self):
        return "<{} -> {}>".format(self.meta_name, self.programs)

    __str__ = __repr__

class Base_Profile():
    """
    Base class for Programs profiles
    """

    # Program name
    program_name = 'Generic_Profile'

    # Default path
    default_path = ''

    # Dependences (set of program names)
    dependences = set([])

    # Indicate here if the program is portable or not.
    # If is enabled, the "self._path" directory will be deleted automatically, otherwinse no.
    # A non portable program would be uninstalled calling the uninstaller.
    is_portable = True

    # Indicate here if the program can be autoupdated or not.
    # If is enabled, the program can be updated, otherwise "self.update()" does nothing.
    # The update would be disabled if, once installed, the program update itself.
    can_update = True

    # Indicate here if the program is available only on x64 systems or not.
    # If is enabled and the system is x86, the installation will be skipped, otherwise it proceeds normally.
    x64_only = False

    def __init__(self, **kargs):
        """
        Init program profile with passed args
        """

        # Load logger
        self._logger = logging.getLogger('appman.%s' % self.program_name)
        self._debug = self._logger.getEffectiveLevel() == logging.DEBUG
        self._logger.debug('Init {} with params {}'.format(self.__class__.__name__, kargs))

        # Choose 'innounp' command
        if self._debug:
            self._inno_extract_cmd = 'innounp -x {file_path} -d{dir_path} -b -y'
        else:
            self._inno_extract_cmd = 'innounp -x {file_path} -d{dir_path} -q -b -y'

        # Init connector
        self._connector = requests.Session()
        self._connector_headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; SGP771 Build/32.2.A.0.253; wv)'
        }
        self._connector_timeout = 12

        # Insert costuum headers (if provided)
        try:
            if 'headers' in kargs:
                self._connector_headers.update(kargs['headers'])
        except (ValueError, TypeError) as ex:
            raise ImplementationError('{}: Invalid {} provided'.format(self.program_name, 'headers'))

        # Set program path
        try:
            if 'path' in kargs:
                if not is_string(kargs['path']):
                    raise ImplementationError('{}: Invalid {} provided'.format(self.program_name, 'path'))
                self._path = os.path.abspath(kargs['path'])
            else:
                self._path = self.default_path if is_string(self.default_path) else ''
        except (OSError, ValueError, TypeError) as ex:
            raise ImplementationError('{}: Invalid {} provided'.format(self.program_name, 'path'))

        # Set current version
        if 'version' in kargs:
            if not is_string(kargs['version']):
                raise ImplementationError('{}: Invalid {} provided'.format(self.program_name, 'version'))
            self._current_version = kargs['version']
        else:
            self._current_version = ''

        # Set executables
        if 'executables' in kargs:
            if not type(kargs['executables']) == list:
                raise ImplementationError('{}: Invalid {} provided'.format(self.program_name, 'executables'))
            self._executables = kargs['executables']
        else:
            self._executables = []

        # Open System Path Wrapper
        self._syspath = winsyspath.WinSysPath()

    def __repr__(self):
        return "<{} v{} at {}>".format(self.program_name, self._current_version, self._path)

    __str__ = __repr__

    def __del__(self):
        if self._connector is not None:
            self._connector.close()

    # ---------------------------------------------------------------------------
    # -------------------------- Strings Utilities-------------------------------
    # ---------------------------------------------------------------------------

    def _b64encode(self, string):
        return base64.b64encode(string)

    def _b64decode(self, string):
        return base64.b64decode(string)

    def _html_escape(self, html_string):
        return html_escape(html_string)

    def _html_unescape(self, html_string):
        return html_unescape(html_string)

    def _url_quote(self, url_string):
        return url_quote(url_string)

    def _url_unquote(self, url_string):
        return url_unquote(url_string)

    def _url_encode(self, params):
        return urlencode(params)

    # ---------------------------------------------------------------------------
    # -------------------------- OS Utilities------------------------------------
    # ---------------------------------------------------------------------------

    @property
    def _tmp_dir(self):
        """
        Get the OS temp folder path.

        Params:
            None

        Return:
            str: the OS temp folder
        """
        return tempfile.gettempdir()

    @property
    def _arch(self):
        """
        Get the bits number of the machine.

        Params:
            None

        Return:
            str: '64' if the machine supports 64 bits, '32' otherwise
        """
        return '64' if '64' in platform.machine() else '32'


    def _check_abs_path(self, path):
        """
        Check if a path is absolute or relative.

        Params:
            path (str): path to check

        Return:
            bool: True if the path is absolute, False if it is relative
        """
        return os.path.isabs(path)

    def _check_dir(self, path):
        """
        Check if a dir exists and if is writable.

        Params:
            path (str): path of the directory to check

        Return:
            bool: True if the directory exists and is writable, False otherwise
        """
        try:
            return os.path.isdir(path) and os.access(path, os.W_OK)
        except (OSError, TypeError, ValueError):
            return False

    def _check_file(self, f):
        """
        Check if a file exists.

        Params:
            path (str): path of the file to check

        Return:
            bool: True if the file exists, False otherwise
        """
        try:
            return os.path.isfile(f)
        except (OSError, TypeError, ValueError):
            return False

    def _get_cwd(self):
        """
        Get the Current Working Directory.

        Params:
            None

        Return:
            str: Absolute path of the Current Working Directory
        """
        return os.getcwd()

    def _set_cwd(self, path):
        """
        Set the Current Working Directory (only if it exists).

        Params:
            path (str): Current Working Directory

        Return:
            bool: True if the Current Working Directory is changed, False otherwise
        """
        self._logger.debug('Changing cwd to "{}" ...'.format(path))
        if not self._check_dir(path):
            return False
        os.chdir(path)
        self._logger.debug('New cwd: "{}"'.format(self._get_cwd()))
        return True

    def _list_files(self, directory, pattern='*.*', recursive=False):
        """
        List all files in a directory that match to a specified pattern.

        Params:
            directory (str) : directory where to search
            pattern (str)   : pattern to check (default "*.*" = all files in the folder)
            recursive (bool): if check also the subdirectories

        Return:
            list: files found (each paths is relative respect to 'directory' param)
        """
        return glob.glob(os.path.join(directory, pattern), recursive=recursive)

    def _make_dir(self, directory):
        """
        Create a directory if not exists.

        Params:
            directory (str): directory path to create

        Return:
            bool: True if the directory was created, False othrwise
        """
        if not os.path.isdir(directory):
            os.makedirs(directory)
            return True
        return False

    def _make_bat_link(self, link_source):
        """
        Create a bat file that call and executable (meant only for appman 'bin' folder).
        Using a "bat link" instead a symlink allow to not copy the needed files
        in executalbe folder (for example DLL files).

        Params:
            link_source (str): abs source path of the link (an executable)

        Return:
            (str, str): the "bat link" path and the bat name
        """
        filename = os.path.split(link_source)[1].rsplit('.', 1)[0] + '.bat'
        link_dest = os.path.join(BIN_FOLDER, filename)
        self._logger.debug("Creating bat link: {} <==> {}".format(link_source, link_dest))
        self._save_file(BAT_LINK_FORMAT.format(link_source), link_dest)
        return (link_dest, filename)

    def _make_symlink(self, link_source, link_dest, is_dir=False):
        """
        Create a symlink to a file/directory

        Warning:
            Works only with Python 3.2 (or newer) and on Windows Vista (or newer).

        Params:
            link_source (str)   : source path of the link
            link_dest (str)     : destination path of the link
            is_dir (bool)       : if the path is a file or a directory (default: file)

        Return:
            None
        """
        # On python 3.2 and upper 'os.symlink' works also in windows (Vista or newer)
        self._logger.debug("Creating {}: {} <==> {}".format(
            'folder symlink' if is_dir else 'file symlink',
            link_source,
            link_dest
            ))
        os.symlink(link_source, link_dest, target_is_directory=is_dir)

    def _make_shortcut(self, shortcut_path, link_source):
        """
        Create a shortcut to a file/directory

        Params:
            shortcut_path (str) : path to the shortcut file (no extension)
            link_source (str)   : path to the shortcut target (file or directory)

        Return:
            None
        """
        from win32com.client import Dispatch
        # If the shortcut already exists, delete it
        full_shortcut_path = shortcut_path + '.lnk'
        if self._check_file(full_shortcut_path):
            self._delete_file(full_shortcut_path)
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(full_shortcut_path)
        shortcut.Targetpath = link_source
        shortcut.WorkingDirectory = os.path.split(link_source)[0]
        shortcut.IconLocation = link_source
        shortcut.save()
        del shell

    def _make_desktop_shortcut(self, link_source, shortcut_name=None):
        """
        Create a shortcut to a file/directory in the desktop (if it exists, it will be overwrited)

        Params:
            link_source (str)   : path to the shortcut target (file or directory)
            shortcut_name (str) : name (no path) of the desktop shortcut (no extension)

        Return:
            None
        """
        if not (shortcut_name and is_string(shortcut_name)):
            shortcut_name = os.path.split(link_source)[1].rsplit('.', 1)[0]
        desktop_folder = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'], 'Desktop')
        self._logger.debug('Deleting "{}" desktop shortcut...'.format(shortcut_name))
        self._make_shortcut(os.path.join(desktop_folder, shortcut_name), link_source)

    def _delete_desktop_shortcut(self, shortcut_name):
        """
        Delete a shortcut in the desktop (if it exists)

        Params:
            shortcut_name (str) : name (no path) of the desktop shortcut (no extension)

        Return:
            None
        """
        desktop_folder = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'], 'Desktop')
        shortcut_path = os.path.join(desktop_folder, shortcut_name + '.lnk')
        # Try to delete the shortcut only if it exists
        self._logger.debug('Deleting "{}" desktop shortcut...'.format(shortcut_name))
        if self._check_file(shortcut_path):
            self._delete_file(shortcut_path)

    def _syspath_add(self, path):
        """
        Add a path in the System Path.

        Params:
            path (str) : directory path to add in System Path

        Returns:
            bool: True if the System Path value is modified, False otherwise

        Raises:
            EnvironmentError if the user is not an "admin" or the admin check fails
            WindowsError if an error occurred when try to edit System Path value
            ValueError if the path passed is not a string
            OSError if the path passed not exist or is not a dir
        """
        self._logger.debug('Adding "{}" in the System Path...'.format(path))
        return self._syspath.add(path)

    def _syspath_remove(self, path):
        """
        Remove a path from the System Path.

        Params:
            path (str): directory path to remove from System Path

        Returns:
            bool: True if the System Path value is modified, False otherwise

        Raises:
            EnvironmentError if the user is not an "admin" or the admin check fails
            WindowsError if an error occurred when try to edit System Path value
            ValueError if the path passed is not a string
            OSError if the path passed not exist or is not a dir
        """
        self._logger.debug('Removing "{}" from the System Path...'.format(path))
        return self._syspath.remove(path)

    def _delete_dir(self, directory):
        """
        Delete a directory with all its content.

        Params:
            directory (str): path of the directory to delete

        Return:
            None
        """
        shutil.rmtree(directory)

    def _delete_file(self, f):
        """
        Delete a file.

        Params:
            f (str): path of the file to delete

        Return:
            None
        """
        os.remove(f)

    def _copy_dir(self, dir_source, dir_dest, *ignore):
        """
        Copy a directory with all its content (ignore glob-like patterns can be specified).
        If dir_dest or a subdirectory exists, it will be overwrited.
        If a Symlink is found, the linked files/directories will be copied in 'dir_dest'.
        If a dangling symlink is found, an error will be raised.

        Params:
            dir_source (srt): path of the directory to copy
            dir_dest (str)  : path of the directory destination
            *ignore (srt)   : glob-style patterns to ignore in the copy

        Return:
            None
        """
        copytree(dir_source, dir_dest, ignore=shutil.ignore_patterns(*ignore))

    def _copy_file(self, file_source, dest):
        """
        Copy a file to another place or to a directory.
        All file metadata will be copied as well.

        Params:
            file_source (str): path of the file to copy
            dest (srt)       : path of the file/directory destination

        Return:
            None
        """
        shutil.copy2(file_source, dest)

    def _move(self, source, dest):
        """
        Move a file/directory to another place.
        The destination file/directory must not exists.

        Params:
            source (str): path of the file/directory to copy
            dest (srt)  : path of the file/directory destination

        Return:
            None
        """
        shutil.move(source, dest)

    def _rename(self, source, dest):
        """
        Rename a file/directory.
        he operation may fail if src and dst are on different filesystems.
        https://docs.python.org/3/library/os.html#os.replace

        Params:
            source (str): path of the file/directory to rename
            dest (srt)  : path of the file/directory renamed

        Return:
            None
        """
        os.replace(source, dest)

    def _load_file(self, path, binary=False, encoding='UTF-8'):
        """
        Get the content of a file

        Params:
            path (str)     : path of the file to load
            binary (bool)  : open in binary mode or not
            encoding (str) : file encoding (ignored if binary is True)

        Return:
            File content (an str if bytes is True, binary otherwise)
        """
        if binary:
            with open(path, 'rb') as f:
                return f.read()
        else:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()

    def _save_file(self, content, path, binary=False, encoding='UTF-8'):
        """
        Save data into a files

        Params:
            content (str/bytes): data that will be saved in the file (bytes if binary is True, str otherwise)
            path (str)         : path of the file to save
            binary (bool)      : open in binary mode or not
            encoding (str)     : file encoding (ignored if binary is True)

        Return:
            None
        """
        if not isinstance(content, (str, bytes)):
            raise ImplementationError('The content can be only an str o a bytes object')
        if binary and isinstance(content, str):
            raise ImplementationError('Attempt to save a binary content into a non binary file')
        if not binary and isinstance(content, bytes):
            raise ImplementationError('Attempt to save a non binary content into a binary file')

        if binary:
            with open(path, 'wb') as f:
                f.write(content)
        else:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

    def _find_file(self, pattern):
        """
        Find a file in the current directory and in the paths specified by the PATH environment variable.

        Params:
            pattern (str) : Filename pattern to find

        Returns:
            list: file paths found (paths are bytes string)
        """

        try:
            res = self._cmd_exec('where {}'.format(pattern), check=True, capture_stdout=True)
            return res.stdout.splitlines()
        except subprocess.CalledProcessError:
            return []

    def _cmd_exec(self, cmd, posix=True, capture_stdout=False, capture_stderr=False, **kwargs):
        """
        Exec a commnad line.
        If debug is enabled, stdout and stderr will be printed on stderr, else capture_* args values will be evaluated.

        Params:
            cmd (str)             : Command line to execute
            posix (bool)          : If True shlex.split() operates in POSIX mode, otherwise it uses non-POSIX mode
            capture_stdout (bool) : If True, 'stdout' will be captured and saved in CompletedProcess response, otherwise no (Default: False)
            capture_stderr (bool) : If True, 'stderr' will be captured and saved in CompletedProcess response, otherwise no (Default: False)
            **kwargs (optional)   : Other args supported by 'subprocess.run()' function (except 'stdout' and 'stderr')

        Returns:
            subprocess.CompletedProcess
        """
        if 'stdout' in kwargs or 'stderr' in kwargs:
            raise ImplementationError("_cmd_exec: 'stdout' and 'stderr' args cannot be altered")

        # Split command line
        cmd = shlex.split(cmd, posix=posix)

        # Exec command line
        if self._debug:
            self._logger.debug('Exec command line:\n{}\n\n'.format(cmd))
            res = subprocess.run(cmd, stdout=sys.stderr, **kwargs)
            print('\n', file=sys.stderr)
        else:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE if capture_stdout else subprocess.DEVNULL,
                stderr=subprocess.PIPE if capture_stderr else subprocess.DEVNULL,
                **kwargs
                )

        # Return command result
        return res

    # ---------------------------------------------------------------------------
    # -------------------------- Extraction Utilities ---------------------------
    # ---------------------------------------------------------------------------

    def _extract(self, archive_path, target_folder=None):
        """
        Extract an archive to the 'self.path' folder or to a specified folder.
        It try to use 7Zip, and if it fails then it tries with other programs in the path.

        Params:
            archive_path (str) : path of the archive to extract
            target_folder (str): path of the destination folder (Default: self._path)

        Return:
            None
        """
        try:
            patoolib.extract_archive(
                archive_path,
                verbosity=1 if self._debug else -1,
                outdir=target_folder if target_folder else self._path,
                program='7z',
                interactive=False
                )
        except (PatoolError, OSError, TypeError, ValueError) as ex:
            raise ExtractException(ex)

    def _extract_innosetup(self, setup_path, target_folder=None):
        """
        Extract an Inno Setup to the 'self.path' folder or to a specified folder.
        Require that 'innounp' is installed and available in the path.

        Params:
            setup_path (str) : path of the Inno Setup to extract
            target_folder (str): path of the destination folder (Default: self._path)

        Return:
            None
        """
        try:
            # Split path
            file_path, file_name = os.path.split(setup_path)
            # Run 'innounp'
            self._cmd_exec(
                self._inno_extract_cmd.format(
                    dir_path=target_folder if target_folder else self._path,
                    file_path=file_name
                ),
                posix=False, # Split command using non-Unix rules
                cwd=file_path # Changes cwd for the comamnd
            )
        except OSError as ex:
            raise ExtractException(ex)

    # ---------------------------------------------------------------------------
    # -------------------------- HTTP Requests Utilities-------------------------
    # ---------------------------------------------------------------------------

    def _http_last_modified(self, url, **kwargs):
        """
        Shortcut to find the last modification date of a resource by an HTTP request.
        The date is provided with this format: %Y.%m.%d-%H:%M:%S %Z
        The string is always stripped, so if the time zone (%Z) is not present, there are no spaces in it.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            str : The 'Last-Modified' response header value, or empty string if 'Last-Modified' header is not found
        """
        with self._http_head_req(url, **kwargs) as r:
            if 'Last-Modified' in r.headers:
                return parse_html_time(r.headers['Last-Modified'])
            else:
                return ''

    def _http_head_req(self, url, **kwargs):
        """
        Shortcut to perform an HEAD HTTP request.
        It is useful to see only the response headers or not follow any HTTP redirection.

        Warning:
            Remember to use the returned obj in a 'with' statement,
            or call 'close()' method when you finished.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            requests.models.Response : The response obj
        """
        return self._http_req(HTTPMethods.HEAD, url, HTTPResponse.TEXT, **kwargs)

    def _http_get_req(self, url, **kwargs):
        """
        Shortcut to perform a GET HTTP request and get a text response.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            str : The text response body
        """
        return self._http_req(HTTPMethods.GET, url, HTTPResponse.TEXT, **kwargs)

    def _http_post_req(self, url, **kwargs):
        """
        Shortcut to perform a POST HTTP request and get a text response.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            str : The text response body
        """
        return self._http_req(HTTPMethods.POST, url, HTTPResponse.TEXT, **kwargs)

    def _http_raw_get_req(self, url, **kwargs):
        """
        Shortcut to perform a GET HTTP request and get a raw response.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            bytes : The raw response body
        """
        return self._http_req(HTTPMethods.GET, url, HTTPResponse.RAW, **kwargs)

    def _http_raw_post_req(self, url, **kwargs):
        """
        Shortcut to perform a POST HTTP request and get a raw response.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            bytes : The raw response body
        """
        return self._http_req(HTTPMethods.POST, url, HTTPResponse.RAW, **kwargs)

    def _http_json_get_req(self, url, **kwargs):
        """
        Shortcut to perform a GET HTTP request and get a json response.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            dict : The json response body
        """
        return self._http_req(HTTPMethods.GET, url, HTTPResponse.JSON, **kwargs)

    def _http_json_post_req(self, url, **kwargs):
        """
        Shortcut to perform a POST HTTP request and get a json response.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            dict : The json response body
        """
        return self._http_req(HTTPMethods.POST, url, HTTPResponse.JSON, **kwargs)

    def _http_dl_req(self, method, url, **kwargs):
        """
        Shortcut to perform a GET/POST HTTP request and the response is large.
        It is useful for downloading files (direct URL only).

        Warning:
            Remember to use the returned obj in a 'with' statement,
            or call 'close()' method when you finished.

        Params:
            url (str/bytes)     : URL where retrieve the content
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            dict : The json response body
        """
        if 'stream' in kwargs and not kwargs['stream']:
            raise ImplementationError('_http_dl_req must be a stream request')

        return self._http_req(method, url, HTTPResponse.RAW, stream=True, **kwargs)

    def _http_req(self, method, url, ret_type, **kwargs):
        """
        Perform an HTTP request.

        Warning:
            If the method return the response object,
            remember to use the returned obj in a 'with' statement,
            or call 'close()' method when you finished.

        Args:
            method (str)        : HTTP Method to use (see 'HTTPMethods' class)
            url (str)           : URL where retrieve the content
            ret_type (str)      : The expected response type (see 'HTTPResponse' class), but ignored if method==HTTPMethods.HEAD
            **kwargs (optional) : Other args supported by 'requests' module

        Returns:
            - If 'method' is HTTPMethods.HEAD or 'is_stream' is True
            requests.models.Response : The request obj (close() method must be called manually on it)

            - Otherwise is based on declared type
            HTTPResponse.RAW  -> bytes : The raw response body
            HTTPResponse.TEXT -> str   : The text response body
            HTTPResponse.JSON -> dict  : The dict parsed from JSON response body

        Raises:
            HTTPRequestException : if an exception occurs during the request
        """

        # Check method and return type
        if not method in HTTPMethods.values:
            raise HTTPRequestException('The request method "{}" is invalid or not supported'.format(method))
        if not ret_type in HTTPResponse.values:
            raise HTTPRequestException('The return type "{}" is invalid or not supported'.format(ret_type))

        # Set connector default params
        # By default, GET/POST requests follow redirects
        kwargs.setdefault('allow_redirects', method in (HTTPMethods.GET, HTTPMethods.POST))
        kwargs.setdefault('headers', self._connector_headers)
        kwargs.setdefault('timeout', self._connector_timeout)
        kwargs.setdefault('stream', False)

        self._logger.debug('Sending {} {} request at "{}" with params: {}'.format(
            method.upper(), ret_type.upper(), url, kwargs))
        try:
            # Perform the request
            res = getattr(self._connector, method)(url, **kwargs)
            self._logger.debug('Received response code: {}'.format(res.status_code))
            res.raise_for_status()
        except RequestException as ex:
            raise HTTPRequestException(ex)

        # Return response
        if method == HTTPMethods.HEAD or kwargs['stream']:
            # Return the response object
            return res
        elif ret_type == HTTPResponse.RAW:
            # Return the raw content
            self._logger.debug('Response body:\n{}\n'.format(res.content))
            return res.content
        elif ret_type == HTTPResponse.JSON:
            # Return the dict parsed from JSON response
            self._logger.debug('Response body:\n{}\n'.format(res.content))
            self._logger.debug('Parsing JSON response ...')
            try:
                try:
                    return res.json()
                except TypeError:
                    return res.json
            except ValueError as ex:
                raise HTTPRequestException(ex)
        else:
            # Return the response text
            self._logger.debug('Response body:\n{}\n'.format(res.text))
            return res.text

    def _download_file(self, dl_data):
        """
        Download a file.

        Params:
            - dl_data (DownloadData) : All data needed to download the file

        Returns:
            None
        """
        try:
            self._logger.debug('Init download -> {}'.format(dl_data))
            with self._http_dl_req(dl_data.method, dl_data.url, params=dl_data.params, data=dl_data.data) as r:
                # Parse file size (if provided)
                file_size = int(r.headers.get('content-length', 0))
                if file_size <= 0:
                    self._logger.debug('File size not provided')
                else:
                    self._logger.debug('File size -> {} bytes'.format(file_size))
                self._logger.debug('Opening file for writing -> {}'.format(dl_data.path))
                # Open file and begin the download
                with open(dl_data.path, 'wb') as f:
                    pbar = download_progressbar(file_size)
                    for chunk in pbar(r.iter_content(chunk_size=CHUNK_SIZE)):
                        if chunk:
                            f.write(chunk)
            self._logger.debug('Download done')
        except Timeout:
            raise HTTPRequestException("Request timeout -> {}".format(dl_data))
        except (RequestException, OSError, IOError) as ex:
            if not dl_data.can_fail:
                raise HTTPRequestException(ex)
            else:
                # If created, remove 'dl_data.path' file
                if self._check_file(dl_data.path):
                    self._delete_file(dl_data.path)

    # ---------------------------------------------------------------------------
    # -------------------------- Manager Core -----------------------------------
    # ---------------------------------------------------------------------------

    def _manager(self, mode):
        """
        Call this method to install/update/remove automatically the program.
        If the program isn't installed, it will be installed.

        Params:
            mode (str) : operation to perform (one of: 'install', 'update', 'remove')

        Returns:
            (bool, str, str) : (Version changed, Version after operations, Time elapsed)
        """

        # If the program is x64 only and the system is x86, exit
        if self.x64_only and self._arch == '32':
            print('Cannot install "{}" (it is only for x64 systems)'.format(self.program_name))
            return (False, self._current_version, '00:00:00')

        # If the mode is update and it is disabled, exit
        if mode == 'update' and not self.can_update:
            print('The "{}" update is disabled'.format(self.program_name))
            return (False, self._current_version, '00:00:00')

        # Get start time
        start_time = time.time()

        # Remove the program
        if mode == 'remove':
            # Remove paths from system path
            print('Removing links ...')
            for l in self._executables[:]:
                self._syspath_remove(l)
                self._executables.pop(0)

            # Perform custom uninstall
            print('Uninstalling {} ...'.format(self.program_name))
            self._remove_program()

            # Remove self._path (if the program is portable and it exists)
            if self.is_portable and self._path and self._check_dir(self._path):
                self._delete_dir(self._path)

            # Get time elapsed
            time_elapsed = format_time( time.time() - start_time )
            print('Done - Time elapsed: {}'.format(time_elapsed))
            return (True, None, time_elapsed)

        #### Install/Update the program

        # Set actual mode
        self._mode = mode

        # Get latest versions
        self._latest_version = self._get_latest_version()

        # Check latest_version
        version_changed = False
        if mode == 'install' or self._latest_version != self._current_version:
            # Print first message
            if mode == 'install':
                print('Installing {} v{} ...'.format(self.program_name, self._latest_version))
            else:
                print('Updating {} from v{} to v{} ...'.format(self.program_name, self._current_version, self._latest_version))

            # Parse download data
            self._dl_data_list = self._get_download_data()
            if self._dl_data_list:
                if is_dl_data(self._dl_data_list):
                    self._dl_data_list = [self._dl_data_list]
                elif not is_list(self._dl_data_list) or not all(is_dl_data(x) for x in self._dl_data_list):
                    raise ImplementationError('The method "_get_download_link" must return a single DownloadData or a DownloadData list')

            # If a path is provided, create it if not exists
            try:
                if self._path:
                    self._make_dir(self._path)
            except OSError:
                raise ImplementationError('Invalid path provided')

            # Download all needed files
            for dl_data in self._dl_data_list:
                print('Downloading {} ...'.format(os.path.split(dl_data.path)[1]))
                self._download_file(dl_data)

            # Extract operation
            print('Extracting ...')
            self._extract_latest_version()

            # Post-extract operation (to install/update the program)
            if mode == 'install':
                print('Installing ...')
                self._install_program()
                print('Creating links ...')
                executables = self._get_executables()
                if is_string(executables):
                    executables = [executables]
                if is_list(executables) and all(not self._check_file(e) and self._check_abs_path(e) for e in executables):
                    for ex in executables:
                        if not ex.endswith('\\'):
                            ex = ex + '\\'
                        self._syspath_add(ex)
                        self._executables.append(ex)
                else:
                    raise ImplementationError('The method "_get_executables" must return a single absolute path or an absolute path list to folders')
            else:
                print('Updating ...')
                self._update_program()

            # Update actual version
            version_changed = True
            self._current_version = self._latest_version

            # Delete all temp attributes
            del self._latest_version
            del self._dl_data_list

            time_elapsed = format_time( time.time() - start_time )
            print('Done - Time elapsed -> ' + time_elapsed)
        else:
            time_elapsed = format_time( time.time() - start_time )
            print('{} is already up to date -> v{}'.format(self.program_name, self._current_version))

        # Delete mode attribute
        del self._mode

        return (version_changed, self._current_version, time_elapsed)

    # ---------------------------------------------------------------------------
    # -------------------------- Specific Methods -------------------------------
    # ---------------------------------------------------------------------------

    def _get_latest_version(self):
        """
        Parse program latest version.

        Advices:
            - The logger interface is in 'self._logger'
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
        Perform the actions needed to update the program and clean temporary files.
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
        Perform the actions to install the program and clean temporary files.
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

        raise NotImplementedError('You must implement "_uninstall_program" method!')

    # ---------------------------------------------------------------------------
    # -------------------------- Getters ----------------------------------------
    # ---------------------------------------------------------------------------

    @property
    def current_version(self):
        return self._current_version

    @property
    def path(self):
        return self._path

    @property
    def executables(self):
        return self._executables[:]

    @property
    def prog_data(self):
        return {
            self.program_name.lower(): {
                'executables'   : self.executables,
                'path'          : self.path,
                'version'       : self.current_version,
            }
        }

    # ---------------------------------------------------------------------------
    # -------------------------- Main Actions -----------------------------------
    # ---------------------------------------------------------------------------

    def install(self):
        """
        Call this method to install automatically the program.
        If an error occurred, an error message is printed, and False is returned.

        Returns:
            (bool, str, str) : (Instllation done, Version installed, Time elapsed)
        """

        # If already installed, exit
        if self._current_version:
            return (False, None, None)

        # Install the program
        return self._manager('install')[1:]

    def remove(self):
        """
        Call this method to remove automatically the program.
        If an error occurred, an error message is printed, and False is returned.

        Returns:
            (bool, str) : (Remove done, Time elapsed)
        """

        # If not installed, exit
        if not self._current_version:
            return (False, None)

        # Remove the program
        return (True, self._manager('remove')[2])

    def update(self):
        """
        Call this method to update automatically the program (if needed).
        If an error occurred, an error message is printed, and False is returned.

        Returns:
            (bool, str, str) : (Update done, Version after update, Time elapsed)
        """

        # If not installed, exit
        if not self._current_version:
            return (False, None, None)

        # Update the program
        return self._manager('update')
