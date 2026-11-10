# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

from hvcc.types.compiler import CompilerNotif


class HeavyGenException(Exception):
    """ This exception is raised if anything goes wrong during the ir2c or generator compilation process.
    """

    def __init__(self, message: str = "") -> None:
        super(Exception, self).__init__(message)
        self.message = message
        self.notes: CompilerNotif = CompilerNotif()
