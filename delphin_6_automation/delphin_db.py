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
import delphin_6_automation.nosql.db_templates.delphin_entry as de
import delphin_6_automation.nosql.db_templates.result_entry as re
import delphin_6_automation.nosql.database_collections as collections
import delphin_6_automation.nosql.database_interactions as interactions

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


def dp6_to_dict(path):
    """Converts a Delphin 6 project file to a python dict"""

    xml_string = et.tostring(et.parse(path).getroot())
    xml_dict = xmltodict.parse(xml_string, encoding='UTF-8')

    return dict(xml_dict)


def upload_to_database(delphin_file,  queue_priority):
    """Uploads a Delphin file to a database"""

    entry = de.Delphin()
    entry.materials = collections.material_db
    entry.weather = collections.weather_db
    entry.result_db = collections.raw_result_db
    entry.queue_priority = queue_priority

    delphin_dict = dp6_to_dict(delphin_file)
    print(delphin_dict)
    entry.dp6_file = delphin_dict

    if len(delphin_dict['DelphinProject']['Discretization']) > 2:
        entry.dimensions = 3
    elif len(delphin_dict['DelphinProject']['Discretization']) > 1:
        entry.dimensions = 2
    else:
        entry.dimensions = 1

    entry.save()


def mongo_document_to_dp6(document_id, path):
    """Converts a json file to Delphin 6 project file"""

    delphin_document = de.Delphin.objects(id=document_id).first()
    delphin_dict = dict(delphin_document.dp6_file)
    xmltodict.unparse(delphin_dict, output=open(path + '/' + document_id + '.d6p', 'w'), pretty=True)


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
        result_dict_ = {}
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
    geometry_dict['D6OARLZ'] = lines[0].split(' ')[-1].strip()

    # get materials
    for i in range(2, tables['grid']-1):
        number = int(lines[i][:3])
        hash = int(lines[i][11:21])
        name = lines[i][22:-1]

        geometry_dict['materials'] = [number, hash, name]

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


def cvode_stats_to_dict(path: str)-> dict:
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


def les_stats_to_dict(path: str)-> dict:
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


def progress_to_dict(path: str)-> dict:
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


def results_to_mongo_db(path_: str, delete_files=True):
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

    entry = re.Result()
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

