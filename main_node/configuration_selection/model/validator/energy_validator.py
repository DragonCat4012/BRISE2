import pandas as pd
from typing import List, Tuple, Dict

from configuration_selection.model.surrogate.surrogate_abs import Surrogate
from configuration_selection.model.optimizer.random_search import RandomSearch
from configuration_selection.model.validator.validator_abs import Validator


class EnergyValidator(Validator):
    def __init__(self, validator_description: Dict, region: Tuple, objectives: Dict):
        super().__init__(validator_description, region, objectives)
        self.validator_description = validator_description
        optimizer_description = {"Instance": {"RandomSearch": {"SamplingSize": 100}}}
        self._optimizer = RandomSearch(optimizer_description, self.region, self.objectives)

    def validate(self, surrogate: Surrogate, features: pd.DataFrame, labels: pd.DataFrame) -> Tuple[bool, float]:
        is_built = surrogate.create(features, labels)
        
        if not is_built:
            return False, 0 
        
        for ct, parameters in self._optimizer.mapping_config_transformer_parameter.items():
            relevant_feature_names = [p.name for p in parameters]
            
            if hasattr(ct, 'fit') and all(name in features.columns for name in relevant_feature_names):
                transformation_data = features[relevant_feature_names]
                ct.fit(transformation_data)

        results = self._optimizer.optimize(surrogate)

        if all(results["energy"] > 0):
            return True, 0
        else:
            return False, 0
        
        is_built = surrogate.create(features, labels)
        

    def train_test_split(self,
                         features: pd.DataFrame,
                         labels: pd.DataFrame) -> Tuple[List[pd.DataFrame], List[pd.DataFrame], List[pd.DataFrame], List[pd.DataFrame]]:
        return [features], [labels], [features], [labels]
