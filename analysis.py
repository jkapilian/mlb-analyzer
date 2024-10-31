import constants
import copy

class Analysis:
	finalObj = {
		"players": {},
		"homeRuns": {},
		"triples": {},
		"attendance": {},
		"gameTimes": {},
		"gameTimes9Innings": {},
		"shortGames": {},
		"extraInnings": {},
		"venues": {},
		"teams": {}
	}

	years = {}
	
	yearsArr = []

	def __init__(self, args):
		if (args.year):
			self.yearsArr = args.year
			for year in args.year:
				self.years[year] = copy.deepcopy(self.finalObj)

	def add_game(self, gameId, otherGameId, cacheManager, year):
		boxscore = cacheManager.get_boxscore(gameId)
		for player in boxscore["home"]["players"]:
			playerObj = boxscore["home"]["players"][player]
			team = constants.teamCodeReverseLookup[boxscore["home"]["team"]["id"]]
			self.process_player(playerObj, year, boxscore, team)
		for player in boxscore["away"]["players"]:
			playerObj = boxscore["away"]["players"][player]
			team = constants.teamCodeReverseLookup[boxscore["away"]["team"]["id"]]
			self.process_player(playerObj, year, boxscore, team)

		self.process_game(boxscore, gameId, otherGameId, cacheManager, year)

	def process_player(self, playerObj, year, boxscore, team):
		id = playerObj["person"]["id"]
		played = playerObj["stats"]["batting"] != {} or playerObj["stats"]["pitching"]
		homeRuns = playerObj["stats"]["batting"]["homeRuns"] if "homeRuns" in playerObj["stats"]["batting"] else 0
		triples = playerObj["stats"]["batting"]["triples"] if "triples" in playerObj["stats"]["batting"] else 0
		
		if played:
			self.add_into_obj("players", id, "val", 1, False, year)
			self.add_into_obj("players", id, "teams", team, True, year)

		if homeRuns > 0:
			self.add_into_obj("homeRuns", id, "val", homeRuns, False, year)
			self.add_into_obj("homeRuns", id, "teams", team, True, year)

		if triples > 0:
			self.add_into_obj("triples", id, "val", triples, False, year)
			self.add_into_obj("triples", id, "teams", team, True, year)
	
	def process_game(self, boxscore, gameId, otherGameId, cacheManager, year):
		try:
			self.add_into_obj("attendance", gameId, "val", int(self.get_field(boxscore, "Att").replace(",", "")), False, year)
		except:
			# for straight doubleheaders, only one game's attendance is included
			otherDoubleHeaderBoxScore = cacheManager.get_boxscore(otherGameId)
			self.add_into_obj("attendance", gameId, "val", int(self.get_field(otherDoubleHeaderBoxScore, "Att").replace(",", "")), False, year)

		time = self.get_field(boxscore, "T").split(":")
		timeInMinutes = 60 * int(time[0]) + int(time[1][0:2])
		self.add_into_obj("gameTimes", gameId, "val", timeInMinutes, False, year)

		innings = int(float(boxscore["home"]["teamStats"]["pitching"]["inningsPitched"]))
		if innings == 9:
			self.add_into_obj("gameTimes9Innings", gameId, "val", timeInMinutes, False, year)
		elif innings < 9:
			self.add_into_obj("shortGames", gameId, "val", innings, False, year)
		else:
			self.add_into_obj("extraInnings", gameId, "val", innings, False, year)

		venue = self.get_field(boxscore, "Venue")
		self.add_into_obj("venues", venue, "val", 1, False, year)

		homeTeamWon = boxscore["home"]["teamStats"]["batting"]["runs"] > boxscore["away"]["teamStats"]["batting"]["runs"]
		homeTeamId = boxscore["home"]["team"]["id"]
		awayTeamId = boxscore["away"]["team"]["id"]
		self.add_into_obj("teams", homeTeamId, "val", 1, False, year)
		self.add_into_obj("teams", homeTeamId, "homeWins", 1 if homeTeamWon else 0, False, year)
		self.add_into_obj("teams", homeTeamId, "homeLosses", 0 if homeTeamWon else 1, False, year)
		self.add_into_obj("teams", homeTeamId, "awayWins", 0, False, year)
		self.add_into_obj("teams", homeTeamId, "awayLosses", 0, False, year)
		self.add_into_obj("teams", awayTeamId, "val", 1, False, year)
		self.add_into_obj("teams", awayTeamId, "homeWins", 0, False, year)
		self.add_into_obj("teams", awayTeamId, "homeLosses", 0, False, year)
		self.add_into_obj("teams", awayTeamId, "awayWins", 0 if homeTeamWon else 1, False, year)
		self.add_into_obj("teams", awayTeamId, "awayLosses", 1 if homeTeamWon else 0, False, year)

	def add_into_obj(self, stat, id, param, increment, isSet, year):
		objects = [self.finalObj]
		if year in self.yearsArr:
			objects.append(self.years[year])

		for obj in objects:
			if id in obj[stat]:
				if param in obj[stat][id]:
					if isSet:
						obj[stat][id][param].add(increment)
					else:
						obj[stat][id][param] += increment
				else: 
					obj[stat][id][param] = {increment} if isSet else increment
			else:
				obj[stat][id] = {
					param: {increment} if isSet else increment
				}

	def get_field(self, boxscore, field):
		for item in boxscore["gameBoxInfo"]:
			if item["label"] == field:
				return item["value"][:-1]
		return ""

	def process_final(self, games, cacheManager):
		objects = [{
			"year": None,
			"obj": self.finalObj
		}]
		for year in self.yearsArr:
			objects.append({
				"year": year,
				"obj": self.years[year]
			})

		for item in objects:
			year = item["year"]
			print(f"SUMMARY: {year if year else ''}\n--------------------------------------\n")
			print(f'Total players seen: {len(item["obj"]["players"])}')
			self.process_stat(cacheManager, "players", "Most seen players: ", self.get_player_name, year)
			print(f'\nYou\'ve seen {len(item["obj"]["homeRuns"])} players hit {sum(player["val"] for player in item["obj"]["homeRuns"].values())} home runs')
			self.process_stat(cacheManager, "homeRuns", "Biggest power hitters: ", self.get_player_name, year)
			print(f'\nYou\'ve seen {len(item["obj"]["triples"])} players hit {sum(player["val"] for player in item["obj"]["triples"].values())} triples')
			self.process_stat(cacheManager, "triples", "Fastest around the basepaths: ", self.get_player_name, year)

			gamesStr = f"\nYou saw {int(sum(team['val'] for team in item['obj']['teams'].values())/2)} games in {year}!" if year else f'\nYou\'ve seen {games} games over the years!'
			print(gamesStr)
			self.process_stat(cacheManager, "attendance", "Most attended games: ", self.get_game_info, year)
			self.process_stat(cacheManager, "attendance", "Least attended games: ", self.get_game_info, year, False)
			self.process_stat(cacheManager, "gameTimes", "Longest games attended: ", self.get_game_info, year)
			self.process_stat(cacheManager, "gameTimes", "Shortest games attended: ", self.get_game_info, year, False)
			self.process_stat(cacheManager, "gameTimes9Innings", "Longest 9-inning games attended: ", self.get_game_info, year)
			self.process_stat(cacheManager, "gameTimes9Innings", "Shortest 9-inning games attended: ", self.get_game_info, year, False)
			self.process_stat(cacheManager, "extraInnings", "Longest extra inning games (innings): ", self.get_game_info, year)
			self.process_stat(cacheManager, "shortGames", "Shortest games (innings): ", self.get_game_info, year, False)
			self.process_stat(cacheManager, "venues", "Most attended stadiums: ", self.get_venue_info, year)
			self.process_stat(cacheManager, "teams", "Most seen teams: ", self.get_team_info, year)

	def process_stat(self, cacheManager, stat, label, process_item, year, most=True):
		obj = self.years[year] if year else self.finalObj
		top = sorted(obj[stat].items(), key=self.get_val, reverse=most)
		final_freq = self.get_val(top[4]) if len(top) >= 5 else (0 if most else float("inf"))
		print(label)
		for item in top:
			if (most and self.get_val(item) < final_freq) or (not most and self.get_val(item) > final_freq):
				break
			process_item(item, "gameTimes" in stat, cacheManager)

	def get_val(self, item):
		return item[1]["val"]

	def get_player_name(self, player, _, cacheManager):
		playerObj = cacheManager.get_player(player[0])
		team_print = ", ".join(player[1]['teams'])
		print(f"{playerObj['first_name']} {playerObj['last_name']}: {self.get_val(player)} ({team_print})")

	def get_game_info(self, game, isTime, cacheManager):
		boxscore = cacheManager.get_boxscore(game[0])
		dateString = boxscore["gameBoxInfo"][-1]["label"]
		away = boxscore["teamInfo"]["away"]["abbreviation"]
		home = boxscore["teamInfo"]["home"]["abbreviation"]
		value = self.get_val(game)
		if isTime:
			hour = int(value/60)
			minute = value - 60 * hour
			value = f"{hour}:{'%02d' % minute}"
		print(f"{dateString} {away} vs. {home}: {value}")

	def get_venue_info(self, venue, _, __):
		print(f"{venue[0]}: {self.get_val(venue)}")

	def get_team_info(self, team, _, __):
		team_code = constants.teamCodeReverseLookup[team[0]]
		team_obj = team[1]
		homeWins = team_obj["homeWins"]
		homeLosses = team_obj["homeLosses"]
		awayWins = team_obj["awayWins"]
		awayLosses = team_obj["awayLosses"]
		home_record = f"{homeWins}-{homeLosses}"
		away_record = f"{awayWins}-{awayLosses}"
		total_record = f"{homeWins+awayWins}-{homeLosses+awayLosses}"
		print(f"{team_code}: {home_record} Home, {away_record} Away ({total_record} Total; {self.get_val(team)} Games)")