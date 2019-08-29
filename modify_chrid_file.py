#-*- coding=utf-8 -*-
#!/usr/bin/env python
#用来处理重测序参考基因组中的文件chr_id.txt，如果包含chr、Chr，则把其他的Scaffold去掉

import glob

if __name__ == '__main__':
    chr_file_path = '/share/nas4/dengdj/Research/DNA/Database_donghs/*/chr_id.txt'
    chr_file_list = glob.glob(chr_file_path)
    for chr_file in chr_file_list:
        contain_chr_flag = 0
        chr_name_list = []
        for line in open(chr_file):
            if line.startswith('#'):
                pass
            else:
                chr_name_list.append(line.split('\t')[0])
        new_chr_name_list = [i for i in chr_name_list if 'chr' in i or 'Chr' in i]
        
        if (len(chr_name_list) - len(new_chr_name_list)) >= 1 and len(new_chr_name_list)>=2:
            contain_chr_flag = 1
            new_chr_file = chr_file+'.new'
            new_chr_file_handle = open(new_chr_file, 'w')
            print chr_file
        if contain_chr_flag == 1:
            for line in open(chr_file):
                if line.startswith('#'):
                    new_chr_file_handle.write(line)
                elif line.startswith('Chr') or line.startswith('chr'):
                    new_chr_file_handle.write(line)
                else:
                    pass
            new_chr_file_handle.close()