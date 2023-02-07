import hashlib
import os


def filter_max(i: int, j: int) -> int:
    """Calculate the maximum of two integers.
    """
    return max(int(i), int(j))


def filter_plugin_id(s: str) -> int:
    """ Return a unique id from patch name
        [0...32767
    """
    sh = hashlib.md5(s.encode('utf-8'))
    sd = sh.hexdigest()[:4]
    return int(sd, 16) & 0x7FFF


def filter_string_cap(s: str, li: int) -> str:
    """Returns a truncated string with ellipsis if it exceeds a certain length.
    """
    return s if (len(s) <= li) else f"{s[0:li - 3]}..."


def filter_templates(template_name: str) -> bool:
    return False if os.path.basename(template_name) in [".DS_Store"] else True


def filter_uniqueid(s: str) -> str:
    """ Return a unique id (in hexadecimal) for the Plugin interface.
    """
    sh = hashlib.md5(s.encode('utf-8'))
    sd = sh.hexdigest().upper()[0:8]
    return f"0x{sd}"


def filter_xcode_build(s: str) -> str:
    """Return a build hash suitable for use in an Xcode project file.
    """
    s = f"{s}_build"
    sh = hashlib.md5(s.encode('utf-8'))
    return sh.hexdigest().upper()[0:24]


def filter_xcode_copy(s: str) -> str:
    """Return a copyref hash suitable for use in an Xcode project file.
    """
    s = f"{s}_copy"
    sh = hashlib.md5(s.encode('utf-8'))
    return sh.hexdigest().upper()[0:24]


def filter_xcode_fileref(s: str) -> str:
    """Return a fileref hash suitable for use in an Xcode project file.
    """
    s = f"{s}_fileref"
    sh = hashlib.md5(s.encode('utf-8'))
    return sh.hexdigest().upper()[0:24]
