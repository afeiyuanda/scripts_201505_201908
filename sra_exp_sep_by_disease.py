#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse

def get_genus_name(species):
    species_list = species.split(' ')
    if 'metagenome' in species:
        genus_name = 'metagenome'
    elif '.' in species_list[0]:
        genus_name = ' '.join(species_list[0:2])
    else:
        genus_name = species_list[0]
    return genus_name

def new_append(l, i):
    if i not in l:
        l.append(i)
    else:
        pass
    return l

def get_year(rd):
    return rd.split('-')[0]
    
if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -infile allsrna.txt\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-infile', dest='infile', help='exp file', default='/share/nas1/liuw/sra_exp_summary/all_exp_new/all_exp_dedup.xls' );
    newParser.add_argument( '-disease', dest='disease', help='disease category file', default='/share/nas1/liuw/sra_exp_summary/all_exp_new/new_code' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    disease = argsDict['disease']
    '''
    big_dic = {}
    for line in open(disease).readlines():
        line_list = line.strip().split('\t')
        disease_code, disease_name, synonym = line_list[0], line_list[1], line_list[2]
        keywords = []
        if synonym == 'null':
            keywords.append(disease_name)
        else:
            keywords.append(disease_name)
            keywords.extend(synonym.split(';'))
        #print keywords
        for exp_line in open(infile).readlines():
            for k in keywords:
                try:
                    pattern = re.compile('[ ,\.]'+k+'[ ,\.]', re.I)
                    if pattern.search(exp_line):
                        big_dic.setdefault(keywords[0], []).append(exp_line)
                        break
                except:
                    pass
    outdir = os.path.dirname(infile)
    infile_name = os.path.basename(infile)
    new_outdir = outdir+'/'+infile_name+'_dir'
    os.system('mkdir -p %s' % new_outdir)
    #print big_dic
    for k,v in big_dic.items():
        disease_new_name = k.replace(' ', '===')
        disease_new_name = disease_new_name.replace("'", '+++')
        outfile_name = new_outdir+'/'+disease_new_name+'.xls'
        outfile_name_handle = open(outfile_name, 'w')
        outfile_name_handle.writelines(v)
        outfile_name_handle.close()
    '''


    big_dic = {}
    for line in open(disease).readlines():
        line_list = line.strip().split('\t')
        disease_name, synonym = line_list[1], line_list[2]
        keywords = synonym.split(';')
        print 'keywords: %s' % keywords
        for exp_line in open(infile).readlines():
            for k in keywords:
                try:
                    pattern = re.compile('[ ,\.]'+k+'[ ,\.]', re.I)
                    if pattern.search(exp_line):
                        big_dic.setdefault(keywords[0], []).append(exp_line)
                        break
                except:
                    pass
    outdir = os.path.dirname(infile)
    infile_name = os.path.basename(infile)
    new_outdir = outdir+'/'+infile_name+'_dir'
    os.system('mkdir -p %s' % new_outdir)
    #print big_dic
    for k,v in big_dic.items():
        disease_new_name = k.replace(' ', '_')
        outfile_name = new_outdir+'/'+disease_new_name+'.xls'
        outfile_name_handle = open(outfile_name, 'w')
        outfile_name_handle.writelines(v)
        outfile_name_handle.close()
