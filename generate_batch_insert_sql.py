#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse,glob

if __name__ == '__main__':
    description = 'Find file and tools connection based on the file attributs and t_cwl_soft!\n'
    quick_usage = 'python '+sys.argv[0]+' -sql xx.sql -outdir /output/dir/ \n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-sql', dest='sql', help='input sql file' );
    newParser.add_argument( '-cut', dest='cut', help='cut, default 1000',type=int, default=1000);
    newParser.add_argument( '-outdir', dest='outdir', help='outdir' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    sql_file = argsDict['sql']
    cut = argsDict['cut']
    outdir = argsDict['outdir']
    outfile = outdir+'/'+os.path.basename(sql_file)
    out = open(outfile, 'w')
    count1 = 0
    count2 = 0
    count3 = 0 
    count4 = 0 
    total_count = 0
    s1 = 'insert into t_file_data (created_date, data_uuid, location, size, status, storage_type) values '
    s2 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, recycle) values '
    s3 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, type, data_uuid, pid, recycle) values '
    for line in open(sql_file):
        if line.split(' ')[2]=='t_file_data' and count1<cut:
            count1 += 1
            value_str = line.rstrip('\n').rstrip(';').split(' values ')[1]
            s1 = s1+' '+value_str+', '
        elif line.split(' ')[2]=='t_file_data' and count1==cut:
            total_count += count1
            out.writelines(s1.rstrip(' ').rstrip(',') + ';\n')
            s1 = 'insert into t_file_data (created_date, data_uuid, location, size, status, storage_type) values '
            value_str = line.rstrip('\n').rstrip(';').split(' values ')[1]
            s1 = s1+' '+value_str+', '
            count1 = 1
        
        elif line.split(' ')[2]=='t_file' and ' size,' in line and count2<cut:
            count2 += 1
            value_str = line.rstrip('\n').rstrip(';').split(' values ')[1]
            s2 = s2+' '+value_str+', '
        elif line.split(' ')[2]=='t_file' and ' size,' in line and count2==cut:
            total_count += count2
            out.writelines(s2.rstrip(' ').rstrip(',')  + ';\n')
            s2 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, recycle) values '
            value_str = line.rstrip('\n').rstrip(';').split(' values ')[1]
            s2 = s2+' '+value_str+', '
            count2 = 1

        elif line.split(' ')[2]=='t_file' and ' size,' not in line and count3<cut:
            count3 += 1
            value_str = line.rstrip('\n').rstrip(';').split(' values ')[1]
            s3 = s3+' '+value_str+', '
        elif line.split(' ')[2]=='t_file' and ' size,' not in line and count3==cut:
            total_count += count3
            out.writelines(s3.rstrip(' ').rstrip(',')  + ';\n')
            s3 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, type, data_uuid, pid, recycle) values '
            value_str = line.rstrip('\n').rstrip(';').split(' values ')[1]
            s3 = s3+' '+value_str+', '
            count3 = 1
        else:
            count4 += 1
    total_count += count1
    total_count += count2
    total_count += count3
    out.writelines(s1.rstrip(' ').rstrip(',') + ';\n')
    out.writelines(s2.rstrip(' ').rstrip(',') + ';\n')
    out.writelines(s3.rstrip(' ').rstrip(',') + ';\n')
    out.close()
    print total_count
    print count4