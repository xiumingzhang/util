from os import makedirs
from os.path import exists, dirname

def toHTML(table, outPath):
    """
    Generate an HTML table of media from the given 2D list.

    Args:
        table: list of lists.
            Dictionary keys are row or column headers; values are paths to media.
            The first dimension corresponds to row; the second to columns.
        outPath: path to the generated HTML.

    Returns:
        HTMLPath: path to resulting HTML.
    """
    outDir = dirname(outPath)
    if not exists(outDir):
        makedirs(outDir)
    with open(outPath, 'w') as f:
        f.write('<!DOCTYPE HTML>\n<html>\n<body>\n<center>\n<table border=1>\n')
        # Rows
        for rowHeader, rowDict in dict2D.items():
            f.write('\t<tr>\n')
            # Columns
            for colHeader, mediaPath in rowDict.items():
                if mediaPath.endswith('.png') or mediaPath.endswith('.jpg'):
                    pass
                elif mediaPath.endswith('.mp4'):
                    pass
