#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse,glob,json
reload(sys);
exec("sys.setdefaultencoding('utf-8')");

#select species_ch,species_en,assemble,species_address,use_perm from t_species where software_id='8a817f674fd9e535014fda7080080a9b' and main_process_version='v2.0' ;

if __name__ == '__main__':
    description = ''
    quick_usage = 'python '+sys.argv[0]+' -user_name 8a817f674d663d1e014d7aec4a2b52f2\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-database_path', dest='database_path', help='database_path', default='/share/nas2/database/genome/' );
    newParser.add_argument( '-ref_list', dest='ref_list', help='ref_list', default='/share/nas1/liuw/ref_v2_species.txt' );
    newParser.add_argument( '-outfile', dest='outfile', help='outfile', default='./all_ref_full.txt' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    database_path = argsDict['database_path']
    ref_list = argsDict['ref_list']
    outfile = argsDict['outfile']
    
    outhandle = open(outfile, 'w')
    
    gene_pattern = re.compile(r'.*\sgene\s.*', re.I)
    pattern_id = re.compile(r'.*ID=([\w\-_\.:]+)[;\s]*.*')
    
    outhandle.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % ('species_ch', 'species_en', 'assemble', 'authority', 'gene_id','gene_name', 'download_url'))
    for line in open(ref_list):
        if line.startswith('#'):
            pass
            outhandle.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % ('species_ch', 'species_en', 'assemble', 'authority', 'gene_id','gene_name', 'download_url'))
        else:
            ref_ch_name = line.strip().split('\t')[0]
            ref_en_name = line.strip().split('\t')[1]
            ref_version = line.strip().split('\t')[2]
            use_perm = line.strip('\n').split('\t')[4]
            authority = (use_perm=='') and 'public' or 'control'
            #print authority
            '''
            species_address_dic = json.loads(line.strip().split('\t')[3])
            gff_file = species_address_dic['Ref_ann']
            species_address = os.path.dirname(gff_file)
            '''
            species_address = '/share/nas2/database/genome/'+ref_en_name+'/'+ref_version
            id_name_file_path = '%s/id_name.list' % (species_address)
            print id_name_file_path
            download_file = '%s/source.bak/readme.txt' % (species_address)
            #print gff_file
            url_list = []
            if os.path.exists(download_file):
                lines = open(download_file).readlines()
                for l in lines:
                    if 'ftp' in l or 'http' in l or 'www' in l:
                        url_list_temp = [i for i in re.split('\s+', l) if i.startswith('ftp') or i.startswith('http') or i.startswith('www')]
                        url_list.extend(url_list_temp)
            if os.path.exists(id_name_file_path) and os.path.getsize(id_name_file_path) > 20:
                id_name_lines = open(id_name_file_path).readlines()
                for id_name_line in id_name_lines:
                    if id_name_line.startswith('#') or id_name_line.strip().split('\t')[1]=='--':
                        pass
                    else:
                        first_id_name_line = id_name_line
                            
                if first_id_name_line.strip().split('\t')[0] == first_id_name_line.strip().split('\t')[1]:
                    new_line = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (ref_ch_name, ref_en_name, ref_version, authority,first_id_name_line.strip().split('\t')[0], 'null', ','.join(url_list))
                else:
                    new_line = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (ref_ch_name, ref_en_name, ref_version, authority, first_id_name_line.strip().split('\t')[0], first_id_name_line.strip().split('\t')[1], ','.join(url_list))
            else:
                gff_file = glob.glob(species_address+'/*.gff3')[0]
                for line in open(gff_file):
                    if gene_pattern.match(line) and pattern_id.match(line):
                        gene_id = pattern_id.match(line).group(1)
                        break
                new_line = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (ref_ch_name, ref_en_name, ref_version, authority, gene_id, 'null', ','.join(url_list))
            outhandle.write(new_line)            
    outhandle.close()
