
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
