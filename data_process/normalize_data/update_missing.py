from delphin_6_automation.delphin_setup.damage_models import mould_index, u_value

__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
from multiprocessing import Pool
import bson
import numpy as np

# RiBuild Modules
from delphin_6_automation.logging.ribuild_logger import ribuild_logger
from delphin_6_automation.database_interactions.db_templates import normalized_entry
from data_process.normalize_data.algea import update_project
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry, material_entry, weather_entry

# Logger
logger = ribuild_logger(__name__)


# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def migrate_delphin(entry, index_, update=False):
    print(f"Got index: {index_}")

    delphin = entry.delphin
    results = delphin.result_processed

    if not results:
        print(f"Skipping {delphin.id}/{index_} due to missing results")
        return

    sample_data = delphin.sample_data
    design = sample_data["design_option"]
    material = material_entry.Material.objects(material_id=sample_data["wall_core_material"]).first()
    weather = weather_entry.Weather.objects(location_name=sample_data["exterior_climate"]).first()

    if not entry:
        entry = normalized_entry.Normalized()

    try:
        entry.delphin = delphin
        entry.loc = weather.location[::-1]
        entry.orientation = sample_data["wall_orientation"]
        entry.wall_width = sample_data["wall_core_width"]
        entry.wall_material = material.material_data["IDENTIFICATION-CATEGORY"].lower()
        entry.ext_plaster = design["exterior_plaster"]

        try:
            entry.int_plaster = design["interior_plaster"]
        except KeyError:
            entry.int_plaster = bool(sample_data["interior_plaster_width"])

        entry.city = sample_data["exterior_climate"]
        entry.insulation_system = design["system_name"]
        entry.insulation_thickness = design["insulation_thickness"]

        raw_data = bson.BSON.decode(results.results_raw.results.read())
        entry.heat_loss = normalize_heat_loss(raw_data["heat loss"]["result"], results.thresholds["heat_loss"])

        entry.algae = get_algea(results, delphin.id)
        entry.u_value = results.u_value
        entry.mould = get_mould(raw_data["temperature mould"]["result"], raw_data["relative humidity mould"]["result"],
                                results.thresholds["mould"])
        avg_temp, min_temp = get_surface_temps(raw_data["temperature interior surface"]["result"])
        entry.avg_surface_temp = avg_temp
        entry.min_surface_temp = min_temp

        insulation_id = design.get("insulation_material", None)
        if insulation_id:
            insulation = material_entry.Material.objects(material_id=insulation_id).first()
            entry.lambda_value = insulation.material_data.get("TRANSPORT_BASE_PARAMETERS-LAMBDA", None)

    except KeyError as err:
        print(f"Got KeyError: {err}. Skipping: {delphin.id}/{index_}")

    else:
        entry.save()


def get_mould(temp_, relhum_, org_mould):
    temp = temp_[8760:]
    relhum = relhum_[8760:]
    if len(temp) > len(relhum):
        temp = temp[:len(relhum)]
    elif len(relhum) > len(temp):
        relhum = relhum[:len(temp)]

    mould = mould_index(temp, relhum, draw_back=1, sensitivity_class=3, surface_quality=0)
    if mould:
        return max(mould)
    else:
        return org_mould


def get_u_value(heat_loss_, ext_temp_, int_temp_):
    heat_loss = heat_loss_[8760:]
    ext_temp = ext_temp_[8760:]
    int_temp = int_temp_[8760:]
    return u_value(heat_loss, ext_temp, int_temp)


def normalize_heat_loss(heat_loss_raw, org_hl):
    heat_loss = np.asarray(heat_loss_raw)[8760:]  # Get rid of the first year
    if heat_loss.size:
        value = heat_loss[heat_loss > 0].sum() / (heat_loss.size / 8760)
        return value
    else:
        return org_hl


def get_algea(results, delphin_id):
    try:
        value = results['thresholds']['algae']
    except KeyError:
        value = update_project(delphin_id)

    return value


def get_surface_temps(results):
    min_temp = min(results)
    avg_temp = sum(results) / len(results)

    return avg_temp, min_temp


def get_ids():
    entries_ = normalized_entry.Normalized.objects(algae__exists=False)
    logger.info(f"Got {entries_.count()} without algae")
    return list(entries_)


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    entries = get_ids()

    # pool = Pool(4)
    # pool.starmap(migrate_delphin, [[delphin.id, index, True] for index, delphin in enumerate(delphins[:50])])

    for index, entry in enumerate(entries):
        migrate_delphin(entry, index, update=True)

    mongo_setup.global_end_ssh(server)
