import json
import statsapi
import constants

class CacheManager:
	boxscores = {}
	gameIds = {}
	players = {}

	def __init__(self, input):
		if input:
			with open(input, "r") as inputfile:
				jsonFile = json.load(inputfile)
				self.boxscores = jsonFile["boxscores"]
				self.gameIds = jsonFile["gameIds"]
				self.players = jsonFile["players"]

	def get_boxscore(self, gameId):
		if str(gameId) not in self.boxscores:
			self.boxscores[str(gameId)] = statsapi.boxscore_data(gameId)
		return self.boxscores[str(gameId)]
	
	def get_game_id(self, row):
		home_team = row[0]
		date = row[1]
		team_code = constants.teamCodes[home_team]
		if str(team_code) in self.gameIds and date in self.gameIds[str(team_code)]:
			games = self.gameIds[str(team_code)][date]
		else: 
			games = statsapi.schedule(date=date, team=team_code)
			if str(team_code) in self.gameIds:
				self.gameIds[str(team_code)][date] = games
			else:
				self.gameIds[str(team_code)] = {
					date: games
				}
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
	
	def get_player(self, playerId):
		if str(playerId) in self.players:
			return self.players[str(playerId)]
		else: 
			player = statsapi.player_stat_data(playerId)
			self.players[str(playerId)] = player
			return player
	
	def export_cache(self, output):
		if output:
			with open(output, "w") as outputfile:
				newObj = {
					"boxscores": self.boxscores,
					"gameIds": self.gameIds,
					"players": self.players
				}
				outputfile.write(json.dumps(newObj))