__author__ = "Christian Kongsgaard"


# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import filecmp
import os
import shutil

# RiBuild Modules:
import delphin_6_automation.simulation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.simulation.nosql.mongo_setup as mongo_setup
import delphin_6_automation.pytest.pytest_helper_functions as helper
from delphin_6_automation.simulation.nosql.auth import dtu_byg
import delphin_6_automation.simulation.nosql.db_templates.delphin_entry as delphin_db

# -------------------------------------------------------------------------------------------------------------------- #
# TEST

mongo_setup.global_init(dtu_byg)


def test_upload_1():
    delphin_file = os.path.dirname(os.path.realpath(__file__)) + '/test_files/5a5479095d9460327c6970f0.d6p'
    id_ = delphin_interact.upload_to_database(delphin_file, 10)
    test_doc = delphin_db.Delphin.objects(id=id_).first()
    test_dict = test_doc.to_mongo()
    test_dict.pop('_id')
    test_dict.pop('added_date')
    source_dict = delphin_db.Delphin.objects(id='5a5479095d9460327c6970f0').first().to_mongo()
    source_dict.pop('_id')
    source_dict.pop('added_date')
    assert test_dict == source_dict
    test_doc.delete()
