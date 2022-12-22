#!/usr/bin/env python

import json

from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory, Protocol


def login(username, password):
    users = {
        "test1": "passwd1",
        "test2": "passwd2",
    }
    if username in users and users[username] == password:
        return True


class EchoClient(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        handshake = {"type": "handshake", "role": "service", "services": ["login"]}
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


class EchoClientFactory(ClientFactory):
    def buildProtocol(self, addr):
        return EchoClient(self)

    def __init__(self):
        self.services = {"login": login}
        self.done = Deferred()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason.getErrorMessage())
        self.done.errback(reason)

    def clientConnectionLost(self, connector, reason):
        print("connection lost:", reason.getErrorMessage())
        self.done.callback(None)


def main(reactor):
    factory = EchoClientFactory()
    reactor.connectTCP("localhost", 1234, factory)
    return factory.done


if __name__ == "__main__":
    task.react(main)
