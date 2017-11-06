__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
from datetime import datetime
import xml.etree.ElementTree as ET
import os

# RiBuild Modules:

# -------------------------------------------------------------------------------------------------------------------- #
# DELPHIN FUNCTIONS AND CLASSES


class Delphin6File:

    def __init__(self):
        self.xml_tree = ET.Element('DelphinProject')
        self.material_database = None

    def create_attributes(self, file_attributes):
        self.xml_tree.set('xmlns', file_attributes['xmlns'])
        self.xml_tree.set('xmlns:xsi', file_attributes['xmlns:xsi'])
        self.xml_tree.set('xmlns:IBK', file_attributes['xmlns:IBK'])
        self.xml_tree.set('xsi:schemaLocation', file_attributes['xsi:schemaLocation'])
        self.xml_tree.set('fileVersion', file_attributes['file_version'])

    def create_project_info(self, comment, created=None):
        last_edited = datetime.strftime(datetime.now(), '%c')

        if not created:
            created = last_edited

        info_tree = ET.SubElement(self.xml_tree, 'ProjectInfo')
        info_tree.set('created', created)
        info_tree.set('lastEdited', last_edited)

        comment_tree = ET.SubElement(info_tree, 'Comment')
        comment_tree.text = str(comment)

    def create_directory_placeholders(self, climate_database=None, material_database=None):
        if not climate_database:
            climate_database = r'C:/Program Files/IBK/Delphin 6.0/resources/DB_climate'

        if not material_database:
            material_database = r'C:/Program Files/IBK/Delphin 6.0/resources/DB_materials'
            self.material_database = material_database

        directory_placeholders_tree = ET.SubElement(self.xml_tree, 'DirectoryPlaceholders')

        climate_param = ET.SubElement(directory_placeholders_tree, 'Placeholder')
        climate_param.set('name', 'Climate Database')
        climate_param.text = climate_database

        material_param = ET.SubElement(directory_placeholders_tree, 'Placeholder')
        material_param.set('name', 'Material Database')
        material_param.text = material_database

    def create_init(self, duration_unit, duration, longitude, latitude, climate_data_path, albedo, balance_equation_module='BEHeatMoisture'):
        init_tree = ET.SubElement(self.xml_tree, 'Init')
        sim_param_tree = ET.SubElement(init_tree, 'SimulationParameter')
        balance_equation_module_tree = ET.SubElement(sim_param_tree, 'BalanceEquationModule')
        balance_equation_module_tree.text = balance_equation_module

        interval_tree = ET.SubElement(sim_param_tree, 'Interval')
        interval_param = ET.SubElement(interval_tree, 'IBK:Parameter')
        interval_param.set('name', 'Duration')
        interval_param.set('unit', str(duration_unit))
        interval_param.text = int(duration)

        climate_path_tree = ET.SubElement(sim_param_tree, 'ClimateDataFilePath')
        climate_path_tree.text = str(climate_data_path)

        longitude_param = ET.SubElement(sim_param_tree, 'IBK:Parameter')
        longitude_param.set('name', 'Longitude')
        longitude_param.set('unit', 'Deg')
        longitude_param.text = str(longitude)

        latitude_param = ET.SubElement(sim_param_tree, 'IBK:Parameter')
        latitude_param.set('name', 'Latitude')
        latitude_param.set('unit', 'Deg')
        latitude_param.text = latitude

        albedo_param = ET.SubElement(sim_param_tree, 'IBK:Parameter')
        albedo_param.set('name', 'Albedo')
        albedo_param.set('unit', '---')
        albedo_param.text = str(albedo)

    def create_materials(self, material_numbers):

        def read_material_file(file_path):
            """Reads a material file and return the information required by the material parameter"""

            if not file_path:
                return None

            # Initialize variables
            name = None
            color = None
            hatch_code = None

            # Open file and loop through the lines
            file_obj = open(file_path, 'r')
            file_lines = file_obj.readlines()

            for line in file_lines:

                if line.startswith('  NAME'):
                    name_line = line.split('=')
                    names = name_line[1].split('|')

                    for n in names:
                        if n.startswith('EN'):
                            name = n[3:-1]
                        else:
                            pass

                elif line.startswith('  COLOUR') or line.startswith('  COLOR'):
                    color_line = line.split('=')
                    color = color_line[1][1:-1]

                elif line.startswith('  HATCHING'):
                    hatch_line = line.split('=')
                    hatch_code = hatch_line[1][1:-1]

                else:
                    pass

            return name, color, hatch_code, file_path

        def lookup_material(material_number):

            file_end = str(material_number) + '.m6'

            material_files = os.listdir(self.material_database)
            material_path = None

            for f in material_files:
                if f.endswith(file_end):
                    material_path = self.material_database + '/' + f
                else:
                    pass

            return read_material_file(material_path)

        material_tree = ET.SubElement(self.xml_tree, 'Materials')

        for m in material_numbers:
            m = int(m)
            material_name, material_color, material_hatch, material_file = lookup_material(m)

            material_param = ET.SubElement(material_tree, 'MaterialReference')
            material_param.set('name', material_name + ' [' + str(m) + ']')
            material_param.set('color', material_color)
            material_param.set('hatchCode', material_hatch)
            material_param.text = material_file

    def create_discretization(self, discretization):
        discretization_tree = ET.SubElement(self.xml_tree, 'Discretization')

        xstep_tree = ET.SubElement(discretization_tree, 'XStep')
        xstep_tree.set('unit', 'm')
        xstep_tree.text = ' '.join(discretization)

    def create_conditions(self, interfaces, climates, boundary):

        condition_tree = ET.SubElement(self.xml_tree, 'Conditions')

        # Set interfaces
        # Interfaces data structure: dict - {'indoor': {'type': string, 'bc': list with strings, 'orientation': int},
        #                                   'outdoor': {'type': string, 'bc': list with strings}
        #                                   }

        interfaces_tree = ET.SubElement(condition_tree, 'Interfaces')

        indoor_tree = ET.SubElement(interfaces_tree, 'Interface')
        indoor_tree.set('name', 'Indoor surface')
        indoor_tree.set('type', interfaces['indoor']['type'])

        interface_param = ET.SubElement(indoor_tree, 'IBK:Parameter')
        interface_param.set('name', 'Orientation')
        interface_param.set('unit', 'Deg')
        interface_param.text = interfaces['indoor']['orientation']

        for bc in interfaces['indoor']['bc']:
            bc_param = ET.SubElement(indoor_tree, 'BCReference')
            bc_param.text = bc

        # Set climate conditions
        # climate conditions data structure: list with dicts.
        # dicts has structure: {'name': 'string',
        #                       'type': string,
        #                       'kind': string,
        #                       'param': dict,
        #                       'file': string or None,
        #                       'flag': dict or None
        #                       }
        #
        # param has structure: {'name': string, 'unit': string, 'value': float or int}
        # flag has structure: {'name': string, 'value': string}

        climate_conditions_tree = ET.SubElement(condition_tree, 'ClimateConditions')

        for climate_dict in climates:
            climate_tree = ET.SubElement(climate_conditions_tree, 'ClimateCondition')
            climate_tree.set('name', climate_dict['name'])
            climate_tree.set('type', climate_dict['type'])
            climate_tree.set('kind', climate_dict['kind'])

            if climate_dict['kind'] == 'TabulatedData':
                file_tree = ET.SubElement(climate_tree, 'Filename')
                file_tree.text = climate_dict['file']

                climate_param = ET.SubElement(climate_tree, 'IBK:Parameter')
                climate_param.set('name', climate_dict['param']['name'])
                climate_param.set('unit', climate_dict['param']['unit'])
                climate_param.text = str(climate_dict['param']['value'])

                flag_param = ET.SubElement(climate_tree, 'IBK:Flag')
                flag_param.set('name', climate_dict['flag']['name'])
                flag_param.text = climate_dict['flag']['value']

            elif climate_dict['kind'] == 'Constant':
                climate_param = ET.SubElement(climate_tree, 'IBK:Parameter')
                climate_param.set('name', climate_dict['param']['name'])
                climate_param.set('unit', climate_dict['param']['unit'])
                climate_param.text = str(climate_dict['param']['value'])

            else:
                pass

        # Set boundary conditions
        # boundary conditions data structure: list with dicts.
        # dicts has structure: {'name': 'string',
        #                       'type': string,
        #                       'kind': string,
        #                       'params': list of dicts,
        #                       'cc_ref': list of dicts
        #                       }
        #
        # params has dict structure: {'name': string, 'unit': string, 'value': float or int}
        # cc_ref has dict structure: {'type': string, 'value': string}

        boundaries_tree = ET.SubElement(condition_tree, 'BoundaryConditions')

        for boundary_dict in boundary:
            boundary_tree = ET.SubElement(boundaries_tree, 'BoundaryCondition')
            boundary_tree.set('name', boundary_dict['name'])
            boundary_tree.set('type', boundary_dict['type'])
            boundary_tree.set('kind', boundary_dict['kind'])

            for boundary_parameter in boundary_dict['param']:
                boundary_param = ET.SubElement(boundary_tree, 'IBK:Parameter')
                boundary_param.set('name', boundary_parameter['name'])
                boundary_param.set('unit', boundary_parameter['unit'])
                boundary_param.text = str(boundary_parameter['value'])

            for cc_parameter in boundary_dict['cc_ref']:
                cc_param = ET.SubElement(boundary_tree, 'CCReference')
                cc_param.set('type', cc_parameter['type'])
                cc_param.text = cc_parameter['value']

    def create_outputs(self, output_unit, output_grids, output_files):

        outputs_tree = ET.SubElement(self.xml_tree, 'Outputs')

        # Set general unit parameter
        unit_tree = ET.SubElement(outputs_tree, 'IBK:Unit')
        unit_tree.set('name', output_unit['name'])
        unit_tree.text = output_unit['value']

        # Set output grids
        # output grids data structure: list with dicts.
        # dicts has structure: {'name': 'string',
        #                       'intervals': list of dicts
        #                       }
        #
        # interval has structure: {'name': string, 'unit': string, 'value': float or int}

        output_grids_tree = ET.SubElement(outputs_tree, 'OutputGrids')

        for output_grid in output_grids:

            output_grid_tree = ET.SubElement(output_grids_tree, 'OutputGrid')
            output_grid_tree.set('name', output_grid['name'])

            for interval in output_grid['intervals']:
                interval_tree = ET.SubElement(output_grid_tree, 'Interval')
                interval_tree.set('name', interval['name'])
                interval_tree.set('unit', interval['unit'])
                interval_tree.text = str(interval['value'])

        # Set output files
        # output files data structure: list with dicts.
        # dicts has structure: {'name': 'string',
        #                       'quantity': {'unit': string, 'value': string},
        #                       'time_type': string,
        #                       'space_type': string,
        #                       'output_grid': string
        #                       }

        output_files_tree = ET.SubElement(outputs_tree, 'OutputFiles')

        for output_file in output_files:
            output_file_tree = ET.SubElement(output_files_tree, 'OutputFile')
            output_file_tree.set('name', output_file['name'])

            quantity_param = ET.SubElement(output_file_tree, 'Quantity')
            quantity_param.set('unit', output_file['quantity']['unit'])
            quantity_param.text = output_file['quantity']['value']

    def create_assignments(self, assignment_list):

        # Set assignments
        # assignments data structure: list with dicts.
        # dicts has structure: {'type': 'string',
        #                       'location': string,
        #                       'reference': string,
        #                       'range': list of ints or None,
        #                       'point': list of floats or None
        #                       }

        assignments_tree = ET.SubElement(self.xml_tree, 'Assignments')

        for assignment in assignment_list:

            assignment_tree = ET.SubElement(assignments_tree, 'Assignment')
            assignment_tree.set('type', assignment['type'])
            assignment_tree.set('location', assignment['location'])

            reference_param = ET.SubElement(assignment_tree, 'Reference')
            reference_param.text = assignment['reference']

            if assignment['type'] == 'Material' or assignment['type'] == 'Interface':

                range_param = ET.SubElement(assignment_tree, 'Range')
                range_param.text = ' '.join(assignment['range'])

            elif assignment['type'] == 'Output':
                if assignment['location'] == 'Coordinate':
                    point_param = ET.SubElement(assignment_tree, 'IBK:Point3D')
                    point_param.text = ' '.join(assignment['point'])
                else:
                    pass

            else:
                pass

    def create_xml(self):

        delphin_tree = ET.ElementTree(self.xml_tree)

        return delphin_tree

    def write_xml(self, path):
        xml_file = self.create_xml()

        xml_file.write(path, xml_declaration=True)