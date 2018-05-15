__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import weather_interactions
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions.db_templates import material_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild

mongo_setup.global_init(auth_dict)

delphin_file0 = r'U:\RIBuild\Material_Sensitivity\Delphin Projects\4A_36cm_brick_1D.d6p'
delphin_file1 = r'U:\RIBuild\Material_Sensitivity\Delphin Projects\4A_36cm_brick_ins_1D.d6p'
delphin_file2 = r'U:\RIBuild\Material_Sensitivity\Delphin Projects\4A_36cm_2D.d6p'
delphin_file3 = r'U:\RIBuild\Material_Sensitivity\Delphin Projects\4A_36cm_ins_2D.d6p'

priority = 'high'
climate_class = 'a'
location_name = 'KobenhavnTaastrup'
years = [2020, 2020, 2021, 2022]
bricks = []

not_hydrolic_computable_bricks = [53, 92, 93, 94, 99, 100, 101, 102, 104, 105, 106, 118, 176, 203, 204, 205, 213, 214,
                                  215, 216, 217, 234, 237, 259, 260, 312, 313, 320, 321, 352, 353, 354, 355, 356, 357,
                                  358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 374, 385,
                                  386, 387, 388, 389, 390, 391]

for material in material_entry.Material.objects():
    if material.material_data['IDENTIFICATION-CATEGORY'] == 'BRICK' and not material.material_id == 504 \
            and material.material_id not in not_hydrolic_computable_bricks:
        bricks.append(material.material_id)


def permutate_uploads(materials):
    print('Uploading')

    sim_id = general_interactions.add_to_simulation_queue(delphin_file0, priority)
    weather_interactions.assign_indoor_climate_to_project(sim_id, climate_class)
    weather_interactions.assign_weather_by_name_and_years(sim_id, location_name, years)
    delphin_interactions.change_entry_simulation_length(sim_id, len(years), 'a')

    layer_material = 'Old Building Brick Dresden ZP [504]'
    priority_ = 1
    modified_ids = delphin_interactions.permutate_entry_layer_material(sim_id, layer_material, materials, priority_)

    for modified_id in modified_ids:
        weather_interactions.assign_weather_by_name_and_years(modified_id, location_name, years)
        weather_interactions.assign_indoor_climate_to_project(modified_id, climate_class)
        delphin_interactions.change_entry_simulation_length(modified_id, len(years), 'a')


print(len(bricks))
#permutate_uploads(bricks)

mongo_setup.global_end_ssh(auth_dict)
