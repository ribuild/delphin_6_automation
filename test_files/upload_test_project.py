
import os

from delphin_6_automation.database_interactions.auth import auth_dict

import delphin_6_automation.database_interactions.mongo_setup as mongo_setup

from delphin_6_automation.pytest.pytest_helper_functions import upload_needed_project

mongo_setup.global_init(auth_dict)

upload_needed_project('download_project_1')
