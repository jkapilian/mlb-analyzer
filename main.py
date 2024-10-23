import statsapi
import argparse
import csv

def build_analysis(args):
	with open(args.file) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			print(row)
	pass

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="MLB Analyzer")
	parser.add_argument('-f', '--file', help="CSV of Attendance Data", required=True)
	parser.add_argument('-y', '--year', nargs='+', default=[], help="Years Highlight")
	args = parser.parse_args()
	build_analysis(args)