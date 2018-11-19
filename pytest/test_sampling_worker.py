__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import pytest

# RiBuild Modules
from delphin_6_automation.backend import sampling_worker
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_sampling_worker(add_three_years_weather, add_five_materials, sampling_strategy, mock_load_design_options,
                         mock_wait_until_simulated_sampling, mock_calculate_sample_output, mock_calculate_error,
                         mock_upload_standard_error, mock_check_convergence):

    with pytest.raises(SystemExit) as exc_info:
        sampling_worker.sampling_worker(sampling_strategy)

    assert delphin_entry.Delphin.objects()
    assert sample_entry.Sample.objects()
    assert sample_entry.SampleRaw.objects()
