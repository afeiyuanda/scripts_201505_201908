#-*- coding=utf-8 -*-
#!/usr/bin/env python
'''
统计按疾病分完类之后的每个文件中的数据量、是否可用、项目数目、实验数目
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
    newParser.add_argument( '-infile', dest='infile', help='allsrna.txt', default='/share/nas1/liuw/sra_exp_summary/all_exp_new/seq_by_disease/Surgical_Wound.xls' );
    newParser.add_argument( '-runindex', dest='runindex',type=int, help='runindex', default=21 );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    runindex = argsDict['runindex']
    
    disease = os.path.basename(infile).split('.')[0]
    disease_new_name = disease.replace('===', ' ')
    disease_new_name = disease_new_name.replace("+++", "'")
    
    disease_related_bases = 0
    bioexperiment_list = []
    bioproject_list = []
    
    disease_related_bases_public = 0
    bioexperiment_list_public = []
    bioproject_list_public = []
    if os.path.getsize(infile) == 0:
        pass
    else:
        for line in open(infile).readlines():
            line_list = line.strip().split('\t')
            bioexperiment = line_list[0]
            bioproject = line_list[10]
            access = line_list[22]
            run_info = line_list[runindex]
            if access == 'PublicAccess':
                bioexperiment_list_public.append(bioexperiment)
                if bioproject not in bioproject_list_public:
                    bioproject_list_public.append(bioproject)
                else:
                    pass
                try:
                    base = get_exp_multi_run_bases(run_info)
                    disease_related_bases_public += base
                except:
                    pass
            else:
                bioexperiment_list.append(bioexperiment)
                if bioproject not in bioproject_list:
                    bioproject_list.append(bioproject)
                else:
                    pass
                run_info = line_list[runindex]
                #print run_info
                try:
                    base = get_exp_multi_run_bases(run_info)
                    disease_related_bases += base
                except:
                    pass
        outfile_handle = open(infile+'.stat', 'w')
        outfile_handle.write(disease_new_name+'\t'+str(len(bioproject_list_public))+'\t'+str(len(bioexperiment_list_public))+'\t'+str(disease_related_bases_public)+'\t'+str(len(bioproject_list))+'\t'+str(len(bioexperiment_list))+'\t'+str(disease_related_bases)+'\t'+','.join(bioproject_list_public)+'\t'+','.join(bioexperiment_list_public)+'\t'+','.join(bioproject_list)+'\t'+','.join(bioexperiment_list)+'\n')
        outfile_handle.close()
