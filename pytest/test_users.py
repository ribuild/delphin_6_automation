__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules
import io
from contextlib import redirect_stdout

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import user_entry
from delphin_6_automation.database_interactions import user_interactions
from delphin_6_automation.database_interactions.db_templates import delphin_entry

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def test_add_user(empty_database):

    user_interactions.create_account('User Test', 'test@test.com')

    assert user_entry.User.objects().first()
    assert len(user_entry.User.objects()) == 1


def test_user_properties(empty_database):

    u_email = 'test@test.com'
    u_name = 'User Test'

    user_interactions.create_account(u_name, u_email)

    expected_user = user_entry.User.objects().first()

    assert expected_user.name == u_name
    assert expected_user.email == u_email
    assert expected_user.simulations == []
    assert not expected_user.password


def test_find_user_by_email(add_single_user):

    expected_user = user_entry.User.objects().first()
    found_user = user_interactions.find_account_by_email(expected_user.email)

    assert expected_user.id == found_user.id


def test_add_simulation_to_user(db_one_project):

    user = user_entry.User.objects().first()
    simulation = delphin_entry.Delphin.objects().first()

    user_interactions.add_simulation_to_user(user, simulation)
    user.reload()

    assert user.simulations
    assert simulation.id == user.simulations[0].id


def test_user_simulations(db_one_project):

    user = user_entry.User.objects().first()
    simulation = delphin_entry.Delphin.objects().first()

    user_interactions.add_simulation_to_user(user, simulation)
    user.reload()

    expected_out = f"ID: {simulation.id} - " \
                   f"Added: {simulation.added_date} - " \
                   f"With priority: {simulation.queue_priority}\n"
    f = io.StringIO()
    with redirect_stdout(f):
        user_interactions.list_user_simulations(user)
    out = f.getvalue()

    assert expected_out == out
