"""Convert between f-string and str.format"""

#pylint: disable=line-too-long
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring
#pylint: disable=no-else-return

import sys
import ast
from typing import Optional, Dict
import argparse
import json

from utilities import node_is_multiline, is_fstring, is_string_format, is_string, get_string_type


def node_contains_cursor(node: ast.AST, cursor_line: int, cursor_col: int) -> bool:
    cursor_offset = cursor_col
    cursor_line += 1

    if node_is_multiline(node):
        if cursor_line == node.lineno and cursor_offset >= node.col_offset:
            return True

        if cursor_line == node.end_lineno and cursor_offset <= node.end_col_offset:
            return True

        if node.lineno < cursor_line < node.end_lineno:
            return True

        return False

    else:
        if cursor_line == node.lineno and node.col_offset <= cursor_offset <= node.end_col_offset:
            return True

        return False

def string_position_descriptor(node: ast.AST) -> Dict[str, Dict[str, int]]:
    if node_is_multiline(node):
        return {
            "type": get_string_type(node),
            "start": {"line": node.lineno-1, "character": node.col_offset},
            "end": {"line": node.end_lineno-1, "character": node.end_col_offset}
        }
    else:
        return {
            "type": get_string_type(node),
            "start": {"line": node.lineno-1, "character": node.col_offset},
            "end": {"line": node.lineno-1, "character": node.end_col_offset}
        }

def string_finder(src: str, cursor_line: int, cursor_col: int) -> Optional[Dict[str, Dict[str, int]]]:
    tree = ast.parse(src, mode='exec')

    for node in ast.walk(tree):
        if is_fstring(node) and node_contains_cursor(node, cursor_line, cursor_col):
            break
        if is_string_format(node) and node_contains_cursor(node, cursor_line, cursor_col):
            break
        if is_string(node) and node_contains_cursor(node, cursor_line, cursor_col):
            break
    else:
        return None

    return string_position_descriptor(node)


def main():
    parser = argparse.ArgumentParser(description="Find strings in Python source code")
    parser.add_argument("line", type=int, help="Cursor line number (0-based)")
    parser.add_argument("col", type=int, help="Cursor column number (0-based)")

    args = parser.parse_args()

    buffer = sys.stdin.buffer.read()
    src = buffer.decode('utf-8')

    result = string_finder(
        src=src,
        cursor_line=args.line,
        cursor_col=args.col
    )

    if result is None:
        sys.stderr.write("No string found at the given cursor position.\n")
        sys.stderr.flush()
        return 1

    sys.stdout.buffer.write(json.dumps(result).encode('utf-8'))
    sys.stdout.flush()

    return 0


if __name__ == "__main__":
    STATUS = main()
    sys.exit(STATUS)
