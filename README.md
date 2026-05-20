# AI Column Classification Agent

This project is a single-task AI Agent for database column classification and sensitivity-level judgment.

It reads database column metadata, loads a replaceable classification-rule Excel file, uses an OpenAI-compatible LLM API to map each column to an allowed classification path, validates the result against the rule Excel, and generates a standardized Markdown report.

## Input Files

### Column metadata

CSV or Excel file with required columns:

| Column | Meaning |
|---|---|
| `table_name` | Database table name |
| `column_name` | Database column name |
| `column_type` | Database column type |
| `column_description` | Business description of the column |

Chinese aliases are also accepted for convenience: `表名`, `字段名`, `字段类型`, `字段描述`, `列名`, `列类型`, `列描述`.

### Rule Excel

The rule Excel uses a fixed template.

Classification sheet required columns:

| Column |
|---|
| `一级分类` |
| `二级分类` |
| `三级分类` |
| `四级分类` |
| `五级分类` |
| `推荐分级` |
| `分类说明` |

Level sheet required columns:

| Column |
|---|
| `安全等级` |
| `等级名称` |
| `共享属性` |
| `开放属性` |

The rule Excel is the authority. The LLM may only choose from candidate `classification_path` values derived from the Excel rules.

## Configuration

Set these environment variables before calling the API:

```bash
export DASHSCOPE_API_KEY="your-api-key"
export OPENAI_BASE_URL="http://mc-llm-api.dev.mchz.com.cn/v1"
export MODEL="qwen-plus"
export TIMEOUT_SECONDS="30"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python agent_demo.py \
  --input data/sample_column_metadata.csv \
  --rules /path/to/分类分级标准.xlsx \
  --output reports/classification_report.md
```

The Agent classifies columns one by one. This keeps the demo flow simple and easy to inspect.

If `DASHSCOPE_API_KEY` is not set, the Agent still loads rules, builds candidates, and generates a Markdown report, but every column is marked as `review_required=true` because no trusted LLM judgment was produced.

## Output

The Markdown report includes:

- total column count
- classified column count
- review-required column count
- security-level summary
- review-required list with candidate paths
- detailed classification table with `classification_path`, `security_level`, `level_name`, `sharing_policy`, `open_policy`, `basis`, `confidence`, and `review_required`

## Evaluate Matching

Create an evaluation CSV with the normal column metadata plus
`expected_classification_path`. A small example is provided at
`data/eval_column_metadata.csv`.

Compare baseline matching with LLM-enhanced match terms:

```bash
.venv/bin/python scripts/evaluate_match_profile.py \
  --input data/eval_column_metadata.csv \
  --rules /path/to/分类分级标准.xlsx \
  --output /private/tmp/match-profile-eval.json
```

This reports `recall@5`, `recall@10`, and `recall@20`, which measure whether
the expected standard classification appears in the candidate list.

To also compare final classification accuracy, call the classifier LLM:

```bash
.venv/bin/python scripts/evaluate_match_profile.py \
  --input data/eval_column_metadata.csv \
  --rules /path/to/分类分级标准.xlsx \
  --include-final \
  --quiet
```

LLM match-profile enhancement is enabled by default for the normal Agent. To
disable it for a faster baseline run:

```bash
ENABLE_LLM_MATCH_PROFILE=0 .venv/bin/python agent_demo.py ...
```

The evaluation script runs both baseline and LLM match-profile modes
automatically.
