# pylint: disable=missing-docstring
# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=missing-module-docstring

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from converter import converter  # pylint: disable=import-error


def test_cursor_in_fstring() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print("Hello, {{}}, {!r:>10}! sin{{{}}} = {:.{}}".format(name, a, math.sin(a), 3))"""

    actual = converter(src, cursor_line=5, cursor_col=16, conversion_target=1)

    assert expected == actual

def test_cursor_in_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")"""

    actual = converter(src, cursor_line=4, cursor_col=16, conversion_target=3)

    assert expected == actual

def test_cursor_left_edge_fstring() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print("Hello, {{}}, {!r:>10}! sin{{{}}} = {:.{}}".format(name, a, math.sin(a), 3))"""

    actual = converter(src, cursor_line=5, cursor_col=8, conversion_target=1)

    assert expected == actual

def test_cursor_left_edge_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")"""

    actual = converter(src, cursor_line=4, cursor_col=8, conversion_target=3)

    assert expected == actual

def test_cursor_over_left_edge() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = src

    actual = converter(src, cursor_line=5, cursor_col=7, conversion_target=1)

    assert expected == actual

def test_cursor_over_left_edge_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = src

    actual = converter(src, cursor_line=4, cursor_col=7, conversion_target=3)

    assert expected == actual

def test_cursor_right_edge_fstring() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print("Hello, {{}}, {!r:>10}! sin{{{}}} = {:.{}}".format(name, a, math.sin(a), 3))"""

    actual = converter(src, cursor_line=5, cursor_col=67, conversion_target=1)

    assert expected == actual

def test_cursor_right_edge_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")"""

    actual = converter(src, cursor_line=4, cursor_col=87, conversion_target=3)

    assert expected == actual

def test_cursor_over_right_edge() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = src

    actual = converter(src, cursor_line=5, cursor_col=68, conversion_target=1)

    assert expected == actual

def test_cursor_over_right_edge_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = src

    actual = converter(src, cursor_line=4, cursor_col=88, conversion_target=3)

    assert expected == actual

def test_string_delimiter_single_quotation_mark_fstring() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f'Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}')
"""
    expected = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print('Hello, {{}}, {!r:>10}! sin{{{}}} = {:.{}}'.format(name, a, math.sin(a), 3))"""

    actual = converter(src, cursor_line=5, cursor_col=67, conversion_target=1)

    assert expected == actual

def test_string_delimiter_single_quotation_mark_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print('Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}'.format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print(f'Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}')
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")"""

    actual = converter(src, cursor_line=4, cursor_col=87, conversion_target=3)

    assert expected == actual

def test_string_delimiter_3single_quotation_marks_fstring() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f'''Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}''')
"""
    expected = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print('''Hello, {{}}, {!r:>10}! sin{{{}}} = {:.{}}'''.format(name, a, math.sin(a), 3))"""

    actual = converter(src, cursor_line=5, cursor_col=67, conversion_target=1)

    assert expected == actual

def test_string_delimiter_3single_quotation_marks_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print('''Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}'''.format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print(f'''Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}''')
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")"""

    actual = converter(src, cursor_line=4, cursor_col=87, conversion_target=3)

    assert expected == actual

def test_string_delimiter_3single_quotation_marks_multiline_fstring() -> bool:
    src = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f'''Hello,
{{}},
{name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}''')
"""
    expected = """import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print('''Hello,
{{}},
{!r:>10}! sin{{{}}} = {:.{}}'''.format(name, a, math.sin(a), 3))"""

    actual = converter(src, cursor_line=5, cursor_col=13, conversion_target=1)

    assert expected == actual

def test_string_delimiter_3single_quotation_marks_multiline_string_format() -> bool:
    src = """import math
a = 0.0
name = "world"
print('''Hello,
{{}},
{n!r:>10}! sin{{{a}}} = {:.{}}'''.format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
"""
    expected = """import math
a = 0.0
name = "world"
print(f'''Hello,
{{}},
{name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}''')
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")"""

    actual = converter(src, cursor_line=4, cursor_col=13, conversion_target=3)

    assert expected == actual

def test_string_delimiter_3double_quotation_marks_fstring() -> bool:
    src = '''import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print(f"""Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}""")
'''
    expected = '''import math
a = 0.0
name = "world"
print("Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}".format(math.sin(a), 3, n=name, a=a))
print("""Hello, {{}}, {!r:>10}! sin{{{}}} = {:.{}}""".format(name, a, math.sin(a), 3))'''

    actual = converter(src, cursor_line=5, cursor_col=67, conversion_target=1)

    assert expected == actual

def test_string_delimiter_3double_quotation_marks_string_format() -> bool:
    src = '''import math
a = 0.0
name = "world"
print("""Hello, {{}}, {n!r:>10}! sin{{{a}}} = {:.{}}""".format(math.sin(a), 3, n=name, a=a))
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")
'''
    expected = '''import math
a = 0.0
name = "world"
print(f"""Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}""")
print(f"Hello, {{}}, {name!r:>10}! sin{{{a}}} = {math.sin(a):.{3}}")'''

    actual = converter(src, cursor_line=4, cursor_col=13, conversion_target=3)

    assert expected == actual

def test_braces_inside_fstring() -> bool:
    src = '''f"Hello, {'world{}'}"'''
    expected = '''"Hello, {}".format('world{}')'''

    actual = converter(src, cursor_line=1, cursor_col=5, conversion_target=1)

    assert expected == actual

def test_braces_inside_string_format() -> bool:
    src = '''"Hello, {}".format('world{}')'''
    expected = '''f"Hello, {'world{}'}"'''

    actual = converter(src, cursor_line=1, cursor_col=5, conversion_target=3)

    assert expected == actual
