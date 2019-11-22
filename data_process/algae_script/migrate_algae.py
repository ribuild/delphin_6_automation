import bson

from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry, result_raw_entry, material_entry, \
    result_processed_entry
from delphin_6_automation.delphin_setup.damage_models import algae
from multiprocessing import Pool


def get_result_data(project_id):
    result = result_raw_entry.Result.objects(delphin=project_id).first()
    data = bson.BSON.decode(result.results.read())

    return data['temperature algae']['result'], data['relative humidity algae']['result']


def get_material_data(project_id):
    sample_data = delphin_entry.Delphin.objects(id=project_id).only('sample_data').first().sample_data
    plaster = sample_data['design_option'].get('exterior_plaster', None)

    if plaster:
        material = sample_data['exterior_plaster_material']
    else:
        material = sample_data['wall_core_material']

    return get_porosity_and_type(material)


def get_porosity_and_type(material):
    material = material_entry.Material.objects(material_id=material).first()
    porosity = material.material_data.get('STORAGE_BASE_PARAMETERS-THETA_POR', 0.5)
    material_type = material.material_data.get('IDENTIFICATION-CATEGORY', 'brick').lower()

    return material_type, porosity


def update_result(project_id, algae_growth):
    max_algae = max(algae_growth)

    result = result_processed_entry.ProcessedResult.objects(delphin=project_id).first()


def get_delphin_ids():
    ids = delphin_entry.Delphin.objects[:5].only('id')
    print(f'Got {ids.count()} projects')

    ids = [project.id for project in ids]

    return ids


def update_project(delphin_id):
    temperature, relative_humidity = get_result_data(delphin_id)
    material_type, porosity = get_material_data(delphin_id)

    algae_growth = algae(relative_humidity, temperature, material_type=material_type, porosity=porosity, roughness=7.5,
                         total_pore_area=6.5)
    update_result(delphin_id, algae_growth)


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)
    project_ids = get_delphin_ids()

    # pool = Pool(4)
    # pool.map(update_project, project_ids)

    update_project(project_ids[0])
    mongo_setup.global_end_ssh(server)
