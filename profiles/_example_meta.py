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

# This import is necessary for get Meta_Profile
from ._base import Meta_Profile

# This import makes available all models and functions contained in '_utils.py'
from ._utils import *

'''
This is an example of a meta profile.
A meta profile is a 'group' of programs names useful to install them easily.

All meta-profile classes MUST inherit 'Meta_Profile'.

To implement a meta profile, you must:
- Assign at 'meta_name' attribute the meta profile name (that must be unique)
- Fill 'programs' attribute with programs names (are allowed only profile names, not meta profiles names)
'''

class Example_Meta_Profile(Meta_Profile):

    '''
    Meta-Program Name

    The value of this attribute MUST be specified
    '''

    # Type here the meta-program name (str)
    meta_name = 'Example_Meta'

    '''
    Programs group

    You MUST specify here the programs 'group' of this meta-program.
    The value MUST be a set and MUST contains at least one program name.
    '''

    # Type here the programs group of the meta-program (set of programs names)
    programs = set('example')
