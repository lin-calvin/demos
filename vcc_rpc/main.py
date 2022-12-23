import json
import uuid
import logging
from twisted.internet import protocol, reactor, endpoints

logging.basicConfig(level=logging.DEBUG)

class RpcProtocol(protocol.Protocol):
    def __init__(self, factory):
        logging.debug(1)
        self.factory = factory

    def send(self, obj):
        self.transport.write(bytes(json.dumps(obj), "UTF8"))

    def connectionLost(self,res):
        if self.role=="client":
            self.factory.clients.remove(self)
    def dataReceived(self, data):
        try:
            data = json.loads(data)
            logging.debug(data)
        except json.JSONDecodeError:
            self.send({"res":"error","error":"not json"})
            return
        if "res" in data:
            return
        match data["type"]:
            case "handshake":
                self.do_handshake(data)
                logging.debug(self.factory.services)
            case "respond":
                self.factory.make_respond(data["jobid"], data["data"])
                ret = {"res": "ok", "next_jobid": str(uuid.uuid4())}
                self.send(ret)
            case "request" if self in self.factory.clients:
                self.factory.make_request(
                    self, data["service"], data["data"], data["jobid"]
                )
            case _:
                self.send({"res":"error","error":"invalid request"})

    def do_handshake(self, data):
        self.role=data["role"]
        if data["role"] == "client":
            self.role = "client"
            self.factory.clients.append(self)
            initial_jobid = uuid.uuid4()
            self.send({"res": "ok", "initial_jobid": str(initial_jobid)})
                    
            return
        if data["role"] == "service":
            self.role = "service"
            for i in data["services"]:
                self.factory.services[i] = self
            self.send({"res":"ok"})
            return

    def make_request(self, service, data, jobid):
        data = {"type": "call", "service": service, "data": data, "jobid": jobid}
        self.send(data)

    def make_respond(self, jobid, data):
        data = {"type": "resp", "data": data, "jobid": jobid}
        self.send(data)


class RpcServer(protocol.Factory):
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
        return RpcProtocol(self)


endpoints.serverFromString(reactor, "tcp:274").listen(RpcServer())
reactor.run()
