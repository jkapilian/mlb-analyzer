import argparse
import csv
import constants
import cache_manager

def build_analysis(args):
	finalObj = {
		"players": {},
		"homeRuns": {},
		"triples": {},
		"attendance": {},
		"gameTimes": {}
	}

	cacheManager = cache_manager.CacheManager(args.input)

	with open(args.data) as csvfile:
		reader = csv.reader(csvfile)
		games = 0
		for row in reader:
			try:
				games += 1
				gameId, otherGameId = cacheManager.get_game_id(row)
				add_game(gameId, otherGameId, finalObj, cacheManager)
			except Exception as e:
				raise Exception(f"Error adding game {row}: {e}")
		try:
			cacheManager.export_cache(args.output)
			process_final(finalObj, games, cacheManager)
		except Exception as e:
			raise Exception(f"Error printing summary: {e}")

def add_game(gameId, otherGameId, finalObj, cacheManager):
	boxscore = cacheManager.get_boxscore(gameId)
	for player in boxscore["home"]["players"]:
		playerObj = boxscore["home"]["players"][player]
		process_player(playerObj, finalObj)
	for player in boxscore["away"]["players"]:
		playerObj = boxscore["away"]["players"][player]
		process_player(playerObj, finalObj)
	try:
		finalObj["attendance"][gameId] = {
			"val": int(get_field(boxscore, "Att").replace(",", ""))
		}
	except:
		# for straight doubleheaders, only one game's attendance is included
		otherDoubleHeaderBoxScore = cacheManager.get_boxscore(otherGameId)
		finalObj["attendance"][gameId] = {
			"val": int(get_field(otherDoubleHeaderBoxScore, "Att").replace(",", ""))
		}
	time = get_field(boxscore, "T").split(":")
	finalObj["gameTimes"][gameId] = {
		"val": 60 * int(time[0]) + int(time[1][0:2])
	}
	

def process_player(playerObj, finalObj):
	id = playerObj["person"]["id"]
	team = constants.teamCodeReverseLookup[playerObj["parentTeamId"]] if "parentTeamId" in playerObj else "Unknown"
	played = playerObj["stats"]["batting"] != {} or playerObj["stats"]["pitching"]
	homeRuns = playerObj["stats"]["batting"]["homeRuns"] if "homeRuns" in playerObj["stats"]["batting"] else 0
	triples = playerObj["stats"]["batting"]["triples"] if "triples" in playerObj["stats"]["batting"] else 0
	
	if played:
		if id in finalObj["players"]:
			finalObj["players"][id]["val"] += 1
			finalObj["players"][id]["teams"].add(team)
		else:
			finalObj["players"][id] = {
				"val": 1,
				"teams": {team}
			}

	if homeRuns > 0:
		if id in finalObj["homeRuns"]:
			finalObj["homeRuns"][id]["val"] += homeRuns
			finalObj["homeRuns"][id]["teams"].add(team)
		else:
			finalObj["homeRuns"][id] = {
				"val": homeRuns,
				"teams": {team}
			}

	if triples > 0:
		if id in finalObj["triples"]:
			finalObj["triples"][id]["val"] += triples
			finalObj["triples"][id]["teams"].add(team)
		else:
			finalObj["triples"][id] = {
				"val": triples,
				"teams": {team}
			}

def get_field(boxscore, field):
	for item in boxscore["gameBoxInfo"]:
		if item["label"] == field:
			return item["value"][:-1]
	return ""

def process_final(finalObj, games, cacheManager):
	print("SUMMARY:\n--------------------------------------\n")
	print(f'Total players seen: {len(finalObj["players"])}')
	process_stat(finalObj, cacheManager, "players", "Most seen players: ", get_player_name)
	print(f'\nYou\'ve seen {len(finalObj["homeRuns"])} players hit {sum(player["val"] for player in finalObj["homeRuns"].values())} home runs')
	process_stat(finalObj, cacheManager, "homeRuns", "Biggest power hitters: ", get_player_name)
	print(f'\nYou\'ve seen {len(finalObj["triples"])} players hit {sum(player["val"] for player in finalObj["triples"].values())} triples')
	process_stat(finalObj, cacheManager, "triples", "Fastest around the basepaths: ", get_player_name)

	print(f'\nYou\'ve seen {games} games over the years!')
	process_stat(finalObj, cacheManager, "attendance", "Most attended games: ", get_game_info)
	process_stat(finalObj, cacheManager, "attendance", "Least attended games: ", get_game_info, False)
	process_stat(finalObj, cacheManager, "gameTimes", "Longest games attended: ", get_game_info)
	process_stat(finalObj, cacheManager, "gameTimes", "Shortest games attended: ", get_game_info, False)
	

def process_stat(finalObj, cacheManager, stat, label, process_item, most=True):
	top = sorted(finalObj[stat].items(), key=get_val, reverse=most)
	final_freq = get_val(top[4]) if len(top) >= 5 else (0 if most else float("inf"))
	print(label)
	for item in top:
		if (most and get_val(item) < final_freq) or (not most and get_val(item) > final_freq):
			break
		process_item(item, stat == "gameTimes", cacheManager)

def get_val(item):
	return item[1]["val"]

def get_player_name(player, _, cacheManager):
	playerObj = cacheManager.get_player(player[0])
	team_print = ", ".join(player[1]['teams'])
	print(f"{playerObj['first_name']} {playerObj['last_name']}: {get_val(player)} ({team_print})")

def get_game_info(game, isTime, cacheManager):
	boxscore = cacheManager.get_boxscore(game[0])
	dateString = boxscore["gameBoxInfo"][-1]["label"]
	away = boxscore["teamInfo"]["away"]["abbreviation"]
	home = boxscore["teamInfo"]["home"]["abbreviation"]
	value = get_val(game)
	if isTime:
		hour = int(value/60)
		minute = value - 60 * hour
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