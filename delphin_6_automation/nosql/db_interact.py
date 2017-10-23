from db_admin import * #db_admin # private info in db_admin.py file - not synced with github
import pymongo
from sshtunnel import SSHTunnelForwarder
import time


server = SSHTunnelForwarder(
(HOST_IP, HOST_PORT),
ssh_username = SSH_USER,
ssh_password = SSH_PASS,
remote_bind_address = ('localhost', 27017)
)

time.sleep(2)
server.start()
client = pymongo.MongoClient('127.0.0.1', server.local_bind_port)
db = client[MONGO_DB]
db.authenticate(MONGO_USER, MONGO_PASS)
coll = db.sim_queue
coll.insert({"testFile42":43})
server.stop()
