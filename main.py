import argparse
import csv
import cache_manager
import analysis

def build_analysis(args):
	cacheManager = cache_manager.CacheManager(args.input)
	analysisManager = analysis.Analysis(args)

	with open(args.data) as csvfile:
		reader = csv.reader(csvfile)
		games = 0
		for row in reader:
			try:
				games += 1
				year = row[1].split("/")[-1]
				gameId, otherGameId = cacheManager.get_game_id(row)
				analysisManager.add_game(gameId, otherGameId, cacheManager, year)
			except Exception as e:
				raise Exception(f"Error adding game {row}: {e}")
		try:
			analysisManager.process_final(games, cacheManager)
			cacheManager.export_cache(args.output)
		except Exception as e:
			raise Exception(f"Error printing summary: {e}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="MLB Analyzer")
	parser.add_argument('-d', '--data', help="CSV of Attendance Data", required=True)
	parser.add_argument('-i', '--input', help="CSV of previously analyzed boxscores")
	parser.add_argument('-o', '--output', help="CSV of analyzed boxscores")
	parser.add_argument('-y', '--year', nargs='+', default=[], help="Years Highlight")
	args = parser.parse_args()
	build_analysis(args)