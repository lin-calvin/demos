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
            self.factory.make_respond(data["jobid"],data["data"])
        if data["type"]=="request":
            self.factory.make_request(self,data['service'],data['data'],data["jobid"])
    def do_handshake(self,data):
        if data['role']=="client":
            self.role="client"
            self.factory.clients.append(self)
            initial_jobid=uuid.uuid4()
            self.transport.write(json.dumps({"res":"ok","initial_jobid":initial_jobid}))
            return
        if data["role"]=="service":
            self.role="service"
            for i in (serv:=data['services']):
                self.factory.services[i]=self
            self.transport.write(b'{"res":"ok"}')
            return
    def make_request(self,service,data,jobid):
        data={"type":"call","service":service,"data":data,"jobid":jobid}
        self.transport.write(json.dumps(data))
        return
    def make_respond(self,jobid,data):
        pass
class EchoFactory(protocol.Factory):
    services={}
    clients=[]
    promises={}
    def make_request(self,client,service,data,jobid):
        self.services[service].make_request(service,data,jobid)
        self.promises[jobid]=client
    def make_respond(self,jobid,data):
        self.promises[jobid].make_respond(jobid,data)
        del self.promises[jobid]
    def buildProtocol(self, addr):
        return Echo(self)

endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
reactor.run()
