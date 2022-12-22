#!/usr/bin/env python

import base
from twisted.internet import task

def login(username, password):
    users = {
        "test1": "passwd1",
        "test2": "passwd2",
    }
    if username in users and users[username] == password:
        return True


def main(reactor):
    factory = base.RpcServiceFactory({"login":login})
    reactor.connectTCP("localhost", 1234, factory)
    return factory.done


if __name__ == "__main__":
    task.react(main)
