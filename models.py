import enum
import random

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app import db

words = ["a", "an", "the", "and", "all", "am", "is"]

class GamePhase(enum.Enum):
    PREGAME = "pregame"
    WRITING = "writing"
    VOTING = "voting"
    RESULTS = "results"
    ENDGAME = "endgame"

class Server(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, default=lambda: str(random.randint(1000, 9999)))
    phase: Mapped[str] = mapped_column(default=GamePhase.PREGAME.value)
    round: Mapped[int] = mapped_column(default=0)

    def get_players(self):
        return Player.query.filter_by(server=self.id).all()

    def display_players(self):
        str = ""
        for p in self.get_players():
            str += p.name
            str += '\n'
        return str

    def generate_words(self):
        xs = []
        for i in range(5):
            xs.append(words[random.randint(0, len(words)-1)])
        return xs

    def send_voting_poems(self, player):
        return [p.poem for p in self.get_players() if p != player]

    def all_poems_submitted(self):
        return all([p.poem_submitted() for p in self.get_players()])

    def all_votes_submitted(self):
        return all([p.vote_submitted() for p in self.get_players()])

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "round": self.round,
            "phase": self.phase,
            "players": {p.id: p.to_json() for p in self.get_players()},
            "all_poems_submitted": self.all_poems_submitted(),
            "all_votes_submitted": self.all_votes_submitted()
        }


class Player(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    server: Mapped[int] = mapped_column(db.ForeignKey(Server.id))
    name: Mapped[str] = mapped_column(String(20))
    score: Mapped[int] = mapped_column(default=0)
    poem: Mapped[str] = mapped_column(String(500), nullable=True, default=None)
    vote: Mapped[int] = mapped_column(nullable=True, default=None)

    def get_words(self, server):
        return server.generate_words()

    def set_poem(self, str):
        self.poem = str

    def get_voting_poems(self, server):
        return server.send_voting_poems(self)

    def set_vote(self, player):
        self.vote = player

    def update_score(self, n):
        self.score += n

    def poem_submitted(self):
        return self.poem is not None

    def vote_submitted(self):
        return self.vote is not None


    def to_json(self):
        return { "name": str(self.name),
                 "score": int(self.score),
                 "poem": str(self.poem),
                 "vote": str(self.vote),
                 "poem_submitted": self.poem_submitted(),
                 "vote_submitted": self.vote_submitted()
                 }