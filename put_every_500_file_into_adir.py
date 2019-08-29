#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse,glob

def make_dir(prefix, suffix):
    new_dir = prefix+'/'+suffix
    os.system('mkdir -p '+new_dir)
    return new_dir

if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -indir indir_containing_xml\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-indir', dest='indir', help='indir containing xml', default='/share/nas1/xiayh/06.databaseAccess/New_method/Data_Exper_AND_Project_New_only_ID/data_exper/20171205' );
    newParser.add_argument( '-num', dest='num', type=int, help='n file number will be separated into 1 dir', default='500' );
    newParser.add_argument( '-outdir', dest='outdir', help='outdir', default=os.getcwd() );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    indir = argsDict['indir']
    num = argsDict['num']
    outdir = argsDict['outdir']+'/separated_dir'
    cut_num = 0
    init_num = num
    new_dir = make_dir(outdir, str(cut_num))
    for xml_file in glob.glob(indir+'/*.xml'):
        if num>0:
            os.system('cp %s %s' % (xml_file, new_dir))
            num-=1
        else:
            cut_num += 1
            new_dir = make_dir(outdir, str(cut_num))
            num = init_num-1
            os.system('cp %s %s' % (xml_file, new_dir))
            