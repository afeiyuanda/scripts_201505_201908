#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse,glob
reload(sys) 
sys.setdefaultencoding('utf8')

def is_target_line(line):
    pattern = re.compile(r'^(\d+)!!!!!(.*)\@\@\@\@\@(.*)\$\$\$\$\$(.*)\*\*\*\*\*(.*)%%%%%(.*)\&\&\&\&\&(.*)\^\^\^\^\^(.*)$')
    pm = pattern.match(line)
    pm_list = pm.groups()
    pmid = pm_list[0]
    title = pm_list[1]
    abs_authors = pm_list[2]
    keywords = pm_list[4]
    IF_magazine = pm_list[5]
    publish_date = pm_list[6]
    publish_year = re.split('\s+', publish_date)[-1]
    abs = abs_authors.split('#####')[0]
    authors_list = abs_authors.split('#####')[1:-1]
    first_author = abs_authors.split('#####')[1]
    correspond_author = abs_authors.split('#####')[-2]
    if publish_year in ['2017', '2018', '2016']:
        return '\t'.join([pmid, title, abs, first_author, correspond_author, keywords, IF_magazine, publish_date])+'\n'
    else:
        return ''

if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -infile Ten_Years.paper\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-infile', dest='infile', help='Ten_Years.paper', default='Ten_Years.paper' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    outfile = infile+'.16-18.xls'
    outfile_handle = open(outfile, 'w')
    
    for line in open(infile):
        if is_target_line(line):
            outfile_handle.write(is_target_line(line))
    outfile_handle.close()