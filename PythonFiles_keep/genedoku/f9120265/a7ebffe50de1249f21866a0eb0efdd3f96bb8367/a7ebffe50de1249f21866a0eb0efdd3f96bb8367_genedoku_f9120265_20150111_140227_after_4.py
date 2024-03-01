import math 

def transpose(m):
	# Transpose matrix (keeping list type on each column, tuples aren't useful on this approach)
	return [list(i) for i in zip(*m)]

def toggle_subgroups(m):
	l = len(m)
	subgroup_l = int(math.sqrt(l))
	res = [[0 for j in range(l)] for i in range(l)]
	for i in range(l):
		for j in range(len(m[i])):
			# IMPORTANT: / operator it's INTEGER division when both operands are integers
			row,col = convert_positions_to_subgroups(i,j,subgroup_l)
			res[row][col] = m[i][j]
	return res

def convert_positions_to_subgroups(i,j,subgroup_l):
	row = subgroup_l * (i/subgroup_l) + (j/subgroup_l)
	col = subgroup_l * (i%subgroup_l) + (j%subgroup_l)
	return row,col

def unique_values(v):
	return list(set(v))
