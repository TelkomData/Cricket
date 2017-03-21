import pandas as pd

class Ball(dict):
    def __init__(self, over):
        self['score'] = 0
        self['bat'] = 0
        self['wicket'] = False
        self['wide'] = False
        self['over'] = over
        self['batsman'] = ''
        self['bowler'] = ''

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
        
    def score_at_time(self, over):
        total = 0
        wicket = 0
        ball_index = self.ball_order.index(over) + 1

        for i in range(ball_index):

            curr_ball = self[str(self.ball_order[i])]
            total += curr_ball['score']
            if curr_ball['wicket']:
                wicket += 1

        return over, total, wicket    

    def fall_of_wickets(self):        
        return [self.score_at_time(ball['over']) for ball in self.wickets()]    
    
    def balls(self):
        return [b for b in self.values() if isinstance(b, Ball)]
    
    def runs(self):
        return [b['score'] for b in self.balls()]
    
    def wickets(self):
        return [b for b in self.balls() if b['wicket']]

    # batting metrics
    
    def bat_partnerships(self):
        return []

    def bat_balls(self, batsman):
        return [b for b in self.balls() if (b['batsman'] == batsman)]
    
    def bat_score(self, batsman):
        if batsman in self.bat_order:        
            return sum([b['bat'] for b in self.bat_balls(batsman)])

    def bat_balls_faced(self, batsman): 
        if batsman in self.bat_order:          
            return sum([1 for b in self.bat_balls(batsman) if ~(b['wide'])]) 

    def bat_ball_outcome(self, batsman, b_out=0):
        if batsman in self.bat_order: 
            return sum([1 for b in self.bat_balls(batsman) if b['score'] == b_out])  
    
    def bat_out(self, batsman):
        if batsman in self.bat_order:   
            return int(batsman in [b['player_out'] for b in self.wickets()])

    def bat_fig(self, batsman):
        if batsman in self.bat_order:
            runs = self.bat_score(batsman)
            balls = self.bat_balls_faced(batsman)
            out = self.bat_out(batsman)
            dots, fours, sixes = [self.bat_ball_outcome(batsman, b) for b in [0, 4, 6]]
            return runs, balls, out, dots, fours, sixes

    def bat_scorecard(self):
        score_board = []
        for batsman in self.bat_order:
            score_board.append([batsman] + [a for a in self.bat_fig(batsman)])
        
        cols = ['Batsman', 'Runs', 'Balls Faced', 'Out', 'Dots', 'Fours', 'Sixes']
        sb = pd.DataFrame(data=score_board, columns=cols)

        total = ['Total', sum(self.runs()), len(self.balls()), len(self.wickets())]
        extra = ['Extras', total[1] - sb['Runs'].sum(), total[2] - sb['Balls Faced'].sum(), 0]
        score_board.append(extra)
        score_board.append(total)
        
        sb = pd.DataFrame(data=score_board, columns=cols) 
        sb['Strike_Rate'] = sb['Runs']/sb['Balls Faced'] * 100
        sb['Pac Man'] = sb['Dots']/sb['Balls Faced'] * 100

        return sb

    # bowling metrics

    def bowl_runs(self, bowler):        
        # adjust for extras
        if bowler in self.bowl_order:
            return sum(b['score'] for b in self.balls() if (b['bowler'] == bowler))

    def bowl_balls_bowled(self, bowler):
        if bowler in self.bowl_order:        
            return sum(1 for b in self.balls() if (b['bowler'] == bowler) & ~(b['wide']))
    
    def bowl_wickets(self, bowler):   
        if bowler in self.bowl_order:     
            return sum([1 for b in self.wickets() if (b['bowler'] == bowler)])
    
    def bowl_fig(self, bowler):
        if bowler in self.bowl_order:
            overs = self.bowl_balls_bowled(bowler)
            runs = self.bowl_runs(bowler)
            wickets = self.bowl_wickets(bowler)
            return overs, runs, wickets

    def bowl_scorecard(self):
        score_board = []
        for bowler in self.bowl_order:
            score_board.append([bowler] + [a for a in self.bowl_fig(bowler)])
         
        sc = pd.DataFrame(data=score_board, columns=['Bowler', 'Balls', 'Runs', 'Wickets']) 
        sc['Overs'] = sc['Balls'].apply(lambda x: self.overs(x))
        return sc[['Bowler', 'Overs', 'Runs', 'Wickets']]

class Match(dict):    
    def __init__(self, match_id):
        self.match_id = match_id
        self.team = {}

    def innings(self):
        for v in self.values():
            if isinstance(v, Innings):
                yield v

    def players(self):
        players = []
        for v in self.innings():
            players += [bat for bat in v.bat_order]
            players += [bowl for bowl in v.bowl_order]
        return list(set(players))

    def __getattr__(self, attr):
        # check if the attribute exists in the Innings class
        # if it does check the attribute in both innings
        # return only the results that come back...
        if hasattr(Innings, attr):
            def wrapper(*args, **kw):
                output = [getattr(i, attr)(*args, **kw) for i in self.innings()]
                try:
                    return [o for o in output if o is not None][0]
                except IndexError:
                    return None
            return wrapper
        raise AttributeError(attr)

    def winner(self):
        pass

class Player(dict):

    def __init__(self, name):
        self.name = name
        self.games = []

    def __repr__(self):
        return 'Bat: {:0.1f}, Bowl: {:0.1f}'.format(self.bat_ave(), self.bowl_ave())

    def __getattr__(self, attr):
        output = [getattr(g, attr)(self.name) for g in self.games]
        return [o for o in output if o is not None]

    def bat_score_above(self, score):
        return sum(int(r > score) for r in self.bat_score)

    def total(self, attr):
        return sum([r for r in getattr(self, attr) if r is not None])

    def ratio(self, num, den):
        try:
            return (1.0 * self.total(num)) / self.total(den)
        except ZeroDivisionError:
            return 0.0

    def bat_ave(self): 
        return self.ratio('bat_score', 'bat_out')

    def bowl_ave(self): 
        return self.ratio('bowl_runs', 'bowl_wickets')


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
            if type(var) == str:
                var = var.strip('- ')
                innings.ball_order.append(var)
            current_ball = innings[var] = Ball(var)

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
