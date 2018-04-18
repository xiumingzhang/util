"""
General Utility Functions

Xiuming Zhang, MIT CSAIL
April 2018
"""

import sys
from os.path import abspath
import logging
import re
import jsonpickle
import yaml
import logging_colorer # noqa: F401 # pylint: disable=unused-import

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)


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
    thisfunc = thisfile + '->print_attrs()'

    if isinstance(excerpts, str):
        excerpts = [excerpts]
    assert isinstance(excerpts, list) or excerpts is None

    try:
        serialized = jsonpickle.encode(obj, max_depth=max_recursion_depth)
    except RecursionError as e:
        logging.error("%s: %s: %s! Please specify a limit to retry",
                      thisfunc, 'RecursionError', str(e))
        sys.exit(1)

    if excerpts is None:
        # Print all attributes
        logging.info("%s: All attributes:", thisfunc)
        print(yaml.dump(yaml.load(serialized), indent=4))
    else:
        for x in excerpts:
            # For each attribute of interest, print excerpts containing it
            logging.info("%s: Excerpt(s) containing '%s':", thisfunc, x)

            mis = [m.start() for m in re.finditer(x, serialized)]
            if len(mis) == 0:
                logging.info(("%s: No matches! "
                              "Retry maybe with deeper recursion"), thisfunc)
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
