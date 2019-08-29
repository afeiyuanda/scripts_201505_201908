#-*- coding=utf-8 -*-
#!/usr/bin/env python
import os,sys,argparse

def get_proteins(alist):
    return [i.split('\t')[2] for i in alist if not i.startswith('#')]
    
if __name__ == '__main__':
    description = ''
    quick_usage = 'python '+sys.argv[0]+' -user_name 8a828b82518483d30151848a950d05e4\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-protein_file', dest='protein_file', help='protein_file', default='20190613Integrated_Table_mRNA_protein_Anno.txt' );
    newParser.add_argument( '-taxo_id', dest='taxo_id', help='taxo_id', default='9606' );
    newParser.add_argument( '-string_db', dest='string_db', help='string_db', default='/share/nas1/liuw/get_interaction_from_stringdb/' );
    newParser.add_argument( '-outdir', dest='outdir', help='outdir', default='./' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    protein_file = argsDict['protein_file']
    taxo_id = argsDict['taxo_id']
    string_db = argsDict['string_db']
    outdir = argsDict['outdir']
    
    links_file = '%s/%s.protein.links.v11.0.txt' % (string_db, taxo_id)
    actions_file = '%s/%s.protein.actions.v11.0.txt' % (string_db, taxo_id)
    protein_list =  get_proteins(open(protein_file).readlines())
    match_strings = []
    i = 0
    while i<len(protein_list)-1:
        for j in range(i+1,len(protein_list)):
            match_strings.append('%s.%s\t%s.%s' % (taxo_id, protein_list[i], taxo_id, protein_list[j])) 
            match_strings.append('%s.%s\t%s.%s' % (taxo_id, protein_list[j], taxo_id, protein_list[i])) 
        i = i + 1
 
    cmd = 'grep -P "' + '|'.join(match_strings) +'" ' + links_file +' > ' + outdir+'/links_in_proteins.xls'
    os.system(cmd)
    os.system('grep -P "' + '|'.join(match_strings) +'" ' + actions_file +' > ' + outdir+'/actions_in_proteins.xls')
    
    for protein in protein_list:
        links_outfile = outdir+'/'+protein+'_links.xls'
        actions_outfile = outdir+'/'+protein+'_actions.xls'
        os.system('grep -P "' + protein +'" ' + links_file +' > ' + links_outfile)
        os.system('grep -P "' + protein +'" ' + actions_file +' > ' + actions_outfile)