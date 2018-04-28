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

import logging
import json
import os
import progressbar
import validators
import time

from datetime import datetime
from python_utils.terminal import get_terminal_size
from ._errors import ImplementationError

CHUNK_SIZE = 1024

''' Models '''

class HTTPMethods():
    """
    Supported HTTP Methods
    """

    GET  = 'get'
    HEAD = 'head'
    POST = 'post'

    values = ['get', 'head', 'post']

class HTTPResponse():
    """
    Supported HTTP Responses
    """

    RAW  = 'raw'
    TEXT = 'text'
    JSON = 'json'

    values = ['raw', 'text', 'json']

class DownloadData():
    """
    Wrapper to require the download of a file.
    """
    def __init__(self, path, method, url, params=None, data=None, can_fail=False):
        """
        Init a download request.

        Params:
            path (str)   : Path where save the downloaded file
            method (str) : HTTP Method to use for download (HTTPMethods.GET or HTTPMethods.POST)
            url (str)    : URL where retrieve the content
            params       : Dictionary or bytes to be sent in the query string (GET data)
            data         : Dictionary or list of tuples ``[(key, value)]`` (will be form-encoded), bytes, or file-like object to send in the body (POST data)
            can_fail (bool): If True, the download can fail without errors, otherwise if it fail an error will be raised
        """

        # Check and set method
        if method in (HTTPMethods.GET, HTTPMethods.POST):
            self._method = method
        else:
            raise ImplementationError('DownloadData: the method "{}" is invalid'.format(method))

        # Check and set path
        if (path and is_string(path)):
            self._path = path
        else:
            raise ImplementationError('DownloadData: the path "{}" is invalid'.format(path))

        # Check and set URL
        if validators.url(url):
            self._url = url
        else:
            raise ImplementationError('DownloadData: the url "{}" is invalid'.format(url))

        # Check and set params
        if params is None or isinstance(params, (dict, str, bytes)):
            self._params = params
        else:
            raise ImplementationError('DownloadData: the params "{}" is invalid'.format(params))

        # Check and set data
        if data is None or (isinstance(data, (dict, list)) and all(len(x)==2 for x in data)):
            self._data = data
        else:
            raise ImplementationError('DownloadData: the data "{}" is invalid'.format(data))

        # Set can_fail
        self._can_fail = bool(can_fail)

    def __repr__(self):
        return "<path={} ; method={} ; URL={} ; params={} ; data={} ; can_fail={}>" \
        .format(self._path, self._method, self._url, self._params, self._data, self._can_fail)

    __str__ = __repr__

    @property
    def method(self):
        return self._method

    @property
    def url(self):
        return self._url

    @property
    def params(self):
        return self._params

    @property
    def data(self):
        return self._data

    @property
    def path(self):
        return self._path

    @property
    def can_fail(self):
        return self._can_fail

def dl_get(path, url, params=None, data=None, can_fail=False):
    """
    Shortcut to make a DownloadData object which provides a GET request.

    All params meaning are the same of DownloadData '__init__' method.
    """
    return DownloadData(
            path,
            HTTPMethods.GET,
            url,
            params,
            data,
            can_fail
        )

def dl_post(filename, url, params=None, data=None, can_fail=False):
    """
    Shortcut to make a DownloadData object which provides a POST request.

    All params meaning are the same of DownloadData '__init__' method.
    """
    return DownloadData(
            path,
            HTTPMethods.POST,
            url,
            params,
            data,
            can_fail
        )

def download_progressbar(total_size):
    """
    Create a progress bar to show in real-time a download status
    """

    # Compute DownaloadProgressBar max value
    if total_size <= 0:
        max_val = progressbar.UnknownLength
    else:
        max_val = int(total_size/CHUNK_SIZE)

    # DownaloadProgressBar settings
    MARKER          = '█'
    PREFIXES        = ('', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')[1:]
    POLL_INTERVAL   = 0.8

    # DownaloadProgressBar spacing
    LEFT_SPACE          = 4
    PERCENTAGE_SPACE    = 4
    PRE_BAR_SPACE       = 1
    BAR_SPACE           = 35
    POST_BAR_SPACE      = 1
    DATA_SIZE_SPACE     = 8
    PRE_SPEED_SPACE     = 1
    SPEED_SPACE         = 8

    # Compute right spacing, and ensure that is not negative
    try:
        right_space = int(get_terminal_size()[0]) - \
        LEFT_SPACE - PERCENTAGE_SPACE - PRE_BAR_SPACE - BAR_SPACE - \
        POST_BAR_SPACE - DATA_SIZE_SPACE - PRE_SPEED_SPACE - SPEED_SPACE
        if right_space < 0:
            right_space = 0
    except (ValueError, TypeError, ArithmeticError):
        right_space = 0

    # Define DownaloadProgressBar skin
    bar_skin=([
        LEFT_SPACE * ' ',
        progressbar.Percentage(),
        PRE_BAR_SPACE * ' ',
        progressbar.Bar(marker=MARKER),
        POST_BAR_SPACE * ' ',
        progressbar.DataSize(prefixes=PREFIXES),
        PRE_SPEED_SPACE * ' ',
        progressbar.AdaptiveTransferSpeed(prefixes=PREFIXES),
        right_space * ' '
        ])

    # Generate DownaloadProgressBar
    return progressbar.ProgressBar(
        max_value=max_val, widgets=bar_skin, poll_interval=POLL_INTERVAL)


''' OS '''

# Edited version of shutil.copytree(...), that allow folders overwrite
from shutil import copy2 as _default_copy
def copytree(src, dst, symlinks=False, ignore=None, copy_function=_default_copy,
             ignore_dangling_symlinks=False):
    """Recursively copy a directory tree.
    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.
    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied. If the file pointed by the symlink doesn't
    exist, an exception will be added in the list of errors raised in
    an Error exception at the end of the copy process.
    You can set the optional ignore_dangling_symlinks flag to true if you
    want to silence this exception. Notice that this has no effect on
    platforms that don't support os.symlink.
    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():
        callable(src, names) -> ignored_names
    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.
    The optional copy_function argument is a callable that will be used
    to copy each file. It will be called with the source path and the
    destination path as arguments. By default, copy2() is used, but any
    function that supports the same signature (like copy()) can be used.
    """
    from shutil import copystat, copy2, Error

    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    # EDIT: Allow folder overwriting
    if not os.path.isdir(dst):
        os.makedirs(dst)

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.islink(srcname):
                linkto = os.readlink(srcname)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    copystat(srcname, dstname, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink if the flag is on
                    if not os.path.exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occurs. copy2 will raise an error
                    if os.path.isdir(srcname):
                        copytree(srcname, dstname, symlinks, ignore,
                                 copy_function)
                    else:
                        copy_function(srcname, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore, copy_function)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)
    return dst


''' Time and Date '''

def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '%02d:%02d:%02d' % (h, m, s)

def parse_html_time(html_time):
    t = datetime.strptime(html_time, '%a, %d %b %Y %H:%M:%S %Z')
    return t.strftime('%Y.%m.%d-%H:%M:%S %Z').strip()


''' Check '''

def is_string(x):
    return isinstance(x, str)

def is_dict(x):
    return isinstance(x, dict)

def is_set(x):
    return isinstance(x, set)

def is_list(x):
    return isinstance(x, list)

def is_dl_data(x):
    return isinstance(x, DownloadData)

def is_int(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

def is_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

def is_two_power(n):
	return is_int(n) and n != 0 and ((n & (n - 1)) == 0)

def is_divisible(n, d):
    try:
        return n % d == 0
    except (ValueError, ArithmeticError):
        return False
