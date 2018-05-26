import logging
import logging_colorer # noqa: F401 # pylint: disable=unused-import


def create_logger(file_abspath, level=logging.INFO):
    logging.basicConfig(level=level)
    logger = logging.getLogger()
    folder_names = file_abspath.split('/')
    thisfile = '/'.join(
        folder_names[
            folder_names.index('xiuminglib'):
        ]
    )
    return logger, thisfile
