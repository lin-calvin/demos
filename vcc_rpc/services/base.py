import json


from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory, Protocol

class Service(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        handshake = {"type": "handshake", "role": "service", "services": list(self.factory.services.keys())}
        handshake = json.dumps(handshake)
        self.transport.write(bytes(handshake, "UTF8"))

    def dataReceived(self, data):
        try:
            data = json.loads(data)
            print(data)
        except json.JSONDecodeError:
            self.transport.write(b'{"res":"error","error":"not json"}')
            return
        if "res" in data:
            return
        if data["type"] == "call":
            print(1)
            func = self.factory.services[data["service"]]
            resp = func(**data["data"])
            resp = {"type": "respond", "data": resp, "jobid": data["jobid"]}
            resp = json.dumps(resp)
            self.transport.write(bytes(resp, "UTF8"))


class RpcServiceFactory(ClientFactory):
    def buildProtocol(self, addr):
        return Service(self)

    def __init__(self,services):
        self.services = services
        self.done = Deferred()

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        self.done.errback(reason)

    def clientConnectionLost(self, connector, reason):
        print(reason)
        self.done.callback(None)
