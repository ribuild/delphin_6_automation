__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.file_parsing import material_parser

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def compute_hybrid_material(mat1_path, mat2_path, mat1_percentage, mat2_percentage):
    mat1_file = material_parser.material_file_to_dict(mat1_path)
    mat2_file = material_parser.material_file_to_dict(mat2_path)

    def density_function(density1, volume1, density2, volume2):

        return (volume1 * density1 + volume2 * density2)/(volume1 + volume2)

    def porosity_function(porosity1, volume1, porosity2, volume2):

        return (volume1 * porosity1 + volume2 * porosity2)/(volume1 * volume2)

    def specific_heat_capacity_function(specific_heat_capacity1, mass1, specific_heat_capacity2, mass2):

        return (specific_heat_capacity1 * mass1 + specific_heat_capacity2 * mass2)/(mass1 * mass2)

    def lambda_dry_function(lambda1, mass1, lambda2, mass2):

        return (lambda1 * mass1 + lambda2 * mass2)/(mass1 + mass2)

    def theta_pc_function(volume1, theta_pc1, volume2, theta_pc2):

        return (volume1 * theta_pc1 + volume2 * theta_pc2)/(volume1 * volume2)

    def theta_phi_function(volume1, theta_phi1, volume2, theta_phi2):
        return (volume1 * theta_phi1 + volume2 * theta_phi2) / (volume1 * volume2)


def create_hybrid_material():
    pass
