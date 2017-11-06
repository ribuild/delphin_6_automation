import mongoengine

class Simulation(mongoengine.Document):
    country = mongoengine.StringField()
    start_year = mongoengine.IntField()
    end_year = mongoengine.IntField()

    meta = {
        'db_alias': 'local',
        'collection': 'delphin6',
    }

