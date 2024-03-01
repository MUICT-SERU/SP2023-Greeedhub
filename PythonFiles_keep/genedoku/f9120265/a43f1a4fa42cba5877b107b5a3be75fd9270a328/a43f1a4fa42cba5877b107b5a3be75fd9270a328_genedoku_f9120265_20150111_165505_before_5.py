import argparse
import math
import sys
from Evolution import Evolution
from Chromosome import Chromosome

parser = argparse.ArgumentParser(description='Resolve sodokus using Genetic Algorithm')
parser.add_argument('--initial-length', default=50, help='stop the agent, use with --kill to remove running jobs')
parser.add_argument('--max-generations', default=10000, help='subnet secret (cached)')

args = vars(parser.parse_args())

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

e = Evolution(problem,args['initial_length'],args['max_generations'])
print "Starting..."
r = e.start()

print "Finished! Result:",r._value,r.evaluate()
