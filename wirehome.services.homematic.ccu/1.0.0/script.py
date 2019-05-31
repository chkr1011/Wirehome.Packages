import xmlrpclib
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer

config = {}


def initialize():
    global ccu_url, _gateway_is_connected

    ccu_ip = config["ccu_ip"]
    ccu_port = config["ccu_port"]
    ccu_url = "http://{ip}:{port}".format(ip=ccu_ip, port=ccu_port)

    _gateway_is_connected = False

    # configuration of the xml-rpc server used to receive events from the ccu
    rpc_ip = config["rpc_ip"]
    rpc_port = int(config["rpc_port"])
    server = ServerThread(rpc_ip, rpc_port)
    server.start()

    # register server with ccu
    __get_proxy__().init("http://{ip}:{port}".format(ip=rpc_ip, port=rpc_port), "wirehome")


def start():
    pass


def stop():
    pass


def get_device_values(address):
    return __get_proxy__().getParamset(address, "VALUES")


def get_device_value(address, name):
    return __get_proxy__().getValue(address, name)


def __get_proxy__():
    global ccu_url
    return xmlrpclib.ServerProxy(ccu_url)


class XMLRPCHandler:
    def __init__(self):
        pass

    def event(self, interface_id, address, value_key, value):
        self.__fire_event(address, value_key, value)
        return unicode("")

    def listDevices(self, _):
        return []

    def newDevices(self, _):
        return unicode("")

    def newDevice(self, _):
        # it is necessary to return a unicode string here. otherwise, the ccu just won't answer anymore
        return unicode("")

    def deleteDevices(self, ):
        return unicode("")

    def __fire_event(self, address, property_name, new_value):
        wirehome.message_bus.publish({
            "type": "homematic.ccu.event.device_state_changed",
            "address": address,
            "property": property_name,
            "new": new_value
        })


class ServerThread(Thread):
    def __init__(self, ip, port):
        Thread.__init__(self)

        self.server = SimpleXMLRPCServer((ip, port), logRequests=False)
        self.server.register_instance(XMLRPCHandler())
        self.server.register_introspection_functions()
        self.server.register_multicall_functions()

    def run(self):
        self.server.serve_forever()
