from pathlib import Path
from coverup import coverup
import pytest
import argparse

def test_clean_error_failure():
    error = """
F                                                                        [100%]
=================================== FAILURES ===================================
_____________ test_find_package_path_namespace_package_first_path ______________

    def test_find_package_path_namespace_package_first_path():
        # Create a dummy namespace package
        os.makedirs('namespace_package/submodule', exist_ok=True)
        open('namespace_package/__init__.py', 'a').close()
        open('namespace_package/submodule/__init__.py', 'a').close()
    
        # Add the current directory to sys.path
        import sys
        sys.path.append(os.getcwd())
    
        # Test the function
>       assert _find_package_path('namespace_package.submodule') == os.getcwd() + '/namespace_package'
E       AssertionError: assert '/Users/juan/tmp/flask' == '/Users/juan/...space_package'
E         - /Users/juan/tmp/flask/namespace_package
E         + /Users/juan/tmp/flask

tests/coverup_tmp_k076ps1h.py:19: AssertionError
=========================== short test summary info ============================
FAILED tests/coverup_tmp_k076ps1h.py::test_find_package_path_namespace_package_first_path
"""

    assert coverup.clean_error(error) == """
    def test_find_package_path_namespace_package_first_path():
        # Create a dummy namespace package
        os.makedirs('namespace_package/submodule', exist_ok=True)
        open('namespace_package/__init__.py', 'a').close()
        open('namespace_package/submodule/__init__.py', 'a').close()
    
        # Add the current directory to sys.path
        import sys
        sys.path.append(os.getcwd())
    
        # Test the function
>       assert _find_package_path('namespace_package.submodule') == os.getcwd() + '/namespace_package'
E       AssertionError: assert '/Users/juan/tmp/flask' == '/Users/juan/...space_package'
E         - /Users/juan/tmp/flask/namespace_package
E         + /Users/juan/tmp/flask

tests/coverup_tmp_k076ps1h.py:19: AssertionError
""".lstrip("\n")


def test_clean_error_error():
    error = """
==================================== ERRORS ====================================
________________ ERROR collecting tests/coverup_tmp_dkd55qhh.py ________________
ImportError while importing test module '/Users/juan/tmp/flask/tests/coverup_tmp_dkd55qhh.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
../../project/slipcover2/src/slipcover/importer.py:162: in exec_wrapper
    exec(obj, g)
tests/coverup_tmp_dkd55qhh.py:4: in <module>
    from flask.json import JSONProvider
E   ImportError: cannot import name 'JSONProvider' from 'flask.json' (/Users/juan/tmp/flask/src/flask/json/__init__.py)
=========================== short test summary info ============================
ERROR tests/coverup_tmp_dkd55qhh.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
"""
    assert coverup.clean_error(error) == """
ImportError while importing test module '/Users/juan/tmp/flask/tests/coverup_tmp_dkd55qhh.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
../../project/slipcover2/src/slipcover/importer.py:162: in exec_wrapper
    exec(obj, g)
tests/coverup_tmp_dkd55qhh.py:4: in <module>
    from flask.json import JSONProvider
E   ImportError: cannot import name 'JSONProvider' from 'flask.json' (/Users/juan/tmp/flask/src/flask/json/__init__.py)
""".lstrip("\n")


def test_find_imports():
    assert ['abc', 'bar', 'baz', 'cba', 'foo'] == sorted(coverup.find_imports("""\
import foo, bar.baz
from baz.zab import a, b, c
from ..xy import yz         # relative, package likely present
from . import blah          # relative, package likely present
import __main__

def foo_func():
    import abc
    from cba import xyzzy
"""))

    assert [] == coverup.find_imports("not a Python program")


def test_write_summary_report(tmp_path):
    initial = {"summary": {"percent_covered": 40.0}, "files": {}}
    final = {"summary": {"percent_covered": 52.5}, "files": {}}
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    generated = tests_dir / "test_coverup_1.py"
    generated.write_text("def test_example():\n    assert True\n\ndef helper():\n    pass\n")

    args = argparse.Namespace(
        source_files=[],
        package_dir=tmp_path / "src" / "demo",
        src_base_dir=tmp_path / "src",
        tests_dir=tests_dir,
        model="gpt-4o",
        prompt="gpt-v2",
        prefix="coverup",
        summary_report=tmp_path / "reports" / "summary.md",
    )

    coverup.state = coverup.State(initial)
    coverup.state.inc_counter("G")

    coverup.write_summary_report(args, initial, final)

    report = args.summary_report.read_text(encoding="utf-8")
    assert "CoverUp 覆盖率引导测试生成实验摘要" in report
    assert "初始覆盖率：40.0%" in report
    assert "最终覆盖率：52.5%" in report
    assert "覆盖率提升：+12.5 个百分点" in report
    assert "生成测试数量：1" in report
    assert "生成断言数量：1" in report
    assert "========== Coverage Report ==========" in report
    assert str(generated) in report


def test_count_test_functions(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    generated = tests_dir / "test_coverup_2.py"
    generated.write_text("""\
def test_one():
    assert True

async def test_two():
    assert True

def helper():
    pass
""")
    broken = tests_dir / "test_coverup_3.py"
    broken.write_text("def test_broken(:\n")

    assert coverup.count_test_functions([generated, broken]) == 2
    assert coverup.count_assertions([generated, broken]) == 2


def test_analyze_test_quality():
    quality = coverup.analyze_test_quality("""\
import pytest

def test_ok():
    assert 1 + 1 == 2

def test_error():
    with pytest.raises(ValueError):
        raise ValueError("x")

if __name__ == "__main__":
    pytest.main()
""")

    assert quality == {
        "syntax_error": None,
        "test_functions": 2,
        "assertions": 2,
        "pytest_main_calls": 1,
    }


def test_test_quality_issues():
    quality = {
        "syntax_error": None,
        "test_functions": 0,
        "assertions": 0,
        "pytest_main_calls": 1,
    }

    issues = coverup.test_quality_issues(quality, min_assertions=1)

    assert any("test_" in issue for issue in issues)
    assert any("断言数量不足" in issue for issue in issues)
    assert any("pytest.main" in issue for issue in issues)

    prompt = coverup.quality_feedback_prompt(issues, quality)
    assert "静态质量检查" in prompt
    assert "不要调用 pytest.main()" in prompt


def test_coverage_delta_lines(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    generated = tests_dir / "test_generated_calculator.py"
    generated.write_text("""\
def test_add():
    assert True

def test_subtract():
    assert True

def test_multiply():
    assert True

def test_divide():
    assert True

def test_zero_division():
    assert True

def test_boundary():
    assert True
""")

    args = argparse.Namespace(
        source_files=[],
        tests_dir=tests_dir,
        prefix="generated",
        project_name="calculator_project",
    )
    initial = {"summary": {"percent_covered": 42.31}, "files": {}}
    final = {"summary": {"percent_covered": 68.75}, "files": {}}

    assert coverup.coverage_delta_lines(args, initial, final) == [
        "========== Coverage Report ==========",
        "项目名称：calculator_project",
        "原始覆盖率：42.31%",
        "生成测试后覆盖率：68.75%",
        "覆盖率提升：26.44%",
        f"新增测试文件：{generated}",
        "生成测试数量：6",
        "生成断言数量：6",
        "运行状态：全部通过",
        "====================================",
    ]


def test_missing_imports():
    assert not coverup.missing_imports(['ast', 'dis', 'sys'])
    assert not coverup.missing_imports([])
    assert coverup.missing_imports(['sys', 'idontexist'])


def test_extract_python():
    assert "foo()\n\nbar()\n" == coverup.extract_python("""\
```python
foo()

bar()
```
""")

    assert "foo()\n\nbar()\n" == coverup.extract_python("""\
```python
foo()

bar()
```""")

    assert "foo()\n\nbar()\n" == coverup.extract_python("""\
```python
foo()

bar()
""")


@pytest.mark.parametrize("pythonpath_exists", [True, False])
def test_add_to_pythonpath(pythonpath_exists):
    import sys, os
    saved_environ = dict(os.environ.items())
    saved_syspath = list(sys.path)

    try:
        if pythonpath_exists:
            os.environ['PYTHONPATH'] = 'foo:bar'
        elif 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']

        coverup.add_to_pythonpath(Path("baz"))

        if pythonpath_exists:
            assert os.environ['PYTHONPATH'] == 'baz:foo:bar'
        else:
            assert os.environ['PYTHONPATH'] == 'baz'

        assert sys.path == ['baz'] + saved_syspath

    finally:
        os.environ = saved_environ
        sys.path = saved_syspath
