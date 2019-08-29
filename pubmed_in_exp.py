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
    newParser.add_argument( '-exp_in', dest='exp_in', help='all_exp.xls', default='all_exp.xls' );
    newParser.add_argument( '-pubmed_in', dest='pubmed_in', help='zhangzhiqiang.result', default='zhangzhiqiang.result' );
    newParser.add_argument( '-outfile', dest='outfile', help='dedup.txt', default='pubmed_with_data.xls' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    exp_in = argsDict['exp_in']
    pubmed_in = argsDict['pubmed_in']
    outfile = argsDict['outfile']
    outfile_handle = open(outfile, 'w')
    #exp_full_info_list = [exp_accession, exp_title, study_ref_accession, design_description, sample_accession, library_strategy, library_source, library_selection, library_layout, platform, bioproject, submission_accession, organization, study_title, study_abstract, magazine, biosample, sample_title, taxon_id, taxon_name, sample_attributes, run_info, access, filename]
    for line in open(exp_in):
        line_list = line.split('\t')
        exp_accession, library_strategy, library_source, library_layout, platform, magazine, run_info = line_list[0], line_list[5], line_list[6], line_list[8], line_list[9], line_list[15].split(':')[1], line_list[21]
        for pline in open(pubmed_in):
            pline_list = pline.split('\t')
            try:
                pubmed = pline_list[3]
                if pubmed == magazine:
                    outfile_handle.write('\t'.join(pline_list[0:4]+[exp_accession, library_strategy, library_source, library_layout, platform, magazine, run_info])+'\n')
                    
            except:
                pass
    outfile_handle.close()
    os.system('cat %s | sort | uniq > %s' % (outfile, outfile+'.dedup'))

        
