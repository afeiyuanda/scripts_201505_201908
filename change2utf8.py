# -*- coding: utf-8 -*- 
import chardet
outf = open('xx.cfg', 'w')
for line in open('ref_trans.detail.cfg'):
    print chardet.detect(line)['encoding'], line
    outf.write(line.decode(chardet.detect(line)['encoding']).encode('utf-8'))
    
outf.close()