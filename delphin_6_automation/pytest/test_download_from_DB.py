import delphin_6_automation.simulation.database_interactions.delphin_interactions as delphin_interact
import delphin_6_automation.simulation.nosql.mongo_setup as mongo_setup
import delphin_6_automation.pytest.pytest_helper_functions as helper
import filecmp

mongo_setup.global_init('test')
test_path, source_path = helper.file_structures_setup()
id_ = "5a25121f5d94600c683b82bd"


def test_download():
    delphin_interact.download_from_database(id_, test_path)
    assert filecmp.cmp(source_path + '/' + str(id_) + '.d6p', test_path + '/' + str(id_) + '.d6p')
