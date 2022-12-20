import json
import uuid
from twisted.internet import protocol, reactor, endpoints


class Echo(protocol.Protocol):
    def __init__(self,factory):
        print(1)
        self.factory:EchoFactory=factory
    def dataReceived(self, data):
        print(data)
        try:
            data=json.loads(data)
            print(data)
        except json.JSONDecodeError:
            print(22)
            self.transport.write(b'{"res":"error","error":"not json"}')
        if data["type"]=="handshake":
            self.do_handshake(data)
        if data["type"]=="respond":

    def do_handshake(self,data):
        if data['role']=="client":
            self.role="client"
            self.factory.clients.append(self)
            self.transport.write(b'{"res":"ok"}')
            return
        if data["role"]=="service":
            self.role="service"
            for i in (serv:=data['services']):
                self.factory.services[i]=self
            self.transport.write(b'{"res":"ok"}')
            return
    def send_request(self,service,data,jobid):
        data={"type":"call","service":service,"data":data,"jobid":jobid}
        self.transport.write(json.dumps(data))
        return
class EchoFactory(protocol.Factory):
    services={}
    clients=[]
    promises={}
    def make_request(self,client,service,data,jobid):
        self.services[service].send_request(service,data,jobid)

    def buildProtocol(self, addr):
        return Echo(self)

endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
reactor.run()
