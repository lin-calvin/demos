import json
import uuid
from twisted.internet import protocol, reactor, endpoints


class Echo(protocol.Protocol):
    def __init__(self, factory):
        print(1)
        self.factory: EchoFactory = factory

    def connectionLost(self,res):
        self.factory.clients.remove(self)
        return
    def dataReceived(self, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            self.transport.write(b'{"res":"error","error":"not json"}')
            return
        if data["type"] == "handshake":
            self.do_handshake(data)
            print(self.factory.services)
        if self not in self.factory.clients:
            self.transport.write(b'{"res":"error","error":"invalid request"}')
        if data["type"] == "respond":
            self.factory.make_respond(data["jobid"], data["data"])
            ret = {"res": "ok", "next_jobid": str(uuid.uuid4())}
            self.transport.write(bytes(json.dumps(ret), "UTF8"))
        if data["type"] == "request":
            self.factory.make_request(
                self, data["service"], data["data"], data["jobid"]
            )

    def do_handshake(self, data):
        if data["role"] == "client":
            self.role = "client"
            self.factory.clients.append(self)
            initial_jobid = uuid.uuid4()
            self.transport.write(
                bytes(
                    json.dumps({"res": "ok", "initial_jobid": str(initial_jobid)}),
                    "UTF8",
                )
            )
            return
        if data["role"] == "service":
            self.role = "service"
            for i in (serv := data["services"]):
                self.factory.services[i] = self
            self.transport.write(b'{"res":"ok"}')
            return

    def make_request(self, service, data, jobid):
        data = {"type": "call", "service": service, "data": data, "jobid": jobid}
        self.transport.write(bytes(json.dumps(data), "UTF8"))
        return

    def make_respond(self, jobid, data):
        data = {"type": "resp", "data": data, "jobid": jobid}
        self.transport.write(bytes(json.dumps(data), "UTF8"))


class EchoFactory(protocol.Factory):
    services = {}
    clients = []
    promises = {}

    def make_request(self, client, service, data, jobid):
        self.services[service].make_request(service, data, jobid)
        self.promises[jobid] = client

    def make_respond(self, jobid, data):
        self.promises[jobid].make_respond(jobid, data)
        del self.promises[jobid]

    def buildProtocol(self, addr):
        return Echo(self)


endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
reactor.run()