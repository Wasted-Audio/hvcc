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

from .HeavyException import HeavyException


class BufferPool:

    def __init__(self):
        # the idea is that the same buffer is reused as quickly as possible so that it doesn't need
        # to be moved around in the cache. It does not give substantially different results
        # from a Counter-based implementation, but it is more consistent and predictable.
        self.pool = {
            "~f>": defaultdict(list),
            "~i>": defaultdict(list)
        }

    def num_buffers(self, connection_type=None):
        """ Returns the number of buffers with the given retain count. By default returns
            the size of the entire pool. Number of buffers per connection type can also be retrieved.
        """
        if connection_type is None:
            return self.num_buffers("~f>") + self.num_buffers("~i>")
        elif connection_type in self.pool:
            return sum(len(v) for v in self.pool[connection_type].values())
        else:
            raise HeavyException("Unknown connection type: \"{0}\"".format(connection_type))

    def get_buffer(self, connection_type, count=1, excludeSet=None):
        """ Returns a currently unused buffer. The buffer can be assigned a retain count. An optional
            exclude set can also be supplied, ensuring that the returned buffer is not one of them.
        """
        excludeSet = excludeSet if excludeSet is not None else set()

        pool = self.pool[connection_type]

        # get the most recently used, unused buffer
        b = next((b for b in reversed(pool[0]) if b not in excludeSet), None)
        if b is not None:
            pool[0].remove(b)
        else:
            # if we get here, then no available buffer was found. Create a new one.
            b = (connection_type, self.num_buffers(connection_type))  # new buffer index for the given type
        pool[count].append(b)
        return b

    def retain_buffer(self, b, count=1):
        """ Increases the retain count of the buffer. Returns the new count.
        """
        # adc~ and ZERO_BUFFER are special. They cannot be retained.
        if b[0] in ["zero", "input"]:
            return 0
        else:
            pool = self.pool[b[0]]
            for k, v in pool.items():
                if b in v:
                    v.remove(b)
                    pool[k + count].append(b)
                    return k + count  # return the new retain count
            raise HeavyException("{0} not found in BufferPool!".format(b))

    def release_buffer(self, b, count=1):
        """ Reduces the retain count of the buffer. Returns the new count.
        """
        # adc~, ZERO_BUFFER, send~ buffers are special. They can not be released.
        # if the buffer is otherwise unknown (as may be in the case that objects provide their own),
        # they cannot be released
        if b[0] in ["zero", "input"]:
            return 0
        else:
            pool = self.pool[b[0]]
            for k, v in pool.items():
                if b in v:
                    v.remove(b)
                    pool[k - count].append(b)
                    return k - count  # return the new retain count
            raise HeavyException("{0} not found in BufferPool!".format(b))

    def __repr__(self):
        return self.pool["~f>"].__repr__() + self.pool["~i>"].__repr__()
