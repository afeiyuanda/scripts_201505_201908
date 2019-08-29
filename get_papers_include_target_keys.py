#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse


if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -infile allsrna.txt\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-infile', dest='infile', help='pubmed file', default='Ten_Years.paper.16-18.xls' );
    newParser.add_argument( '-outfile', dest='outfile', help='outfile', default='paper_ngs.xls' );

    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    outfile = argsDict['outfile']
    keywords = ["sequencing","\s+NGS","high throughput seq","Next generation seq","-seq","\s+wgs\s+","metagenome","Metatranscriptomic", "transcriptome seq"] #去掉包含 "sanger seq"
    #keywords = ["Lung Neoplasms Pulmonary Neoplasms","Lung Cancer","Pulmonary Cancer","Cancer of the Lung","Cancer of Lung"]
    #keywords = ["Neoplasia","Tumors","Cancer","Malignant Neoplasms","Malignancy","Malignancies","Benign Neoplasms"]
    outfile_handle = open(outfile, 'w')
    for line in open(infile).readlines():
        line_list = line.split('\t')
        title = line_list[1]
        abs = line_list[2]
        for k in keywords:
             pattern = re.compile(k, re.I)
             if pattern.search(title+' '+abs):
                outfile_handle.write(line)
                break
    outfile_handle.close()
