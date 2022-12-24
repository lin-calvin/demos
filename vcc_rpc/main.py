import json
import uuid
import logging

from twisted.internet import protocol, reactor, endpoints

class RpcProtocol(protocol.Protocol):
    def __init__(self, factory):
        logging.debug(1)
        self.factory: RpcServer = factory
    
    def dataReceived(self, data):
        try:
            data = json.loads(data)
            logging.debug(data)
        except json.JSONDecodeError:
            self.send({"res": "error", "error": "not json"})
            return
        if "res" in data:
            return
        match data["type"]:
            case "handshake":
                self.do_handshake(data)
                logging.debug(self.factory.services)
            case "respond" if self.role == "service":
                self.factory.make_respond(data["jobid"], data["data"])
            case "request" if self.role == "client":
                try:
                    self.factory.make_request(
                        self, data["service"], data["data"], data["jobid"]
                    )
                    ret = "ok"
                except KeyError:
                    ret = "err"
                self.send({"res": ret, "next_jobid": str(uuid.uuid4())})
            case _:
                self.send({"res": "error", "error": "invalid request"})

    def send(self, data):
        self.transport.write(json.dumps(data).encode())
    
    def do_handshake(self, data):
        self.role = data["role"]
        if data["role"] == "client":
            initial_jobid = uuid.uuid4()
            self.send({"res": "ok", "initial_jobid": str(initial_jobid)})
        elif data["role"] == "service":
            for i in data["services"]:
                self.factory.services[i] = self
            self.send({"res": "ok"})

    def make_request(self, service, data, jobid):
        self.send({"type": "call", "service": service, "data": data, "jobid": jobid})

    def make_respond(self, jobid, data):
        self.send({"type": "resp", "data": data, "jobid": jobid})


class RpcServer(protocol.Factory):
    services = {}
    promises = {}

    def make_request(self, client, service, data, jobid):
        try:
            self.services[service].make_request(service, data, jobid)
        except KeyError:
            raise KeyError("Not such service")
        self.promises[jobid] = client

    def make_respond(self, jobid, data):
        self.promises[jobid].make_respond(jobid, data)
        del self.promises[jobid]

    def buildProtocol(self, addr):
        return RpcProtocol(self)


endpoints.serverFromString(reactor, "tcp:274").listen(RpcServer())
reactor.run()
