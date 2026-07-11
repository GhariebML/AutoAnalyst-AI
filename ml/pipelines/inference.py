import os
import pickle
import logging
from typing import Any, Dict
import pandas as pd

logger = logging.getLogger(__name__)

class InferencePipeline:
    """Production inference pipeline wrapper with automatic rules fallback."""

    def __init__(self, agent_name: str, fallback_rules: Any = None):
        self.agent_name = agent_name
        self.fallback_rules = fallback_rules
        self.model = self._load_model()

    def _load_model(self) -> Any:
        """Loads serialized model pickle from the local registry."""
        model_path = f"ml/registry/{self.agent_name}_model.pkl"
        
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    model = pickle.load(f)
                logger.info(f"Loaded {self.agent_name} model from local registry.")
                return model
            except Exception as e:
                logger.error(f"Failed to load {self.agent_name} model from {model_path}: {e}")
                
        logger.warning(f"No model found for {self.agent_name}. Falling back to default rules.")
        return None

    def predict(self, input_data: pd.DataFrame) -> Any:
        """Executes model prediction, falling back to static rules if model is missing."""
        if self.model is not None:
            try:
                return self.model.predict(input_data)
            except Exception as e:
                logger.error(f"Inference error in {self.agent_name} model: {e}")
                
        if self.fallback_rules is not None:
            logger.info(f"Using fallback rules for {self.agent_name}.")
            return self.fallback_rules(input_data)
            
        raise RuntimeError(f"No active model or fallback rules configured for {self.agent_name}")

    def predict_proba(self, input_data: pd.DataFrame) -> Any:
        """Returns probability predictions for classification agents."""
        if self.model is not None:
            try:
                if hasattr(self.model, "predict_proba"):
                    return self.model.predict_proba(input_data)
            except Exception as e:
                logger.error(f"Probability inference error in {self.agent_name}: {e}")
                
        # Static fallback representation for probabilities
        if self.model is None and self.fallback_rules is not None:
            return [[0.5, 0.5]]
            
        raise RuntimeError(f"Model predict_proba not supported or missing for {self.agent_name}")
