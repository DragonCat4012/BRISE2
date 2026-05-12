import pytest
from typing import Union
from configuration_selection.configuration_selection import ConfigurationSelection
from configuration_selection.model.surrogate.model_mock import ModelMock
from configuration_selection.model.surrogate.tree_parzen_estimator import TreeParzenEstimator
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from default_config_handler.default_configuration_handler_orchestrator import DefaultConfigHandlerOrchestrator
from core_entities.experiment import Experiment
from core_entities.configuration import Configuration
from core_entities.search_space import get_search_space_record
from tools.restore_db import RestoreDB

rdb = RestoreDB()


class TestConfigurationSelection:

    def test_14(self, get_experiment, get_workers, get_configurations_2_float):
        """
        ['2 float', 'flat', 'so', 'mo.none', 'lr', 'surr.vt.none', 'surr.ct.none',
        'optimizer.pso', 'opt.vt.none', 'opt.ct.none',  'validator.mock', 'validator.internal.none', 'cs.best',
        'ted.quantity', 'mr.fsl', 'mtl.none', 'sc.fsl', 'rm.experiment_aware', 'dch.none', 'ss.sobol']
        """
        rdb.cleanup()
        rdb.restore()
        experiment_description, search_space = get_experiment(14)
        experiment = Experiment(experiment_description, search_space)
        experiment.database.write_one_record("Experiment_description", experiment.get_experiment_description_record())
        experiment.database.write_one_record(
            "Search_space", get_search_space_record(search_space, experiment.unique_id)
        )
        dch_o = DefaultConfigHandlerOrchestrator()
        default_config_handler = dch_o.get_default_configuration_handler(experiment=experiment)
        default_configuration = default_config_handler.get_default_configuration()
        assert isinstance(default_configuration, Configuration)
        default_configuration.results = {"Y1": get_configurations_2_float[10]['Result']["Y1"]}
        default_configuration.status['measured'] = True
        default_configuration.status['evaluated'] = True
        experiment.default_configuration = default_configuration
        Configuration.set_task_config(experiment.description["Context"]["TaskConfiguration"])
        cs = ConfigurationSelection(experiment)
        assert isinstance(list(list(cs.predictor.mapping_region_model.values())[0].mapping_surrogate_objective.keys())[
                              0].surrogate_instance, LinearRegression)
        configs = []
        for i in range(0, 9):
            predicted, measured = cs.send_new_configurations_to_measure("", "", "", get_workers)
            results = {"Y1": get_configurations_2_float[i]['Result']["Y1"]}
            predicted[0].results = results
            predicted[0].status['enabled'] = True
            predicted[0].status['measured'] = True
            predicted[0].status['evaluated'] = True
            configs = configs + predicted
            assert len(configs) == i + 1
            assert predicted[0].type is Configuration.Type.FROM_SELECTOR
            experiment.add_configuration(predicted[0])

            experiment.database.write_one_record("Configuration", predicted[0].get_configuration_record())
            experiment.send_state_to_db()

        predicted, measured = cs.send_new_configurations_to_measure("", "", "", get_workers)
        results = {"Y1": get_configurations_2_float[10]['Result']["Y1"]}
        predicted[0].results = results
        predicted[0].status['enabled'] = True
        predicted[0].status['measured'] = True
        predicted[0].status['evaluated'] = True
        configs = configs + predicted
        assert len(configs) == 10
        experiment.add_configuration(predicted[0])
        assert isinstance(list(list(cs.predictor.mapping_region_model.values())[0].mapping_surrogate_objective.keys())[
                              0].surrogate_instance, GaussianProcessRegressor)
        experiment.database.write_one_record("Configuration", predicted[0].get_configuration_record())
        experiment.send_state_to_db()

        temp_region = list(cs.predictor.mapping_region_model.keys())[0]
        assert len(cs.predictor.mapping_region_model[temp_region].mapping_surrogate_objective) == 1  # SO
        experiment.dump("Results")

