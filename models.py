import enum
import random

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poem_game.db'
app.secret_key = 'thisisagoodsecretkey'
db = SQLAlchemy(app)

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
        return {p.id: p.poem for p in self.get_players() if p != player}

    def all_poems_submitted(self):
        return all([p.poem_submitted() for p in self.get_players()])

    def all_votes_submitted(self):
        return all([p.vote_submitted() for p in self.get_players()])

    def get_vip(self):
        vip = Player.query.filter_by(server=self.id, vip=True).first()
        if not vip:
            new_vip = Player.query.filter_by(server=self.id).first()
            if not new_vip:
                return None
            new_vip.set_vip(True)
            db.session.commit()
            vip = new_vip
        return vip

    def clear_round(self):
        for p in self.get_players():
            p.poem = None
            p.vote = None
        self.round += 1
        self.phase = "writing"
        db.session.commit()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "round": self.round,
            "phase": self.phase,
            "players": {p.id: p.to_json() for p in self.get_players()},
            "all_poems_submitted": self.all_poems_submitted(),
            "all_votes_submitted": self.all_votes_submitted(),
            "vip": self.get_vip().to_json() if self.get_vip() else None
        }


class Player(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    server: Mapped[int] = mapped_column(db.ForeignKey(Server.id))
    name: Mapped[str] = mapped_column(String(20))
    vip: Mapped[bool] = mapped_column(default=False)
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

    def set_vip(self, is_vip):
        self.vip = is_vip

    def is_vip(self):
        return self.vip


    def to_json(self):
        return { "name": self.name,
                 "vip": self.vip,
                 "score": self.score,
                 "poem": self.poem,
                 "vote": self.vote,
                 "poem_submitted": self.poem_submitted(),
                 "vote_submitted": self.vote_submitted()
                 }

with app.app_context():
    db.create_all()