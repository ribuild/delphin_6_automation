__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:


# RiBuild Modules:
import delphin_6_automation.simulation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.simulation.nosql.mongo_setup as mongo_setup
from delphin_6_automation.nosql.auth import dtu_byg
import delphin_6_automation.simulation.nosql.db_templates.result_entry as result_db
import delphin_6_automation.pytest.pytest_helper_functions as helper
import delphin_6_automation.simulation.simulation_package.delphin_solver as solver

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)


def download():
    id_ = "5a5479095d9460327c6970f0"
    test_path, source_path = helper.setup_test_folders()
    delphin_interact.download_from_database(id_, test_path)
    test_file = test_path + '/' + str(id_) + '.d6p'

    return test_file, test_path


def simulate(test_file):
    solver.solve_delphin(test_file)


def upload(test_folder):
    id_ = delphin_interact.results_to_mongo_db(test_folder + '/5a5479095d9460327c6970f0')
    test_doc = result_db.Result.objects(id=id_).first()

    return test_doc


def clean_up(test_doc):
    helper.clean_up_test_folders()
    test_doc.delete()


def test_download_simulate_upload():
    test_file, test_folder = download()
    simulate(test_file)
    test_doc = upload(test_folder)
    clean_up(test_doc)
