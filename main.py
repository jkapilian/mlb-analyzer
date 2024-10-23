import statsapi
import argparse
import csv
import constants
import json

def build_analysis(args):
	finalObj = {
		"players": {},
		"homeRuns": {},
		"triples": {},
		"attendance": {},
		"gameTimes": {}
	}

	with open(args.file) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			gameId = get_game_id(row)
			add_game(gameId, finalObj)
		print(finalObj)

def get_game_id(row):
	home_team = row[0]
	date = row[1]
	team_code = constants.teamCodes[home_team]
	games = statsapi.schedule(date=date, team=team_code)
	if len(games) == 1:
		return games[0]["game_id"]
	else:
		if len(row) > 2:
			gameNum = row[2]
			for game in games:
				if game["game_num"] == gameNum:
					return game["game_id"]
		else:
			raise Exception("Doubleheaders must have a third column specifying which game was attended")
	raise Exception(f"No game found for {team_code} on {date}")

def add_game(gameId, finalObj):
	boxscore = statsapi.boxscore_data(gameId)
	for player in boxscore["home"]["players"]:
		playerObj = boxscore["home"]["players"][player]
		process_player(playerObj, finalObj)
	for player in boxscore["away"]["players"]:
		playerObj = boxscore["away"]["players"][player]
		process_player(playerObj, finalObj)
	finalObj["attendance"][gameId] = get_field(boxscore, "Att")
	finalObj["gameTimes"][gameId] = get_field(boxscore, "T")
	

def process_player(playerObj, finalObj):
	id = playerObj["person"]["id"]
	homeRuns = playerObj["stats"]["batting"]["homeRuns"] if "homeRuns" in playerObj["stats"]["batting"] else 0
	triples = playerObj["stats"]["batting"]["triples"] if "triples" in playerObj["stats"]["batting"] else 0
	
	if id in finalObj["players"]:
		finalObj["players"][id] += 1
	else:
		finalObj["players"][id] = 1

	if homeRuns > 0:
		if id in finalObj["homeRuns"]:
			finalObj["homeRuns"][id] += homeRuns
		else:
			finalObj["homeRuns"][id] = homeRuns

	if triples > 0:
		if id in finalObj["triples"]:
			finalObj["triples"][id] += triples
		else:
			finalObj["triples"][id] = triples

def get_field(boxscore, field):
	for item in boxscore["gameBoxInfo"]:
		if item["label"] == field:
			return item["value"]
	return ""

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="MLB Analyzer")
	parser.add_argument('-f', '--file', help="CSV of Attendance Data", required=True)
	parser.add_argument('-y', '--year', nargs='+', default=[], help="Years Highlight (not yet implemented)")
	args = parser.parse_args()
	build_analysis(args)