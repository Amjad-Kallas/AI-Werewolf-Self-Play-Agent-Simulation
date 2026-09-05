from enum import Enum


class Team(str, Enum):
    VILLAGERS = "villagers"
    WEREWOLVES = "werewolves"


class Role(str, Enum):
    VILLAGER = "villager"
    WEREWOLF = "werewolf"


ROLE_TEAM: dict[Role, Team] = {
    Role.VILLAGER: Team.VILLAGERS,
    Role.WEREWOLF: Team.WEREWOLVES,
}
