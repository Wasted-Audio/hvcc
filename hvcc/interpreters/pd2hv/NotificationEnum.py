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

from enum import Enum

# http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python


class NotificationEnum(Enum):
    """ These enumerations refer to all possible warnings and errors produced by pd2hv.
    """

    # Warnings

    # an unspecified generic warning
    WARNING_GENERIC = 1000

    # an empty object has been added to a Pd graph
    WARNING_EMPTY_OBJECT = 1001

    # heavy only supports the -path flag to the Pd declare object
    WARNING_DECLARE_PATH = 1002

    # the object does nothing (and will likely be removed)
    WARNING_USELESS_OBJECT = 1003

    # the message box is empty and does nothing
    WARNING_EMPTY_MESSAGE = 1004

    # Errors

    # an unspecified generic error
    ERROR_GENERIC = 2000

    # the parser doesn't know how to handle the object
    ERROR_UNKNOWN_OBJECT = 2001

    # top-level graphs may not contain inlet~ or outlet~ objects
    ERROR_NO_TOPLEVEL_SIGNAL_LETS = 2002

    # only arguments 'a', 'f', 's', and 'b' are supported for trigger object
    ERROR_TRIGGER_ABFS = 2003

    # only arguments 'f', 'float' and numeric values are supported for pack object
    ERROR_PACK_FLOAT_ARGUMENTS = 2003

    # a value cannot be resolved because the required argument is missing
    ERROR_MISSING_REQUIRED_ARGUMENT = 2004

    # unique arguments are required for this object
    ERROR_UNIQUE_ARGUMENTS_REQUIRED = 2005

    # two objects cannot be connected
    ERROR_UNABLE_TO_CONNECT_OBJECTS = 2006

    # a particular connection (type?) is not supported
    ERROR_UNSUPPORTED_CONNECTION = 2007

    # Exception

    # the exception that was raised
    ERROR_EXCEPTION = 3000
