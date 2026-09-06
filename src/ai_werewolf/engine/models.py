from dataclasses import dataclass, field

from .roles import ROLE_TEAM, Role, Team


@dataclass
class Player:
    id: int
    name: str
    role: Role
    alive: bool = True
    # Facts only this player's own prompts may ever see (e.g. a Seer's past
    # investigation results). Never read when building another player's prompt.
    private_log: list[str] = field(default_factory=list)

    @property
    def team(self) -> Team:
        return ROLE_TEAM[self.role]


@dataclass
class GameState:
    players: list[Player]
    round: int = 0
    log: list[str] = field(default_factory=list)
    winner: Team | None = None
    # Rolling narrative of everything before `summarized_through`, so prompts
    # can stay bounded in size instead of replaying the full transcript.
    summary: str = ""
    summarized_through: int = 0

    def alive_players(self) -> list[Player]:
        return [p for p in self.players if p.alive]

    def alive_by_team(self, team: Team) -> list[Player]:
        return [p for p in self.alive_players() if p.team == team]

    def get(self, player_id: int) -> Player:
        for p in self.players:
            if p.id == player_id:
                return p
        raise KeyError(f"no player with id {player_id}")

    def eliminate(self, player_id: int) -> Player:
        player = self.get(player_id)
        player.alive = False
        return player
