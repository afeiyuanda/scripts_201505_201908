#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse


if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -infile allsrna.txt\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-infile', dest='infile', help='pubmed file', default='Ten_Years.paper.16-18.xls' );
    newParser.add_argument( '-outfile', dest='outfile', help='outfile', default='paper_china.xls' );

    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    outfile = argsDict['outfile']
    keywords = ["Anhui","Beijing","Chongqing","Fujian","Gansu","Guangdong","Guangxi","Guizhou","Hainan","Hebei","Heilongjiang","Henan","Hong Kong","Hubei","Hunan","Jiangsu","Jiangxi","Jilin","Liaoning","Macau","Inner Mongol","Ningxia","Qinghai","Shandong","Shanxi","Shaanxi","Shanghai","Sichuan","Taiwan","Tianjin","Tibet","Sinkiang","Yunnan","Zhejiang"]
    outfile_handle = open(outfile, 'w')
    for line in open(infile).readlines():
        line_list = line.split('\t')
        first_author = line_list[3]
        correspond_author = line_list[4]
        for k in keywords:
             pattern = re.compile(k, re.I)
             if pattern.search(first_author+' '+correspond_author):
                outfile_handle.write(line)
                break
    outfile_handle.close()
