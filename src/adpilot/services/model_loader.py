import os
import joblib
import threading
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ModelLoader:
    """Thread-safe model caching loader for AdPilot ML models."""

    _instance: Optional[ModelLoader] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelLoader, cls).__new__(cls)
                    cls._instance._models = {}
        return cls._instance

    def load_model(self, path: str) -> Optional[Any]:
        """Load and cache a model file from path. Returns None if missing."""
        if path in self._models:
            return self._models[path]

        with self._lock:
            if path in self._models:
                return self._models[path]

            if not os.path.exists(path):
                logger.warning("Model file not found at: %s. Using fallback mode.", path)
                self._models[path] = None
                return None

            try:
                model = joblib.load(path)
                self._models[path] = model
                logger.info("Successfully loaded model from: %s", path)
                return model
            except Exception as e:
                logger.error("Failed to load model from %s: %s", path, str(e))
                self._models[path] = None
                return None
