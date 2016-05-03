import simplejson as json
import numpy
import requests
from cachecontrol import CacheControl
from cachecontrol.heuristics import LastModified

app_id = {'X-TBA-App-Id': ""}

s = requests.Session()
s = CacheControl(s, heuristic=LastModified())
s.headers.update(app_id)


class Event:
    def __init__(self, info, teams, matches, awards, rankings):
        self.key = info['key']
        self.info = info
        self.teams = list(filter(lambda team: len(list(filter(
            lambda match: team['key'] in match['alliances']['red']['teams'] or team['key'] in
                                                                               match['alliances']['blue']['teams'],
            matches))) > 0, teams))
        self.matches = sorted(matches, key=match_sort_key)
        self.awards = awards
        self.rankings = rankings

    def get_match(self, match_key):
        key = self.key + '_' + match_key
        for match in self.matches:
            if match['key'] == key: return match
        return None

    def team_matches(self, team, quals_only=None, playoffs_only=None):
        if isinstance(team, int): team = 'frc' + str(team)
        matches = []
        filteredMatches = self.matches

        if(quals_only is not None): filteredMatches = self.get_qual_matches()
        if (playoffs_only is not None): filteredMatches = self.get_playoff_matches()

        for match in filteredMatches:
            if team in match['alliances']['red']['teams']:
                matches.append({'match': match, 'alliance': 'red', 'score': match['alliances']['red']['score'],
                                'opp_score': match['alliances']['blue']['score']})
            elif team in match['alliances']['blue']['teams']:
                matches.append({'match': match, 'alliance': 'blue', 'score': match['alliances']['blue']['score'],
                                'opp_score': match['alliances']['red']['score']})
        return matches

    def team_awards(self, team):
        if isinstance(team, str): team = int(team[-4:])
        awards = []
        for award in self.awards:
            for recipient in award['recipient_list']:
                if recipient['team_number'] == team:
                    awards.append({'award': award, 'name': award['name'], 'awardee': recipient['awardee']})
        return awards

    def team_ranking(self, team):
        if isinstance(team, str):
            team = team.split('frc')[1]
        elif isinstance(team, int):
            team = str(team)
        headers = self.rankings[0]
        rank = None

        for row in self.rankings:
            if row[1] == team:
                rank = row
                break

        if rank is None: return None

        col = 0
        ranking_dict = {}
        for c in headers:
            ranking_dict[c] = rank[col]
            col += 1
        return ranking_dict

    def get_qual_matches(self):
        return list(filter(lambda match: match['comp_level'] == 'qm', self.matches))

    def get_playoff_matches(self):
        return list(filter(lambda match: match['comp_level'] != 'qm', self.matches))

    def match_matrix(self):
        match_list = []
        for match in filter(lambda match: match['comp_level'] == 'qm',self.matches):
            matchRow = []
            for team in self.teams:
                matchRow.append(1 if team['key'] in match['alliances']['red']['teams'] else 0)
            match_list.append(matchRow)
            matchRow = []
            for team in self.teams:
                matchRow.append(1 if team['key'] in match['alliances']['blue']['teams'] else 0)
            match_list.append(matchRow)

        mat = numpy.array(match_list)
        return mat[:, numpy.apply_along_axis(numpy.count_nonzero, 0, mat) > 8]

    def opr(self, **kwargs):
        match_scores = []
        kwargs['total'] = lambda m, a: match['alliances'][a]['score']
        for match in filter(lambda match: match['comp_level'] == 'qm',self.matches):
            score = []
            for key in kwargs.keys():
                item = kwargs[key]
                if callable(item):
                    score.append(item(match, 'red'))
                else:
                    score.append(match['score_breakdown']['red'][item])
            match_scores.append(score)
            score = []
            for key in kwargs.keys():
                item = kwargs[key]
                if callable(item):
                    score.append(item(match, 'blue'))
                else:
                    score.append(match['score_breakdown']['red'][item])
            match_scores.append(score)

        match_matrix = self.match_matrix()
        score_matrix = numpy.array(match_scores)
        opr_dict = {}
        mat = numpy.transpose(match_matrix).dot(match_matrix)

        for team in self.teams:
            opr_dict[team['key']] = {}

        col = 0
        for key in kwargs:
            """Solving  A'Ax = A'b with A being the match matrix, and b being the score column we're solving for"""
            score_comp = score_matrix[:,col]
            opr = numpy.linalg.solve(mat, numpy.transpose(match_matrix).dot(score_comp))
            assert len(opr) == len(self.teams)
            row = 0
            for team in self.teams:
                opr_dict[team['key']][key] = opr[row]
                row += 1
            col += 1

        return opr_dict

def match_sort_key(match):
    levels = {
        'qm': 0,
        'ef': 1000,
        'qf': 2000,
        'sf': 3000,
        'f': 4000
    }

    key = levels[match['comp_level']]
    key += 100 * match['set_number'] if match['comp_level'] != 'qm' else 0
    key += match['match_number']
    return key

def set_api_key(name, description, version):
    global app_id
    app_id['X-TBA-App-Id'] = name + ':' + description + ':' + version


def tba_get(path):
    global app_id
    if app_id['X-TBA-App-Id'] == "":
        raise Exception('An API key is required for TBA. Please use set_api_key() to set one.')

    url_str = 'https://www.thebluealliance.com/api/v2/' + path
    r = s.get(url_str, headers=app_id)
    # print(r.url)
    tba_txt = r.text
    return json.loads(tba_txt)


def event_get(year_key):
    event_url = 'event/' + year_key + '/'
    info = tba_get(event_url[:-1])
    teams = tba_get(event_url + 'teams')
    matches = tba_get(event_url + 'matches')
    awards = tba_get(event_url + 'awards')
    rankings = tba_get(event_url + 'rankings')
    return Event(info, teams, matches, awards, rankings)


def team_get(team):
    if isinstance(team, int): team = 'frc' + str(team)
    return tba_get('team/' + team)


def team_events(team, year):
    if isinstance(team, int): team = 'frc' + str(team)
    return tba_get('team/' + team + '/' + str(year) + '/events')


def team_matches(team, year):
    if isinstance(team, int): team = 'frc' + str(team)
    matches = []
    for event in team_events(team, year):
        try:
            ev_matches = tba_get('team/' + team + '/event/' + event['key'] + '/matches')
            for match in ev_matches:
                if team in match['alliances']['red']['teams']:
                    matches.append({'match': match, 'alliance': 'red', 'score': match['alliances']['red']['score'],
                                    'opp_score': match['alliances']['blue']['score']})
                elif team in match['alliances']['blue']['teams']:
                    matches.append({'match': match, 'alliance': 'blue', 'score': match['alliances']['blue']['score'],
                                    'opp_score': match['alliances']['red']['score']})
        except:
            print(event['key'])
    return matches


def district_list(year):
    return tba_get('districts/' + str(year))


def district_events(year, district_code):
    return tba_get('district/' + district_code + '/' + str(year) + '/events')


def district_rankings(year, district_code, team=None):
    if isinstance(team, int): team = 'frc' + str(team)
    ranks_list = []
    ranks_dict = tba_get('district/' + district_code + '/' + str(year) + '/rankings')
    for row in ranks_dict:
        if team is not None and row['team_key'] == team:
            return row
        elif team is None:
            ranks_list.append(row)
    return ranks_list


def district_teams(year, district_code):
    return tba_get('district/' + district_code + '/' + str(year) + '/teams')

##set_api_key("wesj", "pybluealliance", "0")
##x = (team_matches(2363, 2016))
##for match in x:
##    print(match['alliance'], match['score'], match['opp_score'])