__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import user_entry
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def create_account(name: str, email: str) -> user_entry.User:
    user = user_entry.User()
    user.name = name
    user.email = email

    user.save()

    return user


def find_account_by_email(email: str) -> user_entry.User:
    user = user_entry.User.objects(email=email).first()

    return user


def add_simulation_to_user(user: user_entry.User, simulation: delphin_entry.Delphin):

    user.update(add_to_set__simulations=simulation)

    return user.id


def list_user_simulations(user):
    user.reload()

    for document in user.simulations:
        if delphin_entry.Delphin.objects(id=document.id).first():
            print(f"ID: {document.id} - Added: {document.added_date} - With priority: {document.queue_priority}")
        else:
            user.update(pull__simulations=document)