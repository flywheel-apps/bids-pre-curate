"""Given string, return something safe to use as a file name."""

import logging
import re
import sys


log = logging.getLogger(__name__)


def make_file_name_safe(input_basename, replace_str="",allows=r'._-'):
    """Remove non-safe characters from a filename and return a filename with 
        these characters replaced with replace_str.

    :param input_basename: the input basename of the file to be replaced
    :type input_basename: str
    :param replace_str: the string with which to replace the unsafe characters
    :type   replace_str: str
    :return: output_basename, a safe
    :rtype: str
    """
    # Compile the user given regex.  Hyphen needs to not be between characters
    #   otherwise it will be taken as a range, we need it to be taken literally
    #   so we add it at the end if it is in the allows string.
    regex = r"[^A-Za-z0-9"
    hyphen_in = '-' in allows
    for char in allows:
        if hyphen_in and char == '-':
            continue
        regex += char
    regex += r"-]+" if hyphen_in else r"]+"
    try:
        safe_patt = re.compile(regex)
    except re.error:
        log.exception(f"Configuration value allows ({allows}) could not be processed. Exiting")
        sys.exit(1)
    # if the replacement is not a string or not safe, set replace_str to x
    if not isinstance(replace_str, str) or safe_patt.match(replace_str):
        log.warning("{} is not a safe string, removing instead".format(replace_str))
        replace_str = ""

    # Replace non-alphanumeric (or underscore) characters with replace_str
    safe_output_basename = re.sub(safe_patt, replace_str, input_basename)

    if safe_output_basename.startswith("."):
        safe_output_basename = safe_output_basename[1:]

    log.debug('"' + input_basename + '" -> "' + safe_output_basename + '"')

    return safe_output_basename
