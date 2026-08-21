import random


words = ["a", "an", "the", "and", "all", "am", "is"]

    

class Server:

    def __init__(self):
        self.players = []

    # def wait_for_players(self):
    #     while (1):
    #         if player add player    

    def add_player(self, player):
        self.players.append(player)

    def display_players(self):
        str = ""
        for p in self.players:
            str += p.name
            str += '\n'
        return str

    def generate_words(self):

        xs = []
        for i in range(5):
            xs.append(words[random.randint(0, len(words)-1)])
        return xs

    def send_voting_poems(self, player):
        return [p.poem for p in self.players if p != player]

    def to_json(self):
        return { "players": [p.to_json() for p in self.players] }
    



class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.poem = None
        self.vote = None


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

    def to_json(self):
        return { "name": str(self.name), 
                 "score": int(self.score),
                 "poem": str(self.poem),
                 "vote": str(self.vote)
                 }    

