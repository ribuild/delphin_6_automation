from delphin_6_automation.database_interactions import general_interactions
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict
from delphin_6_automation.database_interactions import delphin_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry
import os
import pandas as pd

mongo_setup.global_init(auth_dict)

folder = r'U:\RIBuild\2D_1D\Results'
simulated_id_folder = r'U:\RIBuild\2D_1D\Delphin Project\4A'


def download(sim_obj):
    result_id = str(sim_obj.results_raw.id)
    general_interactions.download_raw_result(result_id, folder)
    delphin_interactions.download_delphin_entry(sim_obj, folder + f'/{result_id}')


excel_frame = pd.DataFrame(columns=['Simulation ID', 'Result ID', 'Dimension', 'Brick Type', 'Plaster Type',
                                    'Insulation Type', 'Acronym'])
bricks1d = ['AltbauziegelDresdenZP', 'AltbauziegelDresdenZD', 'AltbauziegelRoteKasernePotsdamInnenziegel1',
            'LimePlasterHist']
bricks2d = ['AltbauziegelDresdenZP', 'AltbauziegelDresdenZD', 'AltbauziegelRoteKasernePotsdamInnenziegel1']
plaster = ['LimeCementMortarHighCementRatio', 'LimeCementMortarLowCementRatio']
insulation = ['RemmersCalciumsilikatSchimmelsanierplatte2']


def create_acronym(dimension, brick, plaster, insulation):
    acronym = ''

    if brick == 'AltbauziegelDresdenZP':
        acronym += 'dresden_zp'

    elif brick == 'AltbauziegelDresdenZD':
        acronym += 'dresden_zd'

    elif brick == 'AltbauziegelRoteKasernePotsdamInnenziegel1':
        acronym += 'potsdam'

    elif brick == 'LimePlasterHist':
        acronym += 'mortar'

    if plaster == 'LimeCementMortarHighCementRatio':
        acronym += '_high_cement'
    elif plaster == 'LimeCementMortarLowCementRatio':
        acronym += '_low_cement'

    if insulation == 'RemmersCalciumsilikatSchimmelsanierplatte2':
        acronym += '_insulated'
    else:
        acronym += '_uninsulated'

    acronym += f'_36_4a_{dimension.lower()}'

    return acronym


simulation_id = []
result_id = []
dimensions = []
brick_type = []
plaster_type = []
insulation_type = []
acronyms = []

for file in os.listdir(simulated_id_folder):
    if file.endswith('.txt'):
        file_obj = open(simulated_id_folder + '/' + file)
        lines = file_obj.readlines()

        for line in lines:
            entry = delphin_entry.Delphin.objects(id=line[:-1]).first()
            if entry.simulated and not os.path.exists(folder + f'\{str(entry.results_raw.id)}'):

                simulation_id.append(str(entry.id))
                result_id.append(str(entry.results_raw.id))
                dimensions.append(f"{entry.dimensions}D")

                for mat in entry.materials:
                    if entry.dimensions == 1 and mat.material_name in bricks1d:
                        brick_type.append(mat.material_name)
                    elif mat.material_name in bricks2d:
                        brick_type.append(mat.material_name)

                plaster_type.append(' '.join([mat.material_name
                                              for mat in entry.materials
                                              if mat.material_name in plaster]))

                insulation_type.append(' '.join([mat.material_name
                                                 for mat in entry.materials
                                                 if mat.material_name in insulation]))

                acronyms.append(create_acronym(dimensions[-1], brick_type[-1], plaster_type[-1], insulation_type[-1]))

                print(f"Simulation ID: {str(entry.id)}, Result ID: {str(entry.results_raw.id)}, "
                      f"Materials: {' '.join([mat.material_name for mat in entry.materials])}, "
                      f"Dimension: {entry.dimensions}\n")
                download(entry)

excel_frame['Simulation ID'] = simulation_id
excel_frame['Result ID'] = result_id
excel_frame['Dimension'] = dimensions
excel_frame['Plaster Type'] = plaster_type
excel_frame['Brick Type'] = brick_type
excel_frame['Insulation Type'] = insulation_type
excel_frame['Acronym'] = acronyms

writer = pd.ExcelWriter(r'U:\RIBuild\2D_1D\4A_36_Acronyms.xlsx')
excel_frame.to_excel(writer, 'Sheet1')
writer.save()
