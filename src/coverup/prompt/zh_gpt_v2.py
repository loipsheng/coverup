import typing as T

from .gpt_v2 import GptV2Prompter
from .prompter import CodeSegment, mk_message
from ..utils import lines_branches_do


class ZhGptV2Prompter(GptV2Prompter):
    """Chinese prompt template for GPT-style models."""

    def initial_prompt(self, segment: CodeSegment) -> T.List[dict]:
        filename = segment.path.relative_to(self.args.src_base_dir)

        return [
            mk_message(f"""
你是一个 Python 测试工程师。
下面的代码片段来自 {filename}，当前测试没有达到完整覆盖率：
运行测试时，{segment.lines_branches_missing_do()} not execute。

请根据下面未覆盖的代码，为其生成 pytest 单元测试。
要求：
1. 测试必须可以直接运行；
2. 使用 assert 验证可观察的结果或状态；
3. 尽量覆盖边界情况，并确保测试确实提升行覆盖率或分支覆盖率；
4. 如有需要，可以调用 get_info 工具函数获取类、函数或方法的额外上下文；
5. 每次生成或修正测试时，都输出完整 Python 测试脚本；
6. 尽量清理测试产生的状态污染，可使用 monkeypatch 或 pytest-mock；
7. 不要输出解释，只输出包含在 ```python 代码块中的代码。

```python
{segment.get_excerpt()}
```
""")
        ]

    def error_prompt(self, segment: CodeSegment, error: str) -> T.List[dict] | None:
        return [mk_message(f"""\
上一次生成的测试运行失败，错误信息如下：

{error}

请修复该 pytest 测试代码。要求：
1. 保留完整可运行的 Python 测试脚本；
2. 修复导致失败的导入、断言、对象构造或环境隔离问题；
3. 如有需要，可以调用 get_info 工具函数获取额外上下文；
4. 不要输出解释，只输出包含在 ```python 代码块中的代码。
""")
        ]

    def missing_coverage_prompt(self, segment: CodeSegment,
                                missing_lines: set, missing_branches: set) -> T.List[dict] | None:
        return [mk_message(f"""\
上一次生成的测试可以运行，但仍未覆盖目标代码：{lines_branches_do(missing_lines, set(), missing_branches)} not execute。

请修改测试，使其覆盖这些缺失的行或分支。不要输出解释，只输出包含在 ```python 代码块中的完整 Python 测试脚本。
如有需要，可以调用 get_info 工具函数获取额外上下文。
""")
        ]
