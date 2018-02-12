from auth import * #db_admin # private info in db_admin.py file - not synced with github
import pymongo
from sshtunnel import SSHTunnelForwarder
import time
import mongoengine


server = SSHTunnelForwarder(
    (HOST_IP, HOST_PORT),
    ssh_username = SSH_USER,
    ssh_password = SSH_PASS,
    remote_bind_address = ('localhost', 27017)
    )


mongoengine.connect(
    db=DB_NAME,
    host="127.0.0.1",
    port=server.local_bind_port
)


"""
mongoengine.register_connection(
    alias='queue_db',
    name=MONGO_DB,
    host='127.0.0.1',
    port=server.local_bind_port,
    read_preference=None,
    username=MONGO_USER,
    password=MONGO_PASS,
    authentication_source=AUTH_SOURCE,
    authentication_mechanism='SCRAM-SHA-1'
    )
"""

"""
client = pymongo.MongoClient('127.0.0.1', server.local_bind_port)
db = client[MONGO_DB]
db.authenticate(MONGO_USER, MONGO_PASS)
coll = db.queue_db
coll.insert({"testFile42":43})
"""

################################

#server.stop()
