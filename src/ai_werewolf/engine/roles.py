from enum import Enum


class Team(str, Enum):
    VILLAGERS = "villagers"
    WEREWOLVES = "werewolves"


class Role(str, Enum):
    VILLAGER = "villager"
    WEREWOLF = "werewolf"
    SEER = "seer"
    DOCTOR = "doctor"


ROLE_TEAM: dict[Role, Team] = {
    Role.VILLAGER: Team.VILLAGERS,
    Role.WEREWOLF: Team.WEREWOLVES,
    Role.SEER: Team.VILLAGERS,
    Role.DOCTOR: Team.VILLAGERS,
}
