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

	boxscores = {}

	if args.input:
		with open(args.input, "r") as inputfile:
			boxscores = json.load(inputfile)

	with open(args.data) as csvfile:
		reader = csv.reader(csvfile)
		games = 0
		for row in reader:
			try:
				games += 1
				gameId, otherGameId = get_game_id(row)
				add_game(gameId, otherGameId, finalObj, boxscores)
			except Exception as e:
				raise Exception(f"Error adding game {row}: {e}")
		try:
			if args.output:
				with open(args.output, "w") as outputfile:
					outputfile.write(json.dumps(boxscores))
			process_final(finalObj, games, boxscores)
		except Exception as e:
			raise Exception(f"Error printing summary: {e}")

def get_game_id(row):
	home_team = row[0]
	date = row[1]
	team_code = constants.teamCodes[home_team]
	games = statsapi.schedule(date=date, team=team_code)
	if len(games) == 1:
		return games[0]["game_id"], None
	else:
		if len(row) > 2:
			gameId = None
			otherGameId=  None
			gameNum = row[2]
			for game in games:
				if game["game_num"] == int(gameNum):
					gameId = game["game_id"]
				else:
					otherGameId = game["game_id"]
			return gameId, otherGameId
		else:
			raise Exception("Doubleheaders must have a third column specifying which game was attended")

def add_game(gameId, otherGameId, finalObj, boxscores):
	boxscore = get_boxscore(gameId, boxscores)
	for player in boxscore["home"]["players"]:
		playerObj = boxscore["home"]["players"][player]
		process_player(playerObj, finalObj)
	for player in boxscore["away"]["players"]:
		playerObj = boxscore["away"]["players"][player]
		process_player(playerObj, finalObj)
	try:
		finalObj["attendance"][gameId] = int(get_field(boxscore, "Att").replace(",", ""))
	except:
		# for straight doubleheaders, only one game's attendance is included
		otherDoubleHeaderBoxScore = get_boxscore(otherGameId, boxscores)
		finalObj["attendance"][gameId] = int(get_field(otherDoubleHeaderBoxScore, "Att").replace(",", ""))
	time = get_field(boxscore, "T").split(":")
	finalObj["gameTimes"][gameId] = 60 * int(time[0]) + int(time[1][0:2])
	

def get_boxscore(gameId, boxscores):
	if gameId not in boxscores:
		boxscores[gameId] = statsapi.boxscore_data(gameId)
	return boxscores[gameId]

def process_player(playerObj, finalObj):
	id = playerObj["person"]["id"]
	played = playerObj["stats"]["batting"] != {} or playerObj["stats"]["pitching"]
	homeRuns = playerObj["stats"]["batting"]["homeRuns"] if "homeRuns" in playerObj["stats"]["batting"] else 0
	triples = playerObj["stats"]["batting"]["triples"] if "triples" in playerObj["stats"]["batting"] else 0
	
	if played:
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
			return item["value"][:-1]
	return ""

def process_final(finalObj, games, boxscores):
	print("SUMMARY:\n--------------------------------------\n")
	print(f'Total players seen: {len(finalObj["players"])}')
	process_stat(finalObj, boxscores, "players", "Most seen players: ", get_player_name)
	print(f'\nYou\'ve seen {len(finalObj["homeRuns"])} players hit {sum(finalObj["homeRuns"].values())} home runs')
	process_stat(finalObj, boxscores, "homeRuns", "Biggest power hitters: ", get_player_name)
	print(f'\nYou\'ve seen {len(finalObj["triples"])} players hit {sum(finalObj["triples"].values())} triples')
	process_stat(finalObj, boxscores, "triples", "Fastest around the basepaths: ", get_player_name)

	print(f'\nYou\'ve seen {games} games over the years!')
	process_stat(finalObj, boxscores, "attendance", "Most attended games: ", get_game_info)
	process_stat(finalObj, boxscores, "attendance", "Least attended games: ", get_game_info, False)
	process_stat(finalObj, boxscores, "gameTimes", "Longest games attended: ", get_game_info)
	process_stat(finalObj, boxscores, "gameTimes", "Shortest games attended: ", get_game_info, False)
	

def process_stat(finalObj, boxscores, stat, label, process_item, most=True):
	top = sorted(finalObj[stat].items(), key=get_val, reverse=most)
	final_freq = top[4][1] if len(top) >= 5 else (0 if most else float("inf"))
	print(label)
	for item in top:
		if (most and item[1] < final_freq) or (not most and item[1] > final_freq):
			break
		process_item(item, stat == "gameTimes", boxscores)

def get_val(item):
	return item[1]

def get_player_name(player, _, __):
	playerObj = statsapi.player_stat_data(player[0])
	print(f"{playerObj['first_name']} {playerObj['last_name']}: {player[1]}")

def get_game_info(game, isTime, boxscores):
	boxscore = get_boxscore(game[0], boxscores)
	dateString = boxscore["gameBoxInfo"][-1]["label"]
	away = boxscore["teamInfo"]["away"]["abbreviation"]
	home = boxscore["teamInfo"]["home"]["abbreviation"]
	value = game[1]
	if isTime:
		hour = int(game[1]/60)
		minute = game[1] - 60 * hour
		value = f"{hour}:{'%02d' % minute}"
	print(f"{dateString} {away} vs. {home}: {value}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="MLB Analyzer")
	parser.add_argument('-d', '--data', help="CSV of Attendance Data", required=True)
	parser.add_argument('-i', '--input', help="CSV of previously analyzed boxscores")
	parser.add_argument('-o', '--output', help="CSV of analyzed boxscores")
	parser.add_argument('-y', '--year', nargs='+', default=[], help="Years Highlight (not yet implemented)")
	args = parser.parse_args()
	build_analysis(args)