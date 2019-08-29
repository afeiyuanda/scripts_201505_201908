#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse

def get_run_bases(run_info):
    if run_info and run_info.split(';')[0].split(',')[1] != '':
        return 1
    else:
        return 0

if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -infile allsrna.txt\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-infile', dest='infile', help='allsrna.txt', default='all_exp.xls' );
    #newParser.add_argument( '-outfile', dest='outfile', help='dedup.txt', default='all_exp_dedup.xls' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    outfile = infile+'.dedup'
    outfile_handle = open(outfile, 'w')
    exp_list=[]
    for line in open(infile):
        bioexperiment = line.strip().split('\t')[0]
        #print line.strip().split('\t')[21]
        if bioexperiment not in exp_list:
            exp_list.append(bioexperiment)
            outfile_handle.write(line)
    outfile_handle.close()
    #print "%s has total exp is : %s" % (infile, len(exp_list))
        
