__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import lxml.etree as et
import xml.etree.ElementTree as ET
import xmltodict



# RiBuild Modules:
import delphin_6_automation.nosql.db_templates.delphin_entry as de
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
    entry.result_db = collections.result_db
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



def do6_to_mongo_db():
    """Converts a Delphin 6 output to a json file"""





