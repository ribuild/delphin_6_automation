__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import lxml.etree as et
import xmltodict
import datetime
import os
import shutil

# RiBuild Modules:
import delphin_6_automation.simulation.nosql.db_templates.delphin_entry as delphin_db
import delphin_6_automation.simulation.nosql.db_templates.result_entry as result_db
import delphin_6_automation.simulation.nosql.database_collections as collections
#import delphin_6_automation.simulation.database_interactions as interactions

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def dp6_to_dict(path: str) -> dict:
    """
    Converts a Delphin 6 project file to a python dict
    :param path: Path to the Delphin project file
    :return: Dictionary with the project file information
    """

    xml_string = et.tostring(et.parse(path).getroot())
    xml_dict = xmltodict.parse(xml_string, encoding='UTF-8')

    return dict(xml_dict)


def upload_to_database(delphin_file: str,  queue_priority: int) -> delphin_db.Delphin.id:
    """
    Uploads a Delphin file to a database
    :param delphin_file: Path to a Delphin 6 project file
    :param queue_priority: Queue priority for the simulation
    :return: Database entry id
    """

    entry = delphin_db.Delphin()
    entry.materials = collections.material_db
    entry.weather = collections.weather_db
    entry.result_db = collections.raw_result_db
    entry.queue_priority = queue_priority

    delphin_dict = dp6_to_dict(delphin_file)
    entry.dp6_file = delphin_dict

    if len(delphin_dict['DelphinProject']['Discretization']) > 2:
        entry.dimensions = 3
    elif len(delphin_dict['DelphinProject']['Discretization']) > 1:
        entry.dimensions = 2
    else:
        entry.dimensions = 1

    entry.save()

    return entry.id


def mongo_document_to_dp6(document_id: str, path: str) -> bool:
    """
    Converts a database entry to Delphin 6 project file
    :param document_id: Database entry id.
    :param path: Path to where the files should be written.
    :return: True
    """

    delphin_document = delphin_db.Delphin.objects(id=document_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    xmltodict.unparse(delphin_dict, output=open(path + '/' + document_id + '.d6p', 'w'), pretty=True)

    return True


def download_from_database(document_id, path):

    mongo_document_to_dp6(document_id, path)
    material_list = interactions.gather_material_list(document_id)
    #weather_list = interactions.gather_weather_list(document_id)

    #download_materials(material_list, path)
    #download_weather(weather_list, path)


def d6o_to_dict(path: str, filename: str)-> tuple:
    """
    Converts a Delphin results file into a dict
    :param path: path to folder
    :param filename: file name with extension
    :return: converted result dict
    """

    # Helper functions
    def d6o_1d(d6o_lines):
        result_dict_ = dict()
        result_dict_['D6OARLZ'] = lines[0].split(' ')[-1].strip()

        meta_dict_ = {}

        for i in range(1, 14):
            line = lines[i].split('=')
            name = line[0].strip().lower()

            if name == 'created':
                value = datetime.datetime.strptime(line[1][1:-1], '%a %b %d %H:%M:%S %Y')
                meta_dict_[name] = value
            elif name == 'geo_file' or name == 'geo_file_hash':
                value = line[1][1:-1]
                meta_dict_[name] = value
            else:
                value = line[1].strip()
                result_dict_[name] = value

        result_values = []
        for j in range(15, len(d6o_lines)):
            line = lines[j].split('\t')
            result_values.append(float(line[1].strip()))

        result_dict_['result'] = result_values

        return result_dict_, meta_dict_

    file_obj = open(path + '/' + filename, 'r')
    lines = file_obj.readlines()
    file_obj.close()

    result_dict, meta_dict = d6o_1d(lines)

    return result_dict, meta_dict


def g6a_to_dict(path: str, filename: str)-> dict:
    """
    Converts a Delphin geometry file into a dict
    :param path: path to folder
    :param filename: file name with extension
    :return: converted geometry dict
    """

    file_obj = open(path + '/' + filename, 'r')
    lines = file_obj.readlines()
    file_obj.close()

    # Search for key points
    tables = {}
    for index, line in enumerate(lines):
        if line.startswith('TABLE  MATERIALS'):
            tables['materials'] = index

        elif line.startswith('TABLE  GRID'):
            tables['grid'] = index

        elif line.startswith('TABLE  ELEMENT_GEOMETRY'):
            tables['element_geometry'] = index

        elif line.startswith('TABLE  SIDES_GEOMETRY'):
            tables['sides_geometry'] = index

    geometry_name = filename[:-4]
    geometry_dict = {}
    geometry_dict['name'] = geometry_name
    geometry_dict['D6GARLZ'] = lines[0].split(' ')[-1].strip()
    geometry_dict['materials'] = []

    # get materials
    for i in range(2, tables['grid']-1):
        number = int(lines[i][:3])
        hash_ = int(lines[i][11:21])
        name = lines[i][22:-1]

        geometry_dict['materials'].append([number, hash_, name])

    # get grid
    geometry_dict['grid'] = {}
    geometry_dict['grid']['x'] = [float(x)
                                  for x in lines[(tables['grid']+1)].strip().split(' ')]
    geometry_dict['grid']['y'] = [float(y)
                                  for y in lines[tables['grid'] + 2].strip().split(' ')]
    geometry_dict['grid']['z'] = [float(z)
                                  for z in lines[tables['grid'] + 3].strip().split(' ')]

    # get element geometry
    geometry_dict['element_geometry'] = []

    for j in range(tables['element_geometry']+1, tables['sides_geometry']-1):
        line = lines[j].split(' ')
        geometry_line = []
        for element in line:
            if element == '' or element == '\t':
                pass
            else:
                geometry_line.append(float(element.strip()))

        geometry_dict['element_geometry'].append(geometry_line)

    # get sides geometry
    geometry_dict['sides_geometry'] = []

    for k in range(tables['sides_geometry'] + 1, len(lines) - 1):
        line = lines[k].split(' ')
        side_line = []
        for element in line:
            if element == '' or element == '\t' or element == '\n':
                pass
            else:
                side_line.append(float(element.strip()))

        geometry_dict['sides_geometry'].append(side_line)

    return geometry_dict


def cvode_stats_to_dict(path: str) -> dict:
    """
    Converts a Delphin integrator_cvode_stats file into a dict
    :param path: path to folder
    :return: converted tsv dict
    """

    file_obj = open(path + '/integrator_cvode_stats.tsv', 'r')
    lines = file_obj.readlines()
    file_obj.close()

    tsv_dict = {'time': [],
                'steps': [],
                'rhs_evaluations': [],
                'lin_setups': [],
                'number_iterations': [],
                'number_conversion_fails': [],
                'number_error_fails': [],
                'order': [],
                'step_size': []
                }

    for i in range(1, len(lines)):
        line = lines[i].split('\t')
        tsv_dict['time'].append(float(line[0].strip()))
        tsv_dict['steps'].append(int(line[1].strip()))
        tsv_dict['rhs_evaluations'].append(int(line[2].strip()))
        tsv_dict['lin_setups'].append(int(line[3].strip()))
        tsv_dict['number_iterations'].append(int(line[4].strip()))
        tsv_dict['number_conversion_fails'].append(int(line[5].strip()))
        tsv_dict['number_error_fails'].append(int(line[6].strip()))
        tsv_dict['order'].append(int(line[7].strip()))
        tsv_dict['step_size'].append(float(line[8].strip()))

    return tsv_dict


def les_stats_to_dict(path: str) -> dict:
    """
    Converts a Delphin LES_direct_stats file into a dict
    :param path: path to folder
    :return: converted les stats dict
    """

    file_obj = open(path + '/LES_direct_stats.tsv', 'r')
    lines = file_obj.readlines()
    file_obj.close()

    les_dict = {'time': [],
                'number_jac_evaluations': [],
                'number_rhs_evaluations': []
                }

    for i in range(1, len(lines)):
        line = lines[i].split(' ')

        placeholder = []
        for element in line:

            if element == '':
                pass
            else:
                placeholder.append(element)

        les_dict['time'].append(float(placeholder[0].strip()))
        les_dict['number_jacobian_evaluations'].append(int(placeholder[1].strip()))
        les_dict['number_rhs_evaluations'].append(int(placeholder[2].strip()))

    return les_dict


def progress_to_dict(path: str) -> dict:
    """
    Converts a Delphin progress file into a dict
    :param path: path to folder
    :return: converted progress dict
    """

    file_obj = open(path + '/progress.txt', 'r')
    lines = file_obj.readlines()
    file_obj.close()

    progress_dict = {'simulation_time': [],
                     'real_time': [],
                     'percentage': []
                     }

    for i in range(1, len(lines)):
        line = lines[i].split('\t')

        progress_dict['simulation_time'].append(int(line[0].strip()))
        progress_dict['real_time'].append(float(line[1].strip()))
        progress_dict['percentage'].append(float(line[2].strip()))

    return progress_dict


def results_to_mongo_db(path_: str, delete_files: bool =True) -> bool:
    """
    Uploads the results from a Delphin simulation
    :param path_: folder path containing the result files
    :param delete_files: if True the result folder will be deleted. Default is True
    :return: True on success
    """

    id_ = os.path.split(path_)[1]
    result_dict = {}
    result_path = path_ + '/results'
    log_path = path_ + '/log'
    geometry_dict = {}
    meta_dict = {}

    for result_file in os.listdir(result_path):
        if result_file.endswith('.d6o'):
            print(result_file)
            result_dict[result_file.split('.')[0]], meta_dict = d6o_to_dict(result_path, result_file)

        elif result_file.endswith('.g6a'):
            geometry_dict = g6a_to_dict(result_path, result_file)

    entry = result_db.Result()
    entry.delphin_db = collections.delphin_db
    entry.delphin_id = id_
    entry.log['integrator_cvode_stats'] = cvode_stats_to_dict(log_path)
    entry.log['les_direct_stats'] = les_stats_to_dict(log_path)
    entry.log['progress'] = progress_to_dict(log_path)
    entry.geometry_file = geometry_dict
    entry.results = result_dict
    entry.simulation_started = meta_dict['created']
    entry.geometry_file_hash = meta_dict['geo_file_hash']
    entry.save()

    if delete_files:
        shutil.rmtree(path_)

    return True


def dict_to_progress_file(file_dict: dict, log_path: str) -> bool:
    """
    Turns a dictionary into a delphin progress file
    :param file_dict: Dictionary holding the information for the progress file
    :param log_path: Path to were the progress file should be written
    :return: True
    """

    file_obj = open(log_path + '/progress.txt', 'w')

    spaces = 15
    file_obj.write('   Simtime [s] \t   Realtime [s]\t Percentage [%]\n')

    for line_index in range(0, len(file_dict['simulation_time'])):
        sim_string = ' ' * (spaces - len(str(file_dict['simulation_time'][line_index]))) + \
                     str(file_dict['simulation_time'][line_index])

        real_string = ' ' * (spaces - len(str(file_dict['real_time'][line_index]))) + \
                      str(file_dict['real_time'][line_index])

        percentage_string = ' ' * (spaces - len(str(file_dict['percentage'][line_index]))) + \
                            str(file_dict['percentage'][line_index])

        file_obj.write(sim_string + '\t' + real_string + '\t' + percentage_string + '\n')

    file_obj.close()

    return True


def dict_to_cvode_stats_file(file_dict: dict, log_path: str) -> bool:
    """
    Turns a dictionary into a delphin cvode stats file
    :param file_dict: Dictionary holding the information for the cvode stats file
    :param log_path: Path to were the cvode stats file should be written
    :return: True
    """

    file_obj = open(log_path + '/integrator_cvode_stats.tsv', 'w')

    file_obj.write('                 Time [s]\t     Steps\t  RhsEvals\t LinSetups\t  NIters\t NConvFails\t  NErrFails'
                   '\t Order\t  StepSize [s]\n')

    for line_index in range(0, len(file_dict['time'])):
        time_string = ' ' * (25 - len(str(file_dict['time'][line_index]))) + \
                      str(file_dict['time'][line_index])

        steps_string = ' ' * (10 - len(str(file_dict['steps'][line_index]))) + \
                       str(file_dict['steps'][line_index])

        rhs_string = ' ' * (10 - len(str(file_dict['rhs_evaluations'][line_index]))) + \
                     str(file_dict['rhs_evaluations'][line_index])

        lin_string = ' ' * (10 - len(str(file_dict['lin_setup'][line_index]))) + \
                     str(file_dict['lin_setup'][line_index])

        iterations_string = ' ' * (8 - len(str(file_dict['number_iterations'][line_index]))) + \
                            str(file_dict['number_iterations'][line_index])

        conversion_fails_string = ' ' * (11 - len(str(file_dict['number_conversion_fails'][line_index]))) + \
                                  str(file_dict['number_conversion_fails'][line_index])

        error_fails_string = ' ' * (11 - len(str(file_dict['number_error_fails'][line_index]))) + \
                             str(file_dict['number_error_fails'][line_index])

        order_string = ' ' * (6 - len(str(file_dict['order'][line_index]))) + str(file_dict['order'][line_index])

        step_size_string = ' ' * (14 - len(str(file_dict['step_size'][line_index]))) + \
                           str(file_dict['step_size'][line_index])

        file_obj.write(time_string + '\t' + steps_string + '\t' + rhs_string + '\t' + lin_string + '\t'
                       + iterations_string + '\t' + conversion_fails_string + '\t' + error_fails_string + '\t'
                       + order_string + '\t' + step_size_string + '\n')

        file_obj.close()

    return True


def dict_to_les_stats_file(file_dict: dict, log_path: str) -> bool:
    """
    Turns a dictionary into a delphin les stats file
    :param file_dict: Dictionary holding the information for the les stats file
    :param log_path: Path to were the les stats file should be written
    :return: True
    """

    file_obj = open(log_path + '/LES_direct_stats.tsv', 'w')

    file_obj.write('                    Time\t   NJacEvals\t    NRhsEvals')

    for line_index in range(0, len(file_dict['time'])):
        time_string = ' ' * (25 - len(str(file_dict['time'][line_index]))) + \
                      str(file_dict['time'][line_index])

        jac_string = ' ' * (13 - len(str(file_dict['number_jac_evaluations'][line_index]))) + \
                     str(file_dict['number_jac_evaluations'][line_index])

        rhs_string = ' ' * (13 - len(str(file_dict['number_rhs_evaluations'][line_index]))) + \
                     str(file_dict['number_rhs_evaluations'][line_index])

        file_obj.write(time_string + '\t' + jac_string + rhs_string + '\n')

    file_obj.close()

    return True


def write_log_files(result_obj: result_db.Result, download_path: str) -> bool:
    """
    Turns a result database entry into a delphin log file
    :param result_obj: Database entry
    :param download_path: Path to were the log file should be written
    :return: True
    """
    log_dict = dict(result_obj.log)

    log_path = download_path + '/log'
    os.mkdir(log_path)

    dict_to_progress_file(log_dict['progress'], log_path)
    dict_to_cvode_stats_file(log_dict['integrator_cvode_stats'], log_path)
    dict_to_les_stats_file(log_dict['les_direct_stats'], log_path)

    return True


def dict_to_g6a(geometry_dict: dict, result_path: str) -> bool:
    """
    Turns a dictionary into a delphin geometry file
    :param geometry_dict: Dictionary holding the information for the geometry file
    :param result_path: Path to were the geometry file should be written
    :return: True
    """

    file_obj = open(result_path + '/' + geometry_dict['name'] + '.g6a', 'w')

    file_obj.write('D6GARLZ! ' + str(geometry_dict['D6GARLZ']) + '\n')

    file_obj.write('TABLE  MATERIALS\n')
    for material in geometry_dict['materials']:
        file_obj.write(str(material[0]) + '        ' + str(material[1]) + ' ' + str(material[2] + '\n'))

    file_obj.write('\nTABLE  GRID\n')
    for dimension in geometry_dict['grid']:
        file_obj.write(' '.join([str(element_)
                                 for element_ in geometry_dict['grid'][dimension]]) + '\n')

    file_obj.write('\nTABLE  ELEMENT_GEOMETRY\n')
    for element in geometry_dict['element_geometry']:
        space0 = ' ' * (9 - len(str(element[0])))
        space1 = ' ' * max((10 - len(str(element[1]))), 1)
        space2 = '       '
        space3 = ' ' * (5 - len(str(element[3])))
        space4 = ' ' * (5 - len(str(element[4])))

        file_obj.write(str(element[0]) + space0 + str(element[1]) + space1 + str(element[2]) + space2 + '\t ' +
                       str(element[3]) + space3 + str(element[4]) + space4 + str(element[4]) + '\n')

    file_obj.write('\nTABLE  SIDES_GEOMETRY\n')
    for side in geometry_dict['sides_geometry']:
        space0 = ' ' * (9 - len(str(side[0])))
        space1 = ' ' * max((10 - len(str(side[1]))), 1)
        space2 = ' ' * (10 - len(str(side[2])))
        space3 = ' ' * (7 - len(str(side[3])))
        space4 = ' ' * (7 - len(str(side[4])))
        space5 = ' ' * 4

        file_obj.write(str(side[0]) + space0 + str(side[1]) + space1 + str(side[2]) + space2 + '\t ' + str(side[3]) +
                       space3 + str(side[4]) + space4 + str(side[5]) + space5 + '\n')

    return True


def dict_to_d6o(result_dict: dict, result_name: str, result_path: str) -> bool:
    """
    Turns a dictionary into a delphin result file
    :param result_dict: Dictionary holding the information for the result file
    :param result_name: Name of the result file
    :param result_path: Path to were the result file should be written
    :return: True
    """

    file_obj = open(result_path + '/' + result_name + '.d6o', 'w')

    file_obj.write('D6OARLZ! ' + str(result_dict[result_name]['D6OARLZ']) + '\n')
    file_obj.write('TYPE          = ' + str(result_dict[result_name]['type']) + '\n')
    file_obj.write('PROJECT_FILE  = ' + str(result_dict[result_name]['project_file']) + '\n')
    file_obj.write('CREATED       = ' + str(result_dict['simulation_started'].strftime('%a %b %d %H:%M:%S %Y')) + '\n')
    file_obj.write('GEO_FILE      = ' + str(result_dict['geometry_file']['name']) + '\n')
    file_obj.write('GEO_FILE_HASH = ' + str(result_dict['geometry_file_hash']) + '\n')
    file_obj.write('QUANTITY      = ' + str(result_dict[result_name]['quantity']) + '\n')
    file_obj.write('QUANTITY_KW   = ' + str(result_dict[result_name]['quantity_kw']) + '\n')
    file_obj.write('SPACE_TYPE    = ' + str(result_dict[result_name]['space_type']) + '\n')
    file_obj.write('TIME_TYPE     = ' + str(result_dict[result_name]['time_type']) + '\n')
    file_obj.write('VALUE_UNIT    = ' + str(result_dict[result_name]['value_unit']) + '\n')
    file_obj.write('TIME_UNIT     = ' + str(result_dict[result_name]['time_unit']) + '\n')
    file_obj.write('START_YEAR    = ' + str(result_dict[result_name]['start_year']) + '\n')
    file_obj.write('INDICES       = ' + str(result_dict[result_name]['indices']) + ' \n\n')

    for count, value in enumerate(result_dict['result']):
        space_count = ' ' * (13 - len(str(count)))
        space_value = ' ' * (15 - len(str(value)))
        file_obj.write(str(count) + space_count + '\t' + str(value) + space_value + '\t\n')

    file_obj.close()

    return True


def write_result_files(result_obj: result_db.Result, download_path: str) -> bool:
    """
    Writes out all the result files from a result database entry
    :param result_obj: Database entry
    :param download_path: Where to write the files
    :return: True
    """

    result_dict = dict(result_obj.results)

    result_path = download_path + '/results'
    os.mkdir(result_path)

    dict_to_g6a(dict(result_obj.geometry_file), result_path)

    for result_name in result_dict.keys():
        dict_to_d6o(result_dict, result_name, result_path)

    return True
