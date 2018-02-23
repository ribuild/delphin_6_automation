# Imports:
import os
import codecs
import re
import datetime



# Functions:
def isfloat(num):
    try:
        float(num)
    except ValueError:
        return False
    else:
        return True


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def material_file_to_dict(file_path):

    material_dict = {}
    data = codecs.open(file_path, "r", "utf-8")

    sub_key = ""
    n = 0

    for line in data:

        if line.split(" ")[0] == "D6MARLZ!":
            material_dict["INFO-MAGIC_HEADER"] = line.strip("\n")
            material_dict["INFO-LAST_MODIFIED"] = datetime.datetime.now()
            material_dict["INFO-MATERIAL_NAME"] = os.path.split(file_path)[-1].split("_")[0]
            material_dict["INFO-UNIQUE_ID"] = int(os.path.split(file_path)[-1].split("_")[1].split(".")[0])
            material_dict["INFO-FILE"] = file_path

        elif line[0] == "[":
            main_key = re.sub('[\[\]\n]', '', line)
            name = ""

        elif line[0] == " " and line[3] != " " and "=" in line:
            # dictionary keys
            sub_key = line.split("=")[0].strip()
            key = main_key + "-" + sub_key

            # dictionary data 01
            data = line.split("=")[1].strip()

            if len(data.split(" ")) == 2 and isfloat(data.split(" ")[0]):
                data = num(data.split()[0])
                material_dict[key] = data

            elif line.split("=")[0].strip() == "FUNCTION":
                sub_key_func = line.split("=")[1].strip()
            else:
                material_dict[key] = data

        elif sub_key == "FUNCTION" and len(line) > 5:
            if line[5] == " ":
                n += 1

                data = line.split(" ")
                data = [x for x in data if x]
                data.remove("\n")
                data = [num(i) for i in data]

                key = main_key + "-FUNCTION-" + sub_key_func

                if n % 2 != 0:  # ulige linjer (1)
                    key = key + "-X"
                    material_dict[key] = data

                else:  # lige linjer (2)
                    key = key + "-Y"
                    material_dict[key] = data

            elif line[2] == "[":
                sub_key_func = "-MODEL-"

            elif line[2] == " " and sub_key_func == "-MODEL-":
                key = main_key + sub_key_func + line.split("=")[0].strip()
                data  = line.split("=")[1].strip()
                #print(data)

                if isfloat(data):
                    data = data.split(" ")
                    data = [num(i) for i in data]

                material_dict[key] = data
        else:
            name = ""

    return material_dict


def dict_to_m6(material: dict, path: str) -> bool:
    """
    Takes an material dict and converts it into a .m6 file.

    :param material: material dict
    :param path: Path to where .m6 should be placed.
    :return: True
    """

    # TODO - Fix Function. Does not produce the same output as input

    def write_material_content(group, material_dict, model=False):
        unit_dict = {"RHO": "kg/m3", "CE": "J/kgK", "THETA_POR": "m3/m3",
                     "THETA_EFF": "m3/m3", "THETA_CAP": "m3/m3",
                     "THETA_80": "m3/m3", "LAMBDA": "W/mK",
                     "AW": "kg/m2s05", "MEW": "-",
                     "KLEFF": "s", "DLEFF": "m2/s", "KG": "s"}

        if model:
            model_exist = False
            file.write("\n\n  " + "[MODEL]")
            for key, value in material_dict.items():
                try:
                    if key[3] == "[":
                        file.write("\n  " + "[MODEL]")
                except IndexError:
                    pass

        #elif group == 'IDENTIFICATION':
        #    file.write("\n\n" + "[" + group + "]")
        else:
            file.write("\n\n" + "[" + group + "]")

        for key, value in material_dict.items():
            if key.split("-")[0] == group:
                name = key.split("-")[1]

                # Parameters under "FUNCTION"
                if name == "FUNCTION" and key.split("-")[-1] == "X" and model is not True:

                    function_value_x = "      "
                    for v in value:
                        if len(str(v)) >= 17:
                            function_value_x += str(v) + '  '
                        else:
                            function_value_x += str(v).ljust(17)
                            if not function_value_x.endswith('  '):
                                function_value_x += ' '

                    value = material_dict[key.strip("-X") + "-Y"]
                    function_value_y = "      "
                    for v in value:
                        if len(str(v)) >= 17:
                            function_value_y += str(v) + '  '
                        else:
                            function_value_y += str(v).ljust(17)
                            if not function_value_y.endswith('  '):
                                function_value_y += ' '

                    value = key.split("-")[2] + "\n" + function_value_x + "\n" + function_value_y

                    file.write("\n" + "  " + name + " = ".ljust(16) + str(value))

                elif name == "MODEL" and model:  # parameters under "MODEL"
                    name = key.split("-")[-1]
                    if not isinstance(value, str):
                        value = "".join([str(element) for element in value])
                    file.write("\n" + "    " + name.ljust(25) + "= " + str(value))

                elif name in unit_dict:  # parameters with units
                    value = str(value) + " " + unit_dict[name]
                    file.write("\n" + "  " + name.ljust(25) + "= " + str(value))

                elif len(key.split("-")) <= 2:
                    if value == 'AIR_TIGHT':
                        value += ' '
                    file.write("\n" + "  " + name.ljust(25) + "= " + str(value))

        if group.endswith('PARAMETERS') or group.endswith('IDENTIFICATION'):
            file.write("\n")

    # Create file
    material_data = material['material_data']
    file_name = os.path.split(material_data['INFO-FILE'])[1]
    file = codecs.open(path + '/' + file_name, "w", "utf-8")

    # Write lines
    file.write(material_data["INFO-MAGIC_HEADER"])
    write_material_content("IDENTIFICATION", material_data)
    write_material_content("STORAGE_BASE_PARAMETERS", material_data)
    write_material_content("TRANSPORT_BASE_PARAMETERS", material_data)
    write_material_content("MOISTURE_STORAGE", material_data)
    write_material_content("MOISTURE_STORAGE", material_data, True)
    write_material_content("MOISTURE_TRANSPORT", material_data)
    write_material_content("MOISTURE_TRANSPORT", material_data, True)
    file.write("\n")

    file.close()

    return True
