# Copyright (C) 2014-2018 Enzien Audio, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict
import os

from .HeavyException import HeavyException


class LocalVars:
    """ A set of scoped objects.
    """

    def __init__(self, stdlib_dir="./"):
        # a dictionary of name-registered objects
        # the data structure is a list map
        # key is the name under which the object is registered, value is a
        # list of all objects who are registered with that name
        self.__REGISTERED_OBJ_DICT = defaultdict(list)

        # the list of globally declared paths
        self.declared_paths = [stdlib_dir]  # initialise with the standard library directory

    def find_path_for_abstraction(self, name):
        # the file name based on the abstraction name
        file_name = "{0}.hv.json".format(name)

        # iterate in order through the declared paths in order to find the file
        for d in self.declared_paths:
            file_path = os.path.join(d, file_name)
            if os.path.exists(file_path):
                return file_path  # if a matching abstraction is found, return the path
        return None  # otherwise return None

    def add_import_paths(self, path_list):
        """ Add import paths. Paths are expanded and made as explicit as possible.
        """
        self.declared_paths.extend([os.path.abspath(os.path.expanduser(p)) for p in path_list])

    def register_object(self, obj, name, static=False, unique=False):
        """ Registers a named object.
        """

        objs = self.get_objects_for_name(name, obj.type)
        if (unique and len(objs) > 0) or (static and len(objs) > 1):
            # if there is already a registered object of this type and the new
            # object is not declared as static, throw an error
            raise HeavyException(f"Object {obj} with name \"{name}\" already exists, "
                                 "and the new object is static or unique.")
        elif len(objs) == 1 and static:
            pass  # the static object has already been registered, move on
        else:
            self.__REGISTERED_OBJ_DICT[name].append(obj)

    def unregister_object(self, obj, name):
        """ Unregisters a named object.
        """

        self.__REGISTERED_OBJ_DICT[name].remove(obj)

    def get_objects_for_name(self, name, obj_types):
        """ Returns a list of objects registered under a name in this scope.
        """

        obj_types = obj_types if isinstance(obj_types, list) else [obj_types]
        return [o for o in self.__REGISTERED_OBJ_DICT[name] if o.type in obj_types]

    def get_registered_objects_for_type(self, obj_type):
        """ Returns a list-dictionary for all objects of the given type, indexed by name.
        """

        d = defaultdict(list)
        for k, v in self.__REGISTERED_OBJ_DICT.items():
            x = [o for o in v if o.type == obj_type]
            if len(x) > 0:  # only return names that actually have associated objects
                d[k].extend(x)
        return d
