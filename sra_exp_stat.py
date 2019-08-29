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
    newParser.add_argument( '-infile', dest='infile', help='allsrna.txt', default='/share/nas1/liuw/yaoyao/allsrna.txt' );
    newParser.add_argument( '-outdir', dest='outdir', help='outdir', default=os.getcwd() );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    infile = argsDict['infile']
    outdir = argsDict['outdir']
    #ERX1430228	454 GS FLX+ sequencing	endophyte bacterium 01	305909	GENOMIC	AMPLICON	454 GS FLX+	SINGLE	SAMEA3928356	PRJEB7624	405776	351967	2016-04-15
    stat_dic = {}
    #stat_dic = {genus_name1:[{AMPLICON:100,WGS:100},[bioproject1,bioproject2],[biosample1,biosample2], }
    instrument_year_dic = {}
    instrument_base_dic = {}
    #instrument_year_dic = {ins1:{year1:100,year2:100}, ins2:{year1:100,year2:100}}
    strategy_list = []
    year_list = []
    for line in open(infile):
        line_list = line.strip().split('\t')
        bioexperiment = line_list[0]
        #genus_name = get_genus_name(line_list[2])
        genus_name = line_list[2]
        strategy = line_list[5]
        source = line_list[4]
        instrument = line_list[6]
        layout = line_list[7]
        biosample = line_list[8]
        bioproject = line_list[9]
        if line_list[10]=='null':
            base = 0
        else:
            base = float(line_list[10])/1000000000
        filesize = line_list[11]
        #为了进行排序，因此转换为int型
        release_year = int(get_year(line_list[12]))
        
        new_append(strategy_list, strategy)
        new_append(year_list, release_year)
        
        if genus_name not in stat_dic.keys():
            stat_dic[genus_name] = []
            strategy_dic = {}
            strategy_dic[strategy] = base
            stat_dic[genus_name].append(strategy_dic)
            
            layout_dic = {}
            layout_dic[layout] = base
            stat_dic[genus_name].append(layout_dic)
        elif genus_name in stat_dic.keys() and strategy not in stat_dic[genus_name][0].keys():
            stat_dic[genus_name][0][strategy] = base
            try:
                stat_dic[genus_name][1][layout] += base
            except:
                stat_dic[genus_name][1][layout] = 0
                stat_dic[genus_name][1][layout] += base
        else:
            stat_dic[genus_name][0][strategy] += base
            try:
                stat_dic[genus_name][1][layout] += base
            except:
                stat_dic[genus_name][1][layout] = 0
                stat_dic[genus_name][1][layout] += base
        
        try:
            new_append(stat_dic[genus_name][2], bioproject)
            new_append(stat_dic[genus_name][3], biosample)
            new_append(stat_dic[genus_name][4], bioexperiment)
        except:
            #初始化三个空列表，分别用于存放项目、样品、实验
            stat_dic[genus_name].append([])
            stat_dic[genus_name].append([])
            stat_dic[genus_name].append([])
            new_append(stat_dic[genus_name][2], bioproject)
            new_append(stat_dic[genus_name][3], biosample)
            new_append(stat_dic[genus_name][4], bioexperiment)
    
        if instrument not in instrument_year_dic.keys():
            instrument_year_dic[instrument] = {}
            instrument_year_dic[instrument][release_year] = base
            instrument_base_dic[instrument] = base
        elif instrument in instrument_year_dic.keys() and release_year not in instrument_year_dic[instrument].keys():
            instrument_year_dic[instrument][release_year] = base
            instrument_base_dic[instrument] += base
        else:
            instrument_year_dic[instrument][release_year] += base
            instrument_base_dic[instrument] += base
            
            
    #print stat_dic
    print instrument_year_dic
    genus_strategy_outfile = outdir+'/genus_strategy.xls'

    genus_strategy_outfile_handle = open(genus_strategy_outfile, 'w')
    #strategy_list = ["AMPLICON","ATAC-seq","Bisulfite-Seq","CLONE","CLONEEND","CTS","ChIA-PET","ChIP","ChIP-Seq","DNase-Hypersensitivity","EST","FAIRE-seq","FINISHING","FL-cDNA","Hi-C","MBD-Seq","MNase-Seq","MRE-Seq","MeDIP-Seq","OTHER","POOLCLONE","RAD-Seq","RIP-Seq","RNA-Seq","SELEX","Synthetic-Long-Read","Targeted-Capture","Tethered Chromatin Conformation Capture","Tn-Seq","VALIDATION","WCS","WGA","WGS","WXS","miRNA-Seq","ncRNA-Seq","other"]
    title = 'Genus\t'+'\t'.join(strategy_list)+'\tTotalBase\tPAIRED\tSINGLE\tBioPrject\tBioSample\tBioExperiment\n'
    genus_strategy_outfile_handle.write(title)

    genus_base_dic = {}
    total_base = 0
    total_paired_base = 0
    total_single_base = 0
    total_project = 0
    total_sample = 0
    total_experiment = 0
    for k,v in stat_dic.items():
        #print 'k:%s\nv:%s' % (k,v)
        genus_sta_line = k+'\t'
        genus_base_dic[k]=[]
        genus_total_base = 0
        for s in strategy_list:
            if s in v[0].keys():
                genus_sta_line += str(v[0][s])+'\t'
                genus_total_base += v[0][s]
            else:
                genus_sta_line += '-\t'
                
        total_base += genus_total_base
        genus_sta_line += str(genus_total_base)+'\t'
        genus_base_dic[k].append(genus_total_base)
        
        if v[1].has_key('PAIRED'):
            total_paired_base += v[1]['PAIRED']
            genus_sta_line += str(v[1]['PAIRED'])+'\t'
            genus_base_dic[k].append(v[1]['PAIRED'])
        else:
            genus_sta_line += '\t'
            genus_base_dic[k].append('')
            
        if v[1].has_key('SINGLE'):
            total_single_base += v[1]['SINGLE']
            genus_sta_line += str(v[1]['SINGLE'])+'\t'
            genus_base_dic[k].append(v[1]['SINGLE'])
        else:
            genus_sta_line += '\t'
            genus_base_dic[k].append('')
            
        total_project += len(v[2])
        total_sample += len(v[3])
        total_experiment += len(v[4])
        
        genus_sta_line += str(len(v[2]))+'\t'
        genus_sta_line += str(len(v[3]))+'\t'
        genus_sta_line += str(len(v[4]))
        genus_strategy_outfile_handle.write(genus_sta_line + '\n')
        
        genus_base_dic[k].append(str(len(v[2])))
        genus_base_dic[k].append(str(len(v[3])))
        genus_base_dic[k].append(str(len(v[4])))
    
    genus_strategy_outfile_handle.close()
    '''
    #print genus_base_dic
    sorted_genus_base_dic = sorted(genus_base_dic.items(), key=lambda x:x[1][0], reverse=True)

    genus_strategy_outfile_top50 = outdir+'/genus_strategy_top50.xls'
    genus_strategy_outfile_top50_handle = open(genus_strategy_outfile_top50, 'w')
    title_top50 = 'Genus\tTotalBase\tPAIRED\tSINGLE\tBioPrject\tBioSample\tBioExperiment\n'
    genus_strategy_outfile_top50_handle.write(title_top50)
    for (k,v) in sorted_genus_base_dic[0:50]:
        line = k+'\t'+'\t'.join([str(i) for i in v])
        genus_strategy_outfile_top50_handle.write(line+'\n')
    genus_strategy_outfile_top50_handle.write('\n')
    genus_strategy_outfile_top50_handle.write('Total\t'+str(total_base)+'\t'+str(total_paired_base)+'\t'+str(total_single_base)+'\t'+str(total_project)+'\t'+str(total_sample)+'\t'+str(total_experiment))
    
    instrument_year_outfile = outdir + '/instrument_year.xls'
    instrument_year_outfile_handle = open(instrument_year_outfile, 'w')
    #instrument_year_dic = {ins1:{year1:100,year2:100}, ins2:{year1:100,year2:100}}
    
    sorted_year_list = sorted(year_list)
    instrument_year_outfile_handle.write('Instrument\t'+'\t'.join([str(i) for i in sorted_year_list])+'\tTotal\n')
    for k,v in instrument_year_dic.items():
        instrument_year_line = k + '\t'
        for year in sorted_year_list:
            if year in v.keys():
                instrument_year_line += str(v[year])+'\t'
            else:
                instrument_year_line += '-\t'
        instrument_year_line += str(instrument_base_dic[k])+'\n'
        instrument_year_outfile_handle.write(instrument_year_line)

    genus_strategy_outfile_top50_handle.close()
    instrument_year_outfile_handle.close()
    '''