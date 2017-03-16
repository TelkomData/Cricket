import pandas as pd

class Ball(dict):
    def __init__(self):
        self['score'] = 0
        self['bat'] = 0
        self['wicket'] = False
        self['wide'] = False

class Innings(Ball):
    
    def __init__(self):
        self.ball_order = []
        self.bat_order = []
        self.bowl_order = []
        
    def overs(self, balls = None):
        if balls == None:
            balls = len(self.balls())            
        return (balls / 6) + ((balls % 6) / 10.0) 

    def over_to_balls(self, over=None):
        if over == None:
            return max(ball_order)
        return int(round(int(over) * 6 + ((over % 1) * 10), 0))
        
    def score_at_time():
        pass    
    
    def balls(self):
        return [b for b in self.values() if isinstance(b, Ball)]
    
    def runs(self):
        return [b['score'] for b in self.balls()]
    
    def wickets(self):
        return [b for b in self.balls() if b['wicket']]

    # batting metrics
    
    def bat_partnerships(self):
        return []
    
    def bat_score(self, batsman):        
        return sum(b['bat'] for b in self.balls() if (b['batsman'] == batsman))

    def bat_balls_faced(self, batsman):        
        return sum(1 for b in self.balls() if (b['batsman'] == batsman) & ~(b['wide']))
            
    
    def bat_out(self, batsman):
        return int(batsman in [b['player_out'] for b in self.wickets()])
    
    def bat_scorecard(self):
        score_board = []
        for batsman in self.bat_order:
            runs = self.bat_score(batsman)
            balls = self.bat_balls_faced(batsman)
            out = self.bat_out(batsman)
            score_board.append((batsman, runs, balls, out))
        
        cols = ['Batsmen', 'Runs', 'Balls Faced', 'Out']
        sb = pd.DataFrame(data=score_board, columns=cols)

        total = ('Total', sum(self.runs()), self.overlen(self.balls()), len(self.wickets()))
        extra = ('Extras', total[1] - sb['Runs'].sum(), total[2] - sb['Balls Faced'].sum(), 0)
        score_board.append(extra)
        score_board.append(total)
        
        sb = pd.DataFrame(data=score_board, columns=cols) 
        sb['Strike_Rate'] = sb['Runs']/sb['Balls Faced'] *100

        return sb

    # bowling metrics

    def bowl_runs(self, bowler):        
        # adjust for extras
        return sum(b['score'] for b in self.balls() if (b['bowler'] == bowler))

    def bowl_balls_bowled(self, bowler):        
        return sum(1 for b in self.balls() if (b['bowler'] == bowler) & ~(b['wide']))
    
    def bowl_wickets(self, bowler):        
        return len([1 for b in self.wickets() if (b['bowler'] == bowler)])
    
    def bowl_scorecard(self):
        score_board = []
        for bowler in self.bowl_order:
            overs = self.overs(self.bowl_balls_bowled(bowler))
            runs = self.bowl_runs(bowler)
            wickets = self.bowl_wickets(bowler)
            score_board.append((bowler, overs, runs, wickets))

        return pd.DataFrame(data=score_board, columns=['Bowler', 'Overs', 'Runs', 'Wickets']) 

class Match(dict):    
    def __init__(self, match_id):
        self.match_id = match_id
        self.team = {}

    def players(self):
        return list(set(self[1].bat_order + self[1].bowl_order + self[2].bat_order + self[2].bowl_order))

    # create functions that reads in metric and returns result for a player
    # def __getattr__(self, attrib):       

        
    def bat_score(self, batsman):
        if batsman in self[1].bat_order:
            return self[1].bat_score(batsman)
        elif batsman in self[2].bat_order:
            return self[2].bat_score(batsman)
        else:
            return None

    def bat_out(self, batsman):
        return any([self[i].bat_out(batsman) for i in [1, 2]])

    def bowl_wickets(self, bowler):
        if bowler in self[1].bowl_order:
            return self[1].bowl_wickets(bowler)
        elif bowler in self[2].bowl_order:
            return self[2].bowl_wickets(bowler)
        else:
            return 0
        
    def winner(self):
        pass

# class Player(dict):
    
#     def __init__(self, name):
#         self.name = name
#         self.games = []
    
#     def __repr__(self):
#         return 'Bat Ave: {:0.1f}, Wickets: {:d}'.format(self.average(), self.wickets())
    
#     def total_runs(self):
#         pass
    
#     def average(self):
#         total = [all_games[g].bat_score(self.name) for g in self.games]
#         times_out = [int(all_games[g].bat_out(self.name)) for g in self.games]        
#         return sum(total) / sum(times_out)

#     def wickets(self):
#         # need to take into account not outs...
#         total = [all_games[g].bowl_wickets(self.name) for g in self.games]      
#         return sum(total)


def read_match(match_id):

    game = Match(match_id)
    f = open('IPL/{:s}.yaml'.format(match_id), 'r')

    for line in f.readlines():
        tabs = [a.strip('\n') for a in line.split('  ')]
        len_tabs = len(tabs)
        try:
            var, out = [a.strip() for a in tabs[-1].split(':')]
        except:
            var = None
            out = [a.strip() for a in tabs[-1].split('- ')]

        if len_tabs == 2:
            game[var] = out
            if (var == '- 1st innings'): 
                innings = game[1] = Innings()
            if (var == '- 2nd innings'):
                innings = game[2] = Innings()

        if len_tabs == 5:
            # var = var.strip('- ')
            # innings.ball_order.append(float(var))
            current_ball = innings[var] = Ball()

        if len_tabs == 7:
            if var == 'wicket':
                current_ball['wicket'] = True
            else:
                current_ball[var] = out

            if var == 'batsman':
                if out not in innings.bat_order:
                    innings.bat_order.append(out)   
 
            if var == 'bowler':
                if out not in innings.bowl_order:
                    innings.bowl_order.append(out)    

        if len_tabs == 8:
            if (var == 'total'):
                current_ball['score'] = int(out)
            if (var == 'batsman'):
                current_ball['bat'] = int(out)
            if (var == 'wides'):
                current_ball['wide'] = True
            
            if current_ball['wicket']:
                current_ball[var] = out
                
    return game
