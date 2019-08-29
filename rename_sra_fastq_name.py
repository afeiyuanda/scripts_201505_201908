#-*-coding:utf-8-*-
'''
Author:    Liu wei
Data:    2018.01.15
'''
#need fastq.py
import os,sys,re,argparse
from fastq import MinimalFastqParser

def __main__():
    try:
        input_seqs_ul = sys.argv[1]
    except:
        sys.exit(1)
    
    infile_name = os.path.basename(input_seqs_ul)
    outfile_name = infile_name + '.tmp'
    output_fq =  os.path.dirname(input_seqs_ul) + '/'+outfile_name
    outf = open( output_fq , 'w')

    for seq_id, seq, qual in MinimalFastqParser(input_seqs_ul, strict=False):
        # @/share/bioCloud/cloud/rawdata/download/PRJDA50447/DRX000300/DRR000534.sra.12 HWI-EAS370_34:2:1:0:82 length=76
        seq_id_spot_info = re.split('\s+', seq_id)[1]
        if '_1.fastq' in infile_name:
            new_seq_id = seq_id_spot_info+'/1'
        elif '_2.fastq' in infile_name:
            new_seq_id = seq_id_spot_info+'/2'
        else:
            new_seq_id = seq_id_spot_info
        outf.write('@%s\n%s\n+\n%s\n' % (new_seq_id, seq, qual))
    outf.close()
    os.system('mv %s %s' % (input_seqs_ul, input_seqs_ul+'.bak'))
    os.system('mv %s %s' % (output_fq, input_seqs_ul))
if __name__ == "__main__" : __main__()