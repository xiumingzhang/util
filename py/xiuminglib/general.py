"""
General Utility Functions

Xiuming Zhang, MIT CSAIL
April 2018
"""

import sys
from os.path import abspath, join
import re
from glob import glob

import config
logger, thisfile = config.create_logger(abspath(__file__))


def print_attrs(obj, excerpts=None, excerpt_win_size=60, max_recursion_depth=None):
    """
    Print all attributes, recursively, of an object

    Args:
        obj: Object in which we search for the attribute
            Any object
        excerpts: Print only excerpts containing certain attributes
            A single string or a list thereof
            Optional; defaults to None (print all)
        excerpt_win_size: How many characters get printed around a match
            Positive integer
            Optional; defaults to 60
        max_recursion_depth: Maximum recursion depth
            Positive integer
            Optional; defaults to None (no limit)
    """
    import jsonpickle
    import yaml

    logger.name = thisfile + '->print_attrs()'

    if isinstance(excerpts, str):
        excerpts = [excerpts]
    assert isinstance(excerpts, list) or excerpts is None

    try:
        serialized = jsonpickle.encode(obj, max_depth=max_recursion_depth)
    except RecursionError as e:
        logger.error("RecursionError: %s! Please specify a limit to retry",
                     str(e))
        sys.exit(1)

    if excerpts is None:
        # Print all attributes
        logger.info("All attributes:")
        print(yaml.dump(yaml.load(serialized), indent=4))
    else:
        for x in excerpts:
            # For each attribute of interest, print excerpts containing it
            logger.info("Excerpt(s) containing '%s':", x)

            mis = [m.start() for m in re.finditer(x, serialized)]
            if not mis:
                logger.info("%s: No matches! Retry maybe with deeper recursion")
            else:
                for mii, mi in enumerate(mis):
                    # For each excerpt
                    m_start = mi - excerpt_win_size // 2
                    m_end = mi + excerpt_win_size // 2
                    print(
                        "Match %d (index: %d): ...%s\033[0;31m%s\033[00m%s..." % (
                            mii,
                            mi,
                            serialized[m_start:mi],
                            serialized[mi:(mi + len(x))],
                            serialized[(mi + len(x)):m_end],
                        )
                    )


def sortglob(directory, filename, exts, ext_ignore_case=False):
    """
    Glob and then sort according to the pattern ending in multiple extensions

    Args:
        directory: Directory to glob
            String; e.g., '/path/to/'
        filename: Filename pattern excluding extensions
            String; e.g., 'batch000_*'
        exts: Extensions of interest
            Set of strings; e.g., ('.png', '.PNG')
        ext_ignore_case: Whether to ignore case for extensions
            Boolean
            Optional; defaults to False
    """
    ext_list = []
    for ext in exts:
        if not ext.startswith('.'):
            ext = '.' + ext
        if ext_ignore_case:
            ext_list += [ext.lower(), ext.upper()]
        else:
            ext_list.append(ext)
    files = []
    for ext in ext_list:
        files += glob(join(directory, filename + ext))
    return sorted(files)
