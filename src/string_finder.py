"""Convert between f-string and str.format"""

#pylint: disable=line-too-long
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring
#pylint: disable=no-else-return

import sys
import ast
from typing import List, Dict, Iterator, Optional
import argparse

from error import PythonStringConverterRecursionError
from config import NEWLINE_CHARACTER
from utilities import *


def node_contains_cursor(node: ast.AST, cursor_line: int, cursor_col: int) -> bool:
    cursor_offset = cursor_col

    if node_is_multiline(node):
        if cursor_line == node.lineno and cursor_offset > node.col_offset:
            return True

        if cursor_line == node.end_lineno and cursor_offset < node.end_col_offset:
            return True

        if node.lineno < cursor_line < node.end_lineno:
            return True

        return False

    else:
        if cursor_line == node.lineno and node.col_offset < cursor_offset < node.end_col_offset:
            return True

        return False
