"""Custom exception hierarchy for AdPilot.

Collecting custom errors in a single module keeps traceback handling tidy and
provides clear semantic meaning for callers.
"""

from __future__ import annotations


class AdPilotError(Exception):
    """Base‑class for all AdPilot‑specific errors."""

    pass


class AgentOutputError(AdPilotError):
    """Raised when an agent produces data that fails ``output_model`` validation."""

    pass


class AgentInputValidationError(AdPilotError):
    """Raised when the supplied input data does not match ``input_model``."""

    pass


class AgentExecutionError(AdPilotError):
    """Raised while an agent is executing for an unexpected reason."""

    pass


class SchemaValidationError(AdPilotError):
    """Raised when invalid config or schema data is detected."""

    pass


class ConfigurationError(AdPilotError):
    """Raised on mis‑configuration of an agent/environment."""

    pass
