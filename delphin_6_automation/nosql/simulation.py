import mongoengine
import datetime

class Simulation(mongoengine.Document):
    date_added = mongoengine.DateTimeField(default=datetime.datetime.now)
    country = mongoengine.StringField(required=True)
    start_year = mongoengine.IntField(required=True)
    #something = mongoengine.FloatField(required=False)
    #something = mongoengine.EmbeddedDocumentField(Engine, required=True)




    meta = {
        'db_alias': 'local',
        'collection': 'delphin6',
    }

