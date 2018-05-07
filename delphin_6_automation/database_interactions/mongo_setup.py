from sshtunnel import SSHTunnelForwarder
import mongoengine



def global_init(auth_dict):


    if auth_dict['ssh']:

        server=SSHTunnelForwarder(
                                    (auth_dict['ssh_ip'], auth_dict['ssh_port']),
                                    ssh_username=auth_dict['ssh_user'],
                                    ssh_password=auth_dict['ssh_password'],
                                    remote_bind_address=('localhost', 27017)
                                 )


        server.start()


        mongoengine.register_connection(
                                        alias=auth_dict['alias'],
                                        name=auth_dict['name'],
                                        host=auth_dict['ip'],
                                        port=server.local_bind_port,
                                        username=auth_dict['username'],
                                        password=auth_dict['password']
                                        )

    else:
        mongoengine.register_connection(
                                        alias=auth_dict['alias'],
                                        name=auth_dict['name'],
                                        host=auth_dict['ip'],
                                        port=auth_dict['port']
                                        )

def global_end_ssh(auth_dict):

    if auth_dict['ssh']:
        server = SSHTunnelForwarder(
            (auth_dict['ssh_ip'], auth_dict['ssh_port']),
            ssh_username=auth_dict['ssh_user'],
            ssh_password=auth_dict['ssh_password'],
            remote_bind_address=('localhost', 27017)
        )

        server.stop()
