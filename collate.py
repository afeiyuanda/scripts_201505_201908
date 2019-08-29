import glob

def get_2list_intersection(l1, l2):
	l3 = [i for i in l1 if i in l2]
	return l3

def get_multi_list_intersection(big_list):
	while len(big_list)>1:
		l1 = big_list.pop()
		l2 = big_list.pop()
		l3 = get_2list_intersection(l1, l2)
		if len(l3)>0:
			big_list.append(l3)
	return big_list[0]

files = glob.glob('*.xls')
files = sorted(files)
all_go_list = []
for f in files:
	temp_list = []
	for line in open(f):
		#go = ' '.join(line.strip().split(' ')[1:])
		go = line.strip().split('\t')[1]
		if go not in temp_list:
			temp_list.append(go)
	print len(temp_list)
	all_go_list.append(temp_list)

all_go_list_intersection = get_multi_list_intersection(all_go_list)
print len(all_go_list_intersection)

go_stat_list = []
for ago in all_go_list_intersection:
	temp_list = []
	for f in files:
		for line in open(f):
			#go = ' '.join(line.strip().split(' ')[1:])
			go = line.strip().split('\t')[1]
			if go == ago:
				if go not in temp_list:
					temp_list.append(go)
				temp_list.append(line.strip().split('\t')[-1])
				break
	go_stat_list.append(temp_list)

out = open('go_stat.xls', 'w')
out.writelines('\t'.join(['GO']+['K'+str(i) for i in range(1,6)])+'\n')
for go in go_stat_list:
	out.writelines('\t'.join(go)+'\n')
out.close()