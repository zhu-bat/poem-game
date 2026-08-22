import enum
import random
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poem_game.db'
app.secret_key = 'thisisagoodsecretkey'
db = SQLAlchemy(app)

WRITING_TIMELIMIT = 120
VOTING_TIMELIMIT = 30
EMPTY_TIMELIMIT = 600

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
    phase_end: Mapped[int] = mapped_column(default=0)

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
        if (self.round <= 3):
            self.set_phase("writing")
        else:
            self.set_phase("endgame")
        db.session.commit()

    def set_phase(self, phase):
        self.phase = phase
        match phase:
            case "writing":
                self.phase_end = int(time.time()) + WRITING_TIMELIMIT
            case "voting":
                self.phase_end = int(time.time()) + VOTING_TIMELIMIT
            case _:
                self.phase_end = int(time.time()) + EMPTY_TIMELIMIT
        db.session.commit()


    # Assume voting phase has finished
    def get_num_votes(self, player):
        return sum([p.vote == player.id for p in self.get_players()])

    def update_score(self):
        all_scores = sorted([self.get_num_votes(p) for p in self.get_players()], reverse=True)
        for p in self.get_players():
            score = self.get_num_votes(p) * 250 * self.round
            p.score += score
            if score >= all_scores[(len(all_scores)//3) - 1]:
                # Save poem
                poem = Poem(player=p.id, server=self.id, content=p.poem, score=score)
                db.session.add(poem)
        db.session.commit()

    def get_players_ranked(self):
        return sorted(self.get_players(), key=lambda p: p.score)

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "round": self.round,
            "phase": self.phase,
            "phase_end": self.phase_end,
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

    def get_ranking(self, server):
        current_rank = 1
        sorted = server.get_players_ranked()
        for i, p in enumerate(server.get_players_ranked()):
            if i > 0 and p.score < sorted[i - 1].score:
                current_rank = i + 1
            if p.id == self.id:
                return current_rank

    def to_json(self):
        return { "name": self.name,
                 "vip": self.vip,
                 "score": self.score,
                 "poem": self.poem,
                 "vote": self.vote,
                 "poem_submitted": self.poem_submitted(),
                 "vote_submitted": self.vote_submitted()
                 }

class Poem(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    server: Mapped[int] = mapped_column(db.ForeignKey(Server.id))
    player: Mapped[int] = mapped_column(db.ForeignKey(Player.id))
    content: Mapped[str] = mapped_column(String(500))
    score: Mapped[int] = mapped_column(default=0)

with app.app_context():
    db.create_all()