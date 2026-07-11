import os
import yaml
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    name: str
    algorithm: str
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)

class DataConfig(BaseModel):
    raw_path: str
    processed_path: str
    test_size: float = 0.2
    random_state: int = 42

class EvaluationConfig(BaseModel):
    target_metrics: Dict[str, float] = Field(default_factory=dict)

class AgentMLConfig(BaseModel):
    model: ModelConfig
    data: DataConfig
    evaluation: EvaluationConfig

def load_agent_config(agent_name: str) -> AgentMLConfig:
    """Loads agent configuration from YAML file or falls back to default values."""
    config_path = f"ml/configs/{agent_name}.yaml"
    
    # Defaults
    default_data = {
        "model": {
            "name": f"{agent_name}_model",
            "algorithm": "random_forest" if agent_name in ["strategy", "audience", "research", "recommendation", "fraud", "lead_scoring", "sentiment", "knowledge"] else "random_forest_regressor",
            "hyperparameters": {"n_estimators": 100, "max_depth": 6}
        },
        "data": {
            "raw_path": f"ml/datasets/raw/{agent_name}_data.csv",
            "processed_path": f"ml/datasets/processed/{agent_name}_features.parquet"
        },
        "evaluation": {
            "target_metrics": {"accuracy": 0.8} if agent_name in ["strategy", "audience", "research", "recommendation", "fraud", "lead_scoring", "sentiment", "knowledge"] else {"mae": 5.0}
        }
    }
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f)
            # Merge YAML data with defaults
            if yaml_data:
                for k, v in yaml_data.items():
                    if k in default_data:
                        default_data[k].update(v)
                        
    return AgentMLConfig(**default_data)
