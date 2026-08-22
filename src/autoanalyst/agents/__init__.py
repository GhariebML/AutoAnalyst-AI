"""Agent layer for AutoAnalyst AI.

The agent layer wraps the deterministic analysis modules as LangChain
tools so a LangGraph workflow (M2+) can orchestrate them. Tools are pure
functions over ``src/autoanalyst`` modules and never call an LLM.
"""
