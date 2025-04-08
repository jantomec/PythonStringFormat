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
from string_finder import *
from utilities import *


def parse_fstring_subnode_to_string_format(recursion_depth: int, node: ast.JoinedStr, n_keys: int, args: Optional[List[ast.AST]] = None, keywords: Optional[List[ast.keyword]] = None, as_kwargs: bool = True) -> str:  # pylint: disable=too-many-arguments, too-many-positional-arguments
    if recursion_depth >= 2:
        raise PythonStringConverterRecursionError("Python permits only two levels of recursion on string format")

    string = ""
    n_digits = len(str(n_keys))

    for value in node.values:
        if isinstance(value, ast.Constant):
            string += value.value.replace('{', '{{').replace('}', '}}')

        else:
            string += "{"

            if as_kwargs:
                key = f"key{len(keywords)+1:0{n_digits}}"
                keywords.append(ast.keyword(key, value.value))
                string += str(key)
            else:
                args.append(value.value)

            if value.conversion == 115:
                string += "!s"
            elif value.conversion == 114:
                string += "!r"
            elif value.conversion == 97:
                string += "!a"

            if value.format_spec is not None:
                string += ":"
                string += parse_fstring_subnode_to_string_format(
                    recursion_depth=recursion_depth+1,
                    node=value.format_spec,
                    n_keys=n_keys,
                    args=args,
                    keywords=keywords,
                    as_kwargs=as_kwargs
                )

            string += "}"

    return string

def convert_fstring_to_string_format(node: ast.JoinedStr, as_kwargs: bool = True) -> ast.Call:
    args = []
    keywords = []
    n_keys = len([value for value in node.values if not isinstance(value, ast.Constant)])
    string = parse_fstring_subnode_to_string_format(recursion_depth=0, node=node, n_keys=n_keys, args=args, keywords=keywords, as_kwargs=as_kwargs)

    return ast.Call(
        func=ast.Attribute(
            value=ast.Constant(value=string),
            attr='format',
            ctx=ast.Load()
        ),
        args=args,
        keywords=keywords
    )

STRING_DELIMITERS = ['"', "'"]
CONVERSION_TABLE = {'s': 115, 'r': 114, 'a': 97}

def parse_string_format_to_fstring(string: str, args: Iterator[List[ast.AST]], keywords: Dict[str, ast.AST]) -> Optional[ast.JoinedStr]:
    # - Double brackets in any direction are ignored in the string but not
    # within the argument, that is within the brackets (unless they are quoted
    # in which case anything is ignored).
    # - This function returns a list of tuples where the first value dictates
    # whether the element is an argument (True) or simple constant string
    # (False).
    # - str.format allows two levels of recursion (curly braces within curly
    # braces).

    string_iterator = iter(string)

    values = []
    current_string = ""

    is_open = 0
    substring_delimiter = None
    close_brace_count = 0

    try:
        while True:
            character = next(string_iterator)

            if character in STRING_DELIMITERS:
                if substring_delimiter is None:
                    substring_delimiter = character
                elif substring_delimiter == character:
                    substring_delimiter = None

            open_brace_count = 0
            while substring_delimiter is None and character == '{':
                character = next(string_iterator)
                open_brace_count += 1

            current_string += '{' * (open_brace_count // 2)

            if open_brace_count % 2 == 1:
                if is_open == 0:
                    values.append(ast.Constant(value=current_string))
                    current_string = ""
                else:
                    current_string += '{'

                is_open += 1

            if substring_delimiter is None and character == '}' and is_open > 0:
                if is_open == 1:
                    if ':' in current_string:
                        keyword, format_spec = current_string.split(':')
                    else:
                        keyword = current_string
                        format_spec = ''

                    if '!' in keyword:
                        keyword, conversion = keyword.split('!')
                        conversion = CONVERSION_TABLE[conversion]
                    else:
                        conversion = -1

                    value = keywords.get(keyword)
                    if value is None:
                        value = next(args)

                    values.append(
                        ast.FormattedValue(
                            value=value,
                            conversion=conversion,
                            format_spec=parse_string_format_to_fstring(string=format_spec, args=args, keywords=keywords)
                        )
                    )
                    current_string = ""

                else:
                    current_string += character

                is_open -= 1

            elif substring_delimiter is None and character == '}' and is_open == 0:
                close_brace_count += 1
                if close_brace_count == 2:
                    close_brace_count = 0
                    current_string += character

            else:
                current_string += character

    except StopIteration:
        if len(current_string) > 0:
            values.append(ast.Constant(value=current_string))

    if len(values) == 0:
        return None
    else:
        return ast.JoinedStr(values=values)

def convert_string_format_to_fstring(node: ast.Call) -> ast.JoinedStr:
    string = node.func.value.value
    args = iter(node.args)
    keywords = {key_value.arg: key_value.value for key_value in node.keywords}
    return parse_string_format_to_fstring(string=string, args=args, keywords=keywords)

def string_format_node_to_string(node: ast.Call, original_delimiter: str) -> str:
    node = replace_character_in_node(node, '\n', NEWLINE_CHARACTER)
    string = ast.unparse(node)
    string = string.replace(NEWLINE_CHARACTER, '\n')
    new_delimiter = get_string_delimiter(string=string)
    string_part, format_part = string.split(new_delimiter + ".format(")
    string_part = original_delimiter + string_part[len(new_delimiter):]
    return string_part + original_delimiter + ".format(" + format_part

def fstring_node_to_string(node: ast.JoinedStr, original_delimiter: str) -> str:
    node = replace_character_in_node(node, '\n', NEWLINE_CHARACTER)
    string = ast.unparse(node)
    string = string.replace(NEWLINE_CHARACTER, '\n')
    new_delimiter = get_string_delimiter(string=string)
    return 'f' + original_delimiter + string[len(new_delimiter)+1:-len(new_delimiter)] + original_delimiter



def replace_node(src: str, original_node: ast.AST, new_node: ast.AST) -> str:
    lines = src.splitlines()

    if node_is_multiline(original_node):
        start_line = lines[original_node.lineno - 1]
        end_line = lines[original_node.end_lineno - 1]
        before_replacement = start_line[:original_node.col_offset]
        after_replacement = end_line[original_node.end_col_offset:]

        original_delimiter = get_string_delimiter(string=start_line, offset=original_node.col_offset)

        if isinstance(original_node, ast.JoinedStr):
            replacement = string_format_node_to_string(node=new_node, original_delimiter=original_delimiter)
        else:
            replacement = fstring_node_to_string(node=new_node, original_delimiter=original_delimiter)

        new_lines = replacement.splitlines()

        new_lines[0] = before_replacement + new_lines[0]
        new_lines[-1] = new_lines[-1] + after_replacement

        lines = lines[:original_node.lineno-1] + new_lines + lines[original_node.end_lineno:]

    else:
        line = lines[original_node.lineno - 1]
        before_replacement = line[:original_node.col_offset]
        after_replacement = line[original_node.end_col_offset:]

        original_delimiter = get_string_delimiter(string=line, offset=original_node.col_offset)

        if isinstance(original_node, ast.JoinedStr):
            replacement = string_format_node_to_string(node=new_node, original_delimiter=original_delimiter)
        else:
            replacement = fstring_node_to_string(node=new_node, original_delimiter=original_delimiter)

        new_line = before_replacement + replacement + after_replacement
        lines[original_node.lineno - 1] = new_line


    return '\n'.join(lines)

def converter(src: str, cursor_line: int, cursor_col: int, conversion: int) -> str:
    tree = ast.parse(src, mode='exec')

    if conversion == 1:
        for node in ast.walk(tree):
            if is_fstring(node) and node_contains_cursor(node, cursor_line, cursor_col):
                fstring = node
                string_format = convert_fstring_to_string_format(fstring, as_kwargs=False)
                return replace_node(src=src, original_node=fstring, new_node=string_format)

    elif conversion == 2:
        for node in ast.walk(tree):
            if is_fstring(node) and node_contains_cursor(node, cursor_line, cursor_col):
                fstring = node
                string_format = convert_fstring_to_string_format(node)
                return replace_node(src=src, original_node=fstring, new_node=string_format)

    elif conversion == 3:
        for node in ast.walk(tree):
            if is_string_format(node) and node_contains_cursor(node, cursor_line, cursor_col):
                string_format = node
                fstring = convert_string_format_to_fstring(string_format)
                return replace_node(src=src, original_node=string_format, new_node=fstring)

    else:
        raise ValueError(f"Unexpected conversion value: {conversion}")

    return src



def main():

    parser = argparse.ArgumentParser(description="Convert between f-string and str.format")
    parser.add_argument("line", type=int, help="Cursor line number (1-based)")
    parser.add_argument("col", type=int, help="Cursor column number (1-based)")
    parser.add_argument("conversion", type=int, choices=[1, 2, 3], help="Conversion type: 1 (f-string to str.format, no kwargs), 2 (f-string to str.format, with kwargs), 3 (str.format to f-string)")

    args = parser.parse_args()

    buffer = sys.stdin.buffer.read()
    src = buffer.decode('utf-8')

    result = converter(
        src=src,
        cursor_line=args.line,
        cursor_col=args.col,
        conversion=args.conversion
    )

    sys.stdout.buffer.write(result.encode('utf-8'))
    sys.stdout.flush()

    return 0


if __name__ == "__main__":
    main()
