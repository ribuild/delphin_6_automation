from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions.db_templates import delphin_entry, sample_entry
from delphin_6_automation.delphin_setup.delphin_permutations import get_layers
from delphin_6_automation.sampling.sampling import create_design_info

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


def organize_projects(projects, design_names):

    for count, project in enumerate(projects):
        if count % 500 == 0:
            print(f"Running project #{count}\n")

        layers = get_layers(project.dp6_file)
        materials, system_name = match_insulation(project)
        thickness = get_thickness(project)
        sd_value = get_sd_value(project)

        if len(layers) == 6:
            design_name = f"1d_exteriorinterior_{system_name}_{materials}_{thickness}{sd_value}"

        elif len(layers) == 5:
            if layers[0]["x_width"] > layers[1]["x_width"]:
                design_name = f"1d_interior_{system_name}_{materials}_{thickness}{sd_value}"
            elif len(materials.split("_")) == 2:
                design_name = f"1d_exteriorinterior_{system_name}_{materials}_{thickness}{sd_value}"
            else:
                design_name = f"1d_exterior_{system_name}_{materials}_{thickness}{sd_value}"

        elif len(layers) == 4:
            if layers[0]["x_width"] < layers[1]["x_width"]:
                design_name = f"1d_exterior_{system_name}_{materials}_{thickness}{sd_value}"
            elif len(materials.split("_")) == 2:
                design_name = f"1d_interior_{system_name}_{materials}_{thickness}{sd_value}"
            else:
                design_name = f"1d_bare_{system_name}_{materials}_{thickness}{sd_value}"
        elif len(layers) == 3:
            if layers[0]["x_width"] < layers[1]["x_width"]:
                design_name = f"1d_exteriorinterior"
            else:
                design_name = f"1d_bare_{system_name}_{materials}_{thickness}{sd_value}"
        elif len(layers) == 2:
            if layers[0]["x_width"] > layers[1]["x_width"]:
                design_name = f"1d_interior"
            else:
                design_name = f"1d_exterior"
        else:
            design_name = "1d_bare"

        update_design_info(project, design_name, design_names)


def update_design_info(project, design_name, design_names):
    #print(f"Got design name: {design_name}")
    if design_name not in design_names:
        print(f'Wrong design name: {design_name}')
        project.delete()

    design_info = create_design_info(design_name)

    sample_data = project.sample_data
    sample_data['design_option'] = design_info
    project.sample_data = sample_data
    project.save()


def match_insulation(project):
    design_info = project.sample_data['design_option']
    insulation = design_info.get('insulation_material', None)
    finish = design_info.get('finish_material', None)
    detail = design_info.get('detail_material', None)
    system = design_info.get("system_name")
    if not detail:
        return f"{insulation}_{finish}", system
    else:
        return f"{insulation}_{finish}_{detail}", system


def get_thickness(project):
    design_info = project.sample_data['design_option']
    return design_info['insulation_thickness']


def get_sd_value(project):
    design_info = project.sample_data['design_option']
    sd = design_info.get('sd_value', None)

    if sd is None:
        return ""
    else:
        return f'_SD{str(sd).replace(".", "")}'


def download_designs():
    print('Getting design files')
    # designs = delphin_entry.Design.objects()
    # design_names_ = [design.design_name for design in designs]

    strategy_doc = sample_entry.Strategy.objects().first()
    design_names_ = strategy_doc.strategy["design"]

    return design_names_


def remove_empty(projects):
    for project in projects:
        if not project.dp6_file:
            project.delete()
            print(f'Empty: {project.id}')


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    projects = delphin_entry.Delphin.objects()
    remove_empty(projects)
    #design_names = download_designs()
    #organize_projects(projects, design_names)

    mongo_setup.global_end_ssh(server)

