from sshtunnel import SSHTunnelForwarder
from delphin_6_automation.nosql.auth import *

import mongoengine


"""
server = SSHTunnelForwarder(
(HOST_IP, HOST_PORT),
ssh_username = SSH_USER,
ssh_password = SSH_PASS,
remote_bind_address = ('localhost', 27017)
)
"""


def global_init():
    mongoengine.register_connection(
                                    alias='local',
                                    name=MONGO_DB,
                                    host=HOST_IP,
                                    port=HOST_PORT
                                        )


    """
    server = SSHTunnelForwarder(
    (HOST_IP, HOST_PORT),
    ssh_username = SSH_USER,
    ssh_password = SSH_PASS,
    remote_bind_address = ('localhost', 27017)
    )

    server.start()

    mongoengine.register_connection(
        alias='db_conn_alias',
        name=MONGO_DB,
        host='127.0.0.1',
        port=server.local_bind_port,

        username=MONGO_USER,
        password=MONGO_PASS,
        authentication_source=AUTH_SOURCE,
        authentication_mechanism='SCRAM-SHA-1'
        )

    server.stop()
    """




"""
client = pymongo.MongoClient('127.0.0.1', server.local_bind_port)
db = client[MONGO_DB]
db.authenticate(MONGO_USER, MONGO_PASS)
coll = db.queue_db
coll.insert({"testFile42":43})
"""



"""
server.start()

def global_init():
    if SSH_USER or SSH_PASS:

        mongoengine.register_connection(
            alias='queue_db',
            name=MONGO_USER,
            host=server,
            port=HOST_PORT,
            read_preference=None,
            username=MONGO_USER,
            password=MONGO_PASS,
            authentication_source=AUTH_SOURCE,
            authentication_mechanism='SCRAM-SHA-1'
            )
server.stop()
"""

"""
auth_dict = dict(
    username = MONGO_USER,
    password = MONGO_PASS,
    host = SERVER,
    port = HOST_PORT,
    authentication_source = AUTH_SOURCE,
    authentication_mechanism = 'SCRAM-SHA-1'
    )

mongoengine.register_connection(
    alias='queue_db',
    db='test',
    **auth_dict)"""


#mongoengine.register_connection(alias='overview', db='ribuild')

#mongoengine.register_connection(alias='results', db='ribuild_results')
#mongoengine.register_connection(alias='weather_db', db='ribuild_weather')
#mongoengine.register_connection(alias='materials_db', db='ribuild_materials')

