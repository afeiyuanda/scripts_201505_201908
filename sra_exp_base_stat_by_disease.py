#-*- coding=utf-8 -*-
#!/usr/bin/env python
'''
统计1个文件中包含不同疾病关键词的数据量、是否可用、项目数目、实验数目
'''
import re,os,sys,argparse

def get_exp_multi_run_bases(run_info):
    if run_info:
        return sum([float(i.split(',')[1])/1000000000 for i in run_info.split(';') if i.split(',')[1]!=''])
        #return sum([int(i.split(',')[1]) for i in run_info.split(';')])
    else:
        return 0
    
if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -infile allsrna.txt\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-infile', dest='infile', help='allsrna.txt', default='/share/nas1/liuw/sra_exp_summary/all_exp_new/all_exp_dedup.xls' );
    newParser.add_argument( '-keywords_file', dest='keywords_file', help='new_code.txt', default='/share/nas1/liz/Paper_Database/new_code' );
    newParser.add_argument( '-runindex', dest='runindex',type=int, help='runindex', default=21 );
    newParser.add_argument( '-outfile', dest='outfile', help='outfile', default='base_stat_by_disease.xls' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    keywords_file = argsDict['keywords_file']
    runindex = argsDict['runindex']
    outfile = argsDict['outfile']
    outfile_handle = open(outfile, 'w')
    #DRX000003	DLD1_normoxia_nucleosome	FL-cDNA	TRANSCRIPTOMIC	SINGLE	Illumina Genome Analyzer	DBTSS:http://dbtss.hgc.jp/	9606	Homo sapiens	DRR000003,232550352,155597364,2010-10-14 00:53:29;DRR000004,218202480,147046970,2010-10-14 00:53:29;DRR000005,217467432,147068738,2010-10-14 00:53:29;DRR000006,213718284,145251596,2010-10-14 00:53:29;DRR000007,126135468,44419930,2010-10-14 00:53:29;DRR000363,1580432724,701100096,2010-10-14 00:53:29;DRR000364,1619455824,733446450,2010-10-14 00:53:29;DRR000365,1634982444,755463631,2010-10-14 00:53:29;DRR000366,1618129332,743442412,2010-10-14 00:53:29	PublicAccess
    for keyword_line in open(keywords_file).readlines():
        keyword = keyword_line.strip().split('\t')[0]
        disease_related_bases = 0
        bioexperiment_list = []
        for line in open(infile).readlines():
            total_base = 0
            if keyword in line:
                line_list = line.strip().split('\t')
                bioexperiment = line_list[0]
                bioexperiment_list.append(bioexperiment)
                run_info = line_list[runindex]
                #print run_info
                try:
                    base = get_exp_multi_run_bases(run_info)
                    total_base += base
                except:
                    pass
                break
            disease_related_bases += total_base
                
        outfile_handle.write(keyword_line.rstrip()+'\t'+'\t'.join([str(disease_related_bases), ','.join(bioexperiment_list)])+'\n')
    outfile_handle.close()
