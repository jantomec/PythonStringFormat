#pylint: disable=line-too-long
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring
#pylint: disable=no-else-return

import ast


def all_characters_same(s: str) -> bool:
    return len(set(s)) == 1

def node_is_multiline(node: ast.AST) -> bool:
    return hasattr(node, 'end_lineno') and node.end_lineno > node.lineno

def get_string_delimiter(string: str, offset: int = 0) -> str:
    if string[offset] == 'f':
        if all_characters_same(string[offset+1:offset+4]):
            return string[offset+1:offset+4]
        else:
            return string[offset+1]
    else:
        if all_characters_same(string[offset:offset+3]):
            return string[offset:offset+3]
        else:
            return string[offset]

def is_string(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)

def is_string_format(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format" and isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str)

def is_fstring(node: ast.AST) -> bool:
    return isinstance(node, ast.JoinedStr)

def get_string_type(node: ast.AST) -> str:
    if is_fstring(node):
        return "f-string"

    elif is_string_format(node):
        if len(node.keywords) == 0:
            return "str.format(args)"
        elif len(node.args) == 0:
            return "str.format(keywords)"
        else:
            return "str.format(args, keywords)"

    elif is_string(node):
        return "str"
    else:
        return "unknown"

def replace_character_in_node(node: ast.AST, old_character: str, new_character: str) -> ast.AST:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            node.value = node.value.replace(old_character, new_character)

    for _, value in ast.iter_fields(node):
        if isinstance(value, ast.AST):
            replace_character_in_node(value, old_character, new_character)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    replace_character_in_node(item, old_character, new_character)

    return node
