from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import sample_entry, delphin_entry

__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger

# Logger
logger = ribuild_logger(__name__)

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def get_bare():
    ids = delphin_entry.Delphin.objects(sample_data__design_option__name__in=['1d_bare'])
    print('IDS', ids.count())

    return ids


def check_ids(project):

    for project in project:
        sample = sample_entry.Sample.objects(delphin_docs=project).first()
        print(f"Project: {project.id} with sequence {project.sample_data.get('sequence')} is in sample iteration: {sample.iteration}")


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    ids = get_bare()
    check_ids(ids)

    mongo_setup.global_end_ssh(server)