from sshtunnel import SSHTunnelForwarder
import mongoengine


def global_init(auth_dict):


    if auth_dict['ssh']:

        server = SSHTunnelForwarder(
                                    (auth_dict['ssh_ip'], auth_dict['ssh_port']),
                                    ssh_username=auth_dict['ssh_user'],
                                    ssh_password=auth_dict['ssh_password'],
                                    remote_bind_address=('localhost', 27017)
                                    )

        print(42)
        server.start()
        print(43)

        mongoengine.register_connection(
                                        alias=auth_dict['alias'],
                                        name=auth_dict['name'],
                                        username=auth_dict['username'],
                                        password=auth_dict['password'],
                                        host=auth_dict['ip'],
                                        port=server.local_bind_port
                                        )

    else:
        mongoengine.register_connection(
                                        alias=auth_dict['alias'],
                                        name=auth_dict['name'],
                                        host=auth_dict['ip'],
                                        port=auth_dict['port']
                                        )


    # TODO - Delete below if not needed.

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

