"""Prompt templates for the optional LLM narration layer.

Prompts are plain strings with named placeholders so they stay inspectable
and testable. Every consumer must render them with truncated payloads (see
``narrator._truncate``) to bound token usage and avoid leaking full datasets.
"""

INSIGHTS_PROMPT = """You are a senior data analyst. Given the dataset profile
and model artifacts below, write the {max_insights} most important findings.

Rules:
- One finding per line, starting with "- ".
- Be specific: reference numbers from the profile or metrics.
- No preamble, no closing remarks, no markdown headers.

Dataset profile (JSON):
{profile_json}

Model results (JSON, may be empty):
{model_json}

Evaluation metrics (JSON, may be empty):
{evaluation_json}
"""

ADVISOR_PROMPT = """You are an ML advisor reviewing a baseline model result.
In at most 3 sentences, advise the analyst on the single most valuable next
improvement (e.g., different estimator, feature work, more data). Reference
the concrete metrics below. Plain prose only.

Model results (JSON):
{model_json}

Evaluation metrics (JSON):
{evaluation_json}
"""

SUMMARY_PROMPT = """You are writing an executive summary for a data analysis
report. In at most 4 sentences, summarize what was analyzed and what was
found, using only the facts below. Plain prose only.

Dataset profile (JSON):
{profile_json}

Key insights:
{insights_block}
"""

ANSWER_PROMPT = """You are answering an analyst's questions about a completed
AutoAnalyst run. Answer concisely using ONLY the facts below. If the facts do
not contain the answer, say what you would need.

Facts (JSON):
{facts_json}

Question: {question}
"""
