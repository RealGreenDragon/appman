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

''' Source code data '''
__title__           = 'appman'
__author__          = 'Daniele Giudice'
__version__         = '0.1.3'
__license__         = 'GNU General Public License v3'
__copyright__       = 'Copyright 2018 Daniele Giudice'
__description__     = 'An application manager for Windows'

import argparse
import json
import logging
import os
import platform
import sys
import subprocess
import time
import traceback
import winvers

# Check that the OS is Windows
if winvers.get_version() == winvers.NO_WIN:
    raise EnvironmentError('This program works only on Windows OSs')

# Add the appman directory to the path
APPMAN_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.append(APPMAN_DIR)

# Now can import profiles and utils
from profiles import get_supported_programs, get_supported_programs_list, \
get_supported_meta_programs, get_profile, expand_meta_program
from profiles._utils import *
from profiles._errors import *

# Define log format
LOG_FORMAT = logging.Formatter('[%(asctime)s] %(levelname)8s - %(name)s: %(message)s')


''' AppMan wrapper '''

class ApplicationManager():
    def __init__(self):
        # Get logger
        self._logger = logging.getLogger('appman.wrapper')

        # Init vars
        self._refresh_env_cmd = 'cmd /c RefreshEnv.bat'
        self._db_path = os.path.join(APPMAN_DIR, 'data.json')
        self._db = {
            'dependences': {},
            'installed': {}
        }

        # The path must be a string
        if not is_string(self._db_path):
            raise ProgramDBException('Invalid path -> {}'.format(self._db_path))

        # Parse path directory and check if is writable
        db_dir = os.path.split(self._db_path)[0]
        if not ( os.path.isdir(db_dir) and os.access(db_dir, os.W_OK) ):
            raise ProgramDBException('Invalid path (directory inexistent or not writable) -> {}'.format(self._db_path))

        # Define temporary DB file path
        self._db_path_tmp = self._db_path + '.tmp'

        # Check if the DB exists and if can be opened
        db_found = False
        if os.path.isfile(self._db_path):
            if not os.access(db_dir, os.W_OK):
                raise ProgramDBException('ProgDB: DB file found at {}, but cannot be opened'.format(self._db_path))
            self._logger.debug('ProgDB found at {} -> it can be opened'.format(self._db_path))
            db_found = True
        else:
            self._logger.debug('ProgDB not found at {} -> it can be created'.format(self._db_path))

        # If found load it, else create it
        if db_found:
            self._read_json()
        else:
            self._write_json()

        # Parse available profiles list
        self._supported_programs = get_supported_programs()
        self._supported_meta_programs = get_supported_meta_programs()

        # Check that all installed programs profiles is avaialble
        res = set(self.installed_programs) - set(self._supported_programs)
        if res:
            raise ImplementationError(
                'Programs installed, but profiles not found: ' + ', '.join(res)
                )

    def __repr__(self):
        return "<AppMan Wrapper - DB Path: {} - Programs installed: {}>" \
            .format(self._db_path, len(self.installed_programs))

    __str__ = __repr__

    def __del__(self):
        del self._db_path
        del self._db

    def _read_json(self):
        self._logger.debug('Opening JSON file for reading --> {}'.format(
            self._db_path
            ))
        try:
            with open(self._db_path, encoding='UTF-8') as f:
                json_content = json.load(f)
                self._logger.debug('Content: \n' + json.dumps(json_content))
                self._db = json_content
        except (IOError, OSError) as ex:
            raise ProgramDBException('Cannot open ProgDB for reading')
        except ValueError as ex:
            raise ProgramDBException('Cannot parse ProgDB JSON content')

    def _write_json(self):
        self._logger.debug('Opening JSON file for writing --> {}\nContent: {}'.format(
            self._db_path_tmp, self._db
            ))
        try:
            with open(self._db_path_tmp, 'w', encoding='UTF-8') as f:
                json.dump(self._db, f, indent=4, sort_keys=True)
            self._logger.debug('Replacing old ProgDB with the updated version')
            os.remove(self._db_path)
            os.rename(self._db_path_tmp, self._db_path)
        except (IOError, OSError) as ex:
            raise ProgramDBException('Cannot open ProgDB for writing')
        except ValueError as ex:
            raise ProgramDBException('Cannot serialize ProgDB content to JSON')

    def _add_dependences(self, prog_name, dependences):
        for dep in dependences:
            if not dep in self._db['dependences']:
                self._db['dependences'][dep] = [prog_name]
            elif not prog_name in self._db['dependences'][dep]:
                self._db['dependences'][dep].append(prog_name)
                sorted(self._db['dependences'][dep])

    def _refresh_env(self):
        # Try to refresh Environmental Variables in the actual shell
        try:
            with open(os.devnull, 'w') as devnull:
                subprocess.run(self._refresh_env_cmd, stdout=devnull, stderr=devnull, shell=True, check=True)
        except subprocess.CalledProcessError:
            print('WARNING: Cannot Refresh Environmental Variables (restart the shell to see the changes).')

    @property
    def installed_programs(self):
        return list(self._db['installed'].keys())

    @property
    def supported_programs(self):
        return self._supported_programs

    @property
    def supported_meta_programs(self):
        return self._supported_meta_programs

    @property
    def installed_report(self):
        installed = self.installed_programs
        if installed:
            return 'Installed programs:\n- '+'\n- '.join([
                    p + " v{}".format(self._db['installed'][p]['version']) \
                    for p in installed \
                ])
        else:
            return 'No programs installed'

    @property
    def available_report(self):
        if not self._supported_programs:
            return 'No Profiles available'
        else:
            report = 'Profiles available:\n- '+'\n- '.join([
                p + " (installed v{})".format(self._db['installed'][p]['version']) \
                if p in self._db['installed'] else p for p in self._supported_programs \
            ])
            if not self._supported_meta_programs:
                report += '\n\nNo Meta-Profiles available'
            else:
                report += '\n\nMeta-Profiles available:\n- '+'\n- '.join([
                        '{} -> {}'.format(p, ', '.join(expand_meta_program(p))) \
                        for p in self._supported_meta_programs \
                    ])
            return report

    @property
    def path(self):
        return self._db_path

    def install(self, prog_name):
        if prog_name in self._db['installed']:
            print('"{}" v{} is already installed'.format(
                prog_name,
                self._db['installed'][prog_name]['version']
                ))
            return False

        # Parse program profile and its dependences
        p = get_profile(prog_name)
        dependences = p.dependences

        # Check that all dependences are satisfied (install them if needed)
        if dependences:
            print('Checking "{}" dependences ...'.format(prog_name))
            for dep in dependences:
                try:
                    self.install(dep)
                except Exception as ex:
                    traceback.print_exc()
                    print('Cannot install "{}" due a problem with the dependence "{}"'.format(prog_name, dep))
                    return False

        # Install the program
        res = p.install()
        self._logger.debug('Install return value -> {}'.format(res))

        try:
            if res[0]:
                # If the install succeed, update the DB
                self._logger.debug('Updating {} DB record ...'.format(prog_name))
                self._db['installed'].update(p.prog_data)
                self._add_dependences(prog_name, dependences)

                # Update DB and cleanup
                self._write_json()
                del p

                # Try to refresh Environmental Variables in the actual shell
                self._refresh_env()

                # Exit
                return True
            else:
                del p
                return False
        except Exception as ex:
            del p
            raise ex

    def update(self, prog_name):
        if not prog_name in self._db['installed']:
            print('Cannot update "{}", because it is not installed'.format(prog_name))
            return False

        # Parse program profile
        p = get_profile(prog_name, self._db['installed'][prog_name])

        # Update the program
        res = p.update()
        self._logger.debug('Update return value -> {}'.format(res))

        try:
            if res[0]:
                # If the update succeed, update the DB
                self._logger.debug('Updating {} DB record ...'.format(prog_name))
                self._db['installed'].update(p.prog_data)

                # Update DB and cleanup
                self._write_json()
                del p

                # Exit
                return True
            else:
                self._logger.debug('Version not changed, so {} DB record not updated'.format(prog_name))
                del p
                return False
        except Exception as ex:
            del p
            raise ex

    def remove(self, prog_name):
        if not prog_name in self._db['installed']:
            print('Cannot remove "{}", because it is not installed'.format(prog_name))
            return False

        # A program can be removed only if its dependences set is empty (so it is not necessary fo any other programs)
        try:
            if self._db['dependences'][prog_name]:
                print('Cannot remove "{}", because it is necessary for:\n{}'.format(
                    prog_name,
                    '\n'.join(self._db['dependences'][prog_name])
                    ))
                return False
        except KeyError:
            pass

        # Parse program profile
        p = get_profile(prog_name, self._db['installed'][prog_name])

        # Remove the program
        res = p.remove()
        self._logger.debug('Remove return value -> {}'.format(res))

        try:
            if res[0]:
                # If the remove succeed, update the DB
                self._logger.debug('Updating {} DB record ...'.format(prog_name))

                # Remove the program from installed
                self._db['installed'].pop(prog_name, None)
                self._db['dependences'].pop(prog_name, None)

                # Remove the program from dependences lists
                for dep in self._db['dependences']:
                    try:
                        self._db['dependences'][dep].remove(prog_name)
                    except (TypeError, ValueError, KeyError):
                        pass

                # Update DB and cleanup
                self._write_json()
                del p

                # Try to refresh Environmental Variables in the actual shell
                self._refresh_env()

                # Exit
                return True
            else:
                del p
                return False
        except Exception as ex:
            del p
            raise ex


''' AppMan Main Functions '''

def appman_shutdown(logger, appman_wrapper):
    if appman_wrapper:
        del appman_wrapper
    if logger:
        # Flush, close, and remove all logger handlers
        for handler in logger.handlers[:]:
            handler.flush()
            handler.close()
            logger.removeHandler(handler)
        # Shutdown logging module
        logging.shutdown()

def appman_init():
    parser = argparse.ArgumentParser(description=__description__,
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     )
    parser.add_argument(
        'mode',
        choices=['install', 'remove', 'update', 'available', 'installed'],
        help='Action to perform, one of: \n' \
        '- install   -> install one/more not installed programs (requires admin privileges)\n' \
        '- remove    -> remove one/more installed programs (requires admin privileges)\n' \
        '- update    -> update one/more installed program\n' \
        '- available -> list all available program profiles\n' \
        '- installed -> list all installed programs\n'
    )
    parser.add_argument(
        'programs',
        nargs='*',
        help='Space separated list of program names (usable only if "mode" is install/update/remove). ' \
        '\nThe keyword "all" can be used to update all programs installed.'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='Version: {} - Author: {}'.format(__version__, __author__),
        help="Show program's author, version number and exit"
    )
    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='Enable debug mode'
    )

    # Parse args
    args = vars(parser.parse_args())

    # Check that the running OS is Windows Vista or upper
    if winvers.get_version() >= winvers.WIN_VISTA:
        if args['mode'] in ('install', 'remove'):
            # If required, check that the user is Admin
            try:
                # This check works only  if "winvers.get_version() >= winvers.WIN_XP_SP2"
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    parser.error('"{}" mode requires admin privileges'.format(args['mode']))
            except Exception:
                parser.error('Windows OS detected, but admin check failed')
    else:
        parser.error('This program works only on Windows Vista or newer')

    # If in listing mode, no programs can be specified
    if args['mode'] in ('available', 'installed') and args['programs']:
        parser.error('Cannot specify any programs if "mode" is available/installed')

    # Init logger
    logger = logging.getLogger('appman')
    if args['debug']:
        _log_handler = logging.StreamHandler()
        _log_handler.setFormatter(LOG_FORMAT)
        _log_level = logging.DEBUG
    else:
        _log_handler = logging.NullHandler()
        _log_level = logging.WARN
    logger.setLevel(_log_level)
    logger.addHandler(_log_handler)
    logger.debug('appman debug module init finished')

    # Load appman wrapper
    try:
        appman_wrapper = ApplicationManager()
    except Exception as ex:
        traceback.print_exc()
        return (logger, None, None)

    # Get installed programs and profiles available
    prog_installed = appman_wrapper.installed_programs
    supported_programs = get_supported_programs()
    supported_meta_programs = get_supported_meta_programs()

    # If requested show lists and exit
    if args['mode'] == 'available':
        print(appman_wrapper.available_report)
        return (logger, None, appman_wrapper)
    elif args['mode'] == 'installed':
        print(appman_wrapper.installed_report)
        return (logger, None, appman_wrapper)

    # Check intsalled
    if args['mode'] == 'update' and not prog_installed:
        parser.error('No programs installed, so cannot update nothing')

    # Check if select all
    args['update_all'] = 'all' in args['programs']

    if args['update_all']:
        # If 'all' is present, check that it is used correctly and expand it
        if args['mode'] != 'update':
            parser.error('"all" selector can be used only in "update" mode')
        if len(args['programs']) > 1:
            parser.error('"all" selector must be the only value in "program" parameter')
        args['programs'] = appman_wrapper.installed_programs
    else:
        # Otherwise, expand meta-pofiles and check all programs profiles
        programs = []
        for prog in args['programs']:
            if not prog in appman_wrapper.supported_programs:
                if prog in appman_wrapper.supported_meta_programs:
                    exp = expand_meta_program(prog)
                    logger.debug("Expand {} meta-program -> {}".format(prog, exp))
                    programs += exp
                else:
                    print('Cannot find "{}" profile'.format(prog))
                    return (logger, None, appman_wrapper)
            else:
                programs.append(prog)
        args['programs'] = programs

    # Return args dict
    return (logger, args, appman_wrapper)

def appman_main():
    start_time = time.time()

    # Parse args, init loger, load database
    logger, args, appman_wrapper = appman_init()
    if not (args and appman_wrapper):
        appman_shutdown(logger, appman_wrapper)
        return

    # Parse method to perform actions in the mode requested
    try:
        run_action = getattr(appman_wrapper, args['mode'])
    except AttributeError:
        raise RuntimeError('Invalid mode')

    # Run requested action on each program provided
    for prog_name in args['programs']:
        try:
            run_action(prog_name)
        except EnvironmentError as ex:
            traceback.print_exc()
            try:
                el_time = format_time( time.time() - start_time )
                appman_shutdown(logger, appman_wrapper)
                print("\nCritical error raised -> Exit (Time elapsed: {})".format(el_time))
            except Exception:
                print("\nCritical error raised -> Exit")
            finally:
                os._exit(1)
        except (SystemExit, KeyboardInterrupt):
            try:
                el_time = format_time( time.time() - start_time )
                appman_shutdown(logger, appman_wrapper)
                print("\nInterrupt received -> Exit (Time elapsed: {})".format(el_time))
            except Exception:
                print("\nInterrupt received -> Exit")
            finally:
                os._exit(1)
        except Exception as ex:
            traceback.print_exc()
            print('{} {} skipped'.format(prog_name, args['mode']))
        finally:
            print()

    # Free resources
    appman_shutdown(logger, appman_wrapper)

    # Parse elapsed time
    elapsed_time = format_time( time.time() - start_time )

    print("All operations done - Time elapsed: " + elapsed_time)

if __name__ == '__main__':
    appman_main()
