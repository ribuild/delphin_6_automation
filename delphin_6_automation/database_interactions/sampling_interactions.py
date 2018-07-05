__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import sample_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def upload_sampling_scheme(sampling_scheme: dict):

    entry = sample_entry.Scheme()
    scheme = sampling_scheme
    entry.save()

    return entry.id


def download_sampling_scheme(scheme_id):
    # TODO - Download sampling scheme

    return None