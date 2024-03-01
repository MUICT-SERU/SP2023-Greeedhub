import argparse
import math
import sys
import os
from genedoku.Evolution import Evolution
from genedoku.SudokuChromosome import SudokuChromosome

parser = argparse.ArgumentParser(description='Resolve sodokus using Genetic Algorithm')
parser.add_argument('--initial-length', default=50, help='length of the initial generation')
parser.add_argument('--max-generations', default=20000, help='max number of generations')

args = vars(parser.parse_args())

def main():
	problem = []
	row = raw_input().strip()
	while row != "":
		problem.append(row.split(" "))
		row = raw_input().strip()

	# Check the input
	sub_length = math.sqrt(len(problem))
	if sub_length != round(sub_length):
		print "Wrong length on input"
		sys.exit(1)

	for r in problem:
		if len(r) != len(problem):
			print "Wrong length on input"
			sys.exit(1)

	# Convert to type int
	for r in range(len(problem)):
		for c in range(len(problem[r])):
			problem[r][c] = int(problem[r][c])

	e = Evolution(problem, SudokuChromosome, args['initial_length'], args['max_generations'])
	print "Starting..."
	r = e.start()
	print "Finished! Result found solution at generation",e.gen,"with",r.evaluate(),"errors:"
	for r in r._value:
		for c in r:
			print c," ",
		print ""

if __name__ == '__main__':
	main()
