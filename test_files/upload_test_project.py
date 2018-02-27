
import os

from delphin_6_automation.database_interactions.auth import dtu_byg

import delphin_6_automation.database_interactions.mongo_setup as mongo_setup

from delphin_6_automation.pytest.pytest_helper_functions import upload_needed_project

mongo_setup.global_init(dtu_byg)

upload_needed_project('download_project_1')
