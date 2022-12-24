#!/usr/bin/env python

from base import RpcServer
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class Group:
    id: int
    name: str
    users: set[str]

class Main:
    def __init__(self) -> None:
        self._groups: list[Group] = []
        self._new_id: int = 0

    def _find_group(self, id: int) -> Group | None:
        for i in self._groups:
            if i.id == id:
                return i
        return None

    def _find_group_with_name(self, name: str) -> Group | None:
        for i in self._groups:
            if i.name == name:
                return i
        return None

    def group_get_by_name(self, name: str) -> dict[str, Any] | None:
        group = self._find_group_with_name(name)
        if group is None:
            return None
        group_dict = asdict(group)
        group_dict["users"] = list(group_dict["users"])
        return group_dict

    def group_get_by_id(self, id: int) -> dict[str, Any] | None:
        group = self._find_group(id)
        if group is None:
            return None
        group_dict = asdict(group)
        group_dict["users"] = list(group_dict["users"])
        return group_dict

    def group_create(self, name: str) -> bool:
        if self._find_group(id) is not None or self._find_group_with_name(name) is not None:
            return False
        self._groups.append(Group(id=id, name=name, users=set()))
        return True

    def group_list(self) -> list[dict[str, Any]]:
        return [{ "id": i.id, "name": i.name } for i in self._groups]

    def group_join(self, username: str, id: int) -> bool: 
        group = self._find_group(id)
        if group is None:
            return False
        if username in group.users:
            return False
        else:
            group.users.add(username)
            return True

    def group_quit(self, username: str, id: int) -> bool:
        group = self._find_group(id)
        if group is None:
            return False
        group.users.discard(username)
        return True



if __name__ == "__main__":
    server = RpcServer()
    server.register(Main())
    server.connect()
