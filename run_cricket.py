from cricket import read_match
import pandas as pd
import glob

all_games = {}

class Player(dict):
    
    def __init__(self, name):
        self.name = name
        self.games = []
    
    def __repr__(self):
        return "Bat Ave: {:0.1f}; Wickets: {:s}".format(self.average(), str(self.wickets()))
    
    def total_runs(self):
        pass
    
    def average(self):

        total = [all_games[g].bat_score(self.name) for g in self.games]
        times_out = [int(all_games[g].bat_out(self.name)) for g in self.games]    
        try:    
            return sum(total) / sum(times_out)
        except:
            return 0

    def wickets(self):
        total = [all_games[g].bowl_wickets(self.name) for g in self.games]   
        return sum(total)


all_players = {}

for file_name in glob.glob('IPL/*.yaml')[0:100]:
    match_id = file_name.strip('IPL/').strip('.yaml')
    # print ('reading in match id {:s}'.format(match_id))
    curr_match = all_games[match_id] = read_match(match_id)

    try:
    
        for player in curr_match.players():
            if player not in all_players.keys():
                all_players[player] = Player(player) 
            all_players[player].games.append(match_id)
    except:
        pass

play = pd.DataFrame(all_players)
play.sort_values('Bat Ave', ascending=False).head()


