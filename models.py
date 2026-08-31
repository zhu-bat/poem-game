import enum
import json
import random
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from functools import lru_cache

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poem_game.db'
app.secret_key = 'thisisagoodsecretkey'
db = SQLAlchemy(app, session_options={"autoflush": False})

WRITING_TIMELIMIT = 180
VOTING_TIMELIMIT = 60
EMPTY_TIMELIMIT = 600

class GamePhase(enum.Enum):
    PREGAME = "pregame"
    WRITING = "writing"
    VOTING = "voting"
    RESULTS = "results"
    ENDGAME = "endgame"

class Server(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, default=lambda: str(random.randint(1000, 9999)))
    phase: Mapped[GamePhase] = mapped_column(default=GamePhase.PREGAME)
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

    @staticmethod
    @lru_cache(maxsize=32)
    def generate_words(seed: int = 0):
        random.seed(seed)
        with open('words.json') as f:
            data = json.load(f)
            rngdle_words = random.choices(list(data.keys()), weights=data.values(), k=25)
        with open('corpus.json') as f:
            data = json.load(f)
            corpus_words = random.choices(list(data.keys()), weights=data.values(), k=15)
        return rngdle_words + corpus_words

    def send_voting_poems(self, player):
        return {p.id: p.poem for p in self.get_players() if p != player and p.poem_submitted()}

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
            self.set_phase(GamePhase.WRITING)
        else:
            self.set_phase(GamePhase.ENDGAME)
        db.session.commit()

    def set_phase(self, phase):
        self.phase = phase
        match phase:
            case GamePhase.WRITING:
                self.phase_end = int(time.time()) + WRITING_TIMELIMIT
            case GamePhase.VOTING:
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
            if p.poem and score >= all_scores[(len(all_scores)//3) - 1]:
                # Save poem
                poem = Poem(player=p.name, server=self.id, round=self.round, content=p.poem, score=score)
                db.session.add(poem)
        db.session.commit()

    def get_players_ranked(self):
        return sorted(self.get_players(), key=lambda p: p.score)[::-1]

    def get_best_poems(self):
        return Poem.query.filter_by(server=self.id).order_by(Poem.score.desc()).all()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "round": self.round,
            "phase": self.phase.value,
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
    last_seen: Mapped[int] = mapped_column(default=0)

    def get_words(self, server):
        return server.generate_words(server.phase_end + self.id)

    def set_poem(self, poem):
        self.poem = poem

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
                current_rank += 1
            if p.id == self.id:
                return current_rank

    def update_last_seen(self):
        self.last_seen = time.time()

    def to_json(self):
        return { "id": self.id,
                 "name": self.name,
                 "vip": self.vip,
                 "score": self.score,
                 "poem": self.poem,
                 "vote": self.vote,
                 "poem_submitted": self.poem_submitted(),
                 "vote_submitted": self.vote_submitted()
                 }

    def __str__(self):
        return f"Player(id={self.id}, name={self.name}, vip={self.vip})"

class Poem(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    server: Mapped[int] = mapped_column(db.ForeignKey(Server.id))
    player: Mapped[str] = mapped_column(String(20))
    round: Mapped[int] = mapped_column()
    content: Mapped[str] = mapped_column(String(500))
    score: Mapped[int] = mapped_column(default=0)

with app.app_context():
    db.create_all()