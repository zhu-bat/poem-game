
words = ["a", "an", "the", "and", "all", "am", "is"]

class Game:

    def __init__(self):
        self.server = Server()


# s.generate_words()

#     Initialize a room and wait for players to
#     join.

#     def start_room():
    

class Server:

    def __init__(self):
        self.players = []

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


#     def send_words():

    
#     def get_poems():
#     def send_voting_poems():

#     def 
    





class Player:
    def __init__(self, name):
        self.name = name

#     def get_words():
    
#     def build_poem():
    
#     def send_poem():

#     def get_voting_poems():
    
#     def vote():
    
#     def update_score():