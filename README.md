# CoverUp 课程改进版：基于覆盖率反馈的 LLM 单元测试生成工具

本仓库基于开源项目 CoverUp 进行课程复现与二次开发。CoverUp 来源于论文 **CoverUp: Effective High Coverage Test Generation for Python**，其核心思想是先测量 Python 项目的代码覆盖率，再将未覆盖的代码片段、分支信息和上下文提供给大语言模型，由模型生成 `pytest` 单元测试，并通过实际运行结果判断测试是否有效。

本课程项目在保留原有覆盖率引导测试生成流程的基础上，新增了面向实验记录的中文摘要报告功能，便于在课程报告中展示覆盖率变化、生成测试数量和运行统计信息。

## 项目来源

- 原始论文：CoverUp: Effective High Coverage Test Generation for Python
- 原始项目：https://github.com/plasma-umass/coverup
- 本课程仓库：https://github.com/loipsheng/coverup.git
- 主要技术：Python、pytest、SlipCover、LLM、覆盖率分析、自动化测试生成

## 核心功能

CoverUp 的主流程可以概括为以下步骤：

1. 使用 SlipCover 测量现有测试套件的行覆盖率和分支覆盖率。
2. 根据覆盖率结果定位未覆盖的代码片段。
3. 将未覆盖代码、导入信息和相关上下文组织成 Prompt。
4. 调用大语言模型生成新的 `pytest` 测试用例。
5. 自动运行生成的测试，判断其是否通过并提高覆盖率。
6. 对失败测试或未提升覆盖率的测试继续反馈给模型进行修正。
7. 将有效测试保存到测试目录中。

## 本次二次开发内容

本项目新增了 `--summary-report` 参数，用于在测试生成结束后自动输出中文 Markdown 实验摘要。

该报告会记录：

- 实验生成时间
- 源码目录和测试目录
- 使用的模型和 Prompt 模板
- 初始覆盖率
- 最终覆盖率
- 覆盖率提升百分点
- 有效、失败、无效、重试等统计信息
- 当前生成的测试文件列表

该功能主要服务于课程实验复现和项目报告撰写，使工具不仅能生成测试，还能自动沉淀实验结果，提升项目的可解释性和工程可交付性。

除摘要报告外，本课程改进版还增加了几个小型工程增强：

- 新增中文 Prompt 模板 `zh-gpt-v2`，可通过 `--prompt zh-gpt-v2` 启用，使模型按中文指令生成 pytest 测试。
- 新增结构化覆盖率报告，在生成结束后直接打印原始覆盖率、生成测试后覆盖率、提升百分点、新增测试文件、生成测试数量和运行状态。
- 新增 AST 测试数量统计，会自动扫描新增测试文件中以 `test_` 开头的同步/异步测试函数，避免手工填写测试数量。
- 新增生成测试静态质量门禁 `--enforce-test-quality`，在运行 LLM 生成的测试前，先用 AST 检查测试函数数量、断言数量和 `pytest.main()` 调用，避免明显低质量测试进入动态执行阶段。
- 新增失败测试修复一次模式 `--repair-failures-once`，当生成测试运行失败时，会把错误信息反馈给 LLM，请求其修复一次。

## 安装方式

建议使用 Python 3.10 及以上版本。

```bash
python -m pip install -e .
```

如果需要运行测试：

```bash
python -m pip install pytest hypothesis
```

## 基本使用

假设目标项目源码位于 `src/mymod`，测试目录为 `tests`，可以运行：

```bash
coverup --package-dir src/mymod --tests-dir tests
```

如果需要生成中文实验摘要，可以增加：

```bash
coverup --package-dir src/mymod --tests-dir tests --summary-report reports/coverup-summary.md
```

如果希望使用中文 Prompt 模板并开启失败后修复一次，可以运行：

```bash
coverup --package-dir src/mymod --tests-dir tests --project-name calculator_project --prompt zh-gpt-v2 --enforce-test-quality --min-assertions 1 --repair-failures-once --summary-report reports/coverup-summary.md
```

生成后的摘要文件示例字段如下：

```text
========== Coverage Report ==========
项目名称：calculator_project
原始覆盖率：42.31%
生成测试后覆盖率：68.75%
覆盖率提升：26.44%
新增测试文件：tests/test_generated_calculator.py
生成测试数量：6
生成断言数量：6
运行状态：全部通过
====================================
```

## LLM 配置

CoverUp 支持 OpenAI、Anthropic 和 AWS Bedrock 等模型服务。使用 OpenAI 模型时，需要配置环境变量：

```bash
set OPENAI_API_KEY=你的 API Key
```

在 PowerShell 中可以使用：

```powershell
$env:OPENAI_API_KEY="你的 API Key"
```

也可以通过 `--model` 指定模型，例如：

```bash
coverup --package-dir src/mymod --tests-dir tests --model gpt-4o
```

## 运行本仓库测试

```bash
python -m pytest tests/test_utils.py tests/test_coverup.py
```

## 项目特点

- 以覆盖率反馈为核心，而不是单纯让模型凭空生成测试。
- 生成后立即执行测试，过滤无法运行或不能提升覆盖率的结果。
- 支持失败反馈，让模型根据报错信息继续修正。
- 新增中文实验摘要，适合课程报告、复现实验和阶段性结果归档。

## 课程报告说明

本项目不是从零原创实现完整 CoverUp，而是在原开源项目和论文思想基础上进行复现、理解和二次开发。
