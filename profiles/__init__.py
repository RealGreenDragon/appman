import importlib
import logging
import os
import pkgutil

from ._base import Base_Profile, Meta_Profile
from ._errors import ImplementationError
from ._utils import is_set

# Import all modules in this folder
_profiles_dirs = [os.path.dirname(os.path.abspath(__file__))]
for (module_loader, name, ispkg) in pkgutil.iter_modules(_profiles_dirs):
    if not name.startswith('_'):
        importlib.import_module('.' + name, __package__)

# Get all subclasses of 'Base_Profile'
_PROFILES = { cls.program_name.lower(): cls for cls in Base_Profile.__subclasses__() }
_PROFILES_KEYS = set(_PROFILES.keys())

# Check 'profiles' names are always implemented and not collide between them
if Base_Profile.program_name.lower() in _PROFILES_KEYS:
    raise ImplementationError('One or more "profiles" not implements theirs "program_name"')
if len(_PROFILES_KEYS) != len(Base_Profile.__subclasses__()):
    raise ImplementationError('Collision detected between names of profiles')

# Get all subclasses of 'Meta_Profile'
_META = { cls.meta_name.lower(): cls.programs for cls in Meta_Profile.__subclasses__() }
_META_KEYS = set(_META.keys())

# Check 'meta-profiles' names are always implemented and not collide between them
if Meta_Profile.meta_name.lower() in _META_KEYS:
    raise ImplementationError('One or more "meta-profiles" not implements theirs "meta_name"')
if len(_META_KEYS) != len(Meta_Profile.__subclasses__()):
    raise ImplementationError('Collision detected between names of profiles')

# Check that the names of 'profiles' and 'meta-profiles' not collide
_profiles_intersection = _PROFILES_KEYS & _META_KEYS
if _profiles_intersection:
    raise ImplementationError('Collision detected between names of profiles and meta-profiles -> {}'.format(_profiles_intersection))

# Check for each meta-program if all its programs exists and itself is not in the set
for meta_name, prog_set in _META.items():
    if not is_set(prog_set):
        raise ImplementationError('The "{}" meta-profile programs set is not a set'.format(meta_name))
    if not prog_set:
        raise ImplementationError('The "{}" meta-profile programs set is empty'.format(meta_name))
    if meta_name in prog_set:
        raise ImplementationError('The "{}" meta-profile programs set contains itself'.format(meta_name))
    if not prog_set <= _PROFILES_KEYS:
        raise ImplementationError('The "{}" meta-profile programs set contains unknown programs'.format(meta_name))

# Check for each program if all its dependences exists and itself is not in the set
for name, cls in _PROFILES.items():
    dep_set = cls.dependences
    if not is_set(dep_set):
        raise ImplementationError('The "{}" profile dependences set is not a set'.format(name))
    if name in dep_set:
        raise ImplementationError('The "{}" profile dependences set contains itself'.format(name))
    if not dep_set <= _PROFILES_KEYS:
        raise ImplementationError('The "{}" profile dependences set contains unknown programs'.format(name))

def get_supported_programs():
    return _PROFILES.keys()

def get_supported_programs_list():
    return sorted(_PROFILES.keys())

def get_supported_meta_programs():
    return _META.keys()

def get_supported_meta_programs_list():
    return sorted(
        [meta_name + ' -> ' + ', '.join(sorted(programs)) for meta_name, programs in _META.items()]
    )

def expand_meta_program(name):
    return sorted(list(_META[name]))

def get_profile(name, prog_data=dict()):
    return _PROFILES[name](**prog_data)
