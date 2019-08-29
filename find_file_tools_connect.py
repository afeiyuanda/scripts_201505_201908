#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse,MySQLdb

def combine_file_attributs(base_attributs, expand_attributs_dic):
    #{'058d30ac-2726-4e5c-8997-9c1014448789': [('Processor', 'GATK')]}
    for f in base_attributs:
        file_uuid = f[0]
        file_name = f[1]
        d = {}
        d['FileFormat']=f[2]
        try:
            expand_attributs_dic[file_uuid].append(d)
        except:
            expand_attributs_dic[file_uuid] = []
            expand_attributs_dic[file_uuid].append(d)
    return expand_attributs_dic

def l2_in_l1(l1, l2):
    #l2 包含于 l1 ,返回1
    l1_lower = [i.lower() for i in l1]
    l2_lower = [i.lower() for i in l2]
    l1_lower.sort()
    l2_lower.sort()
    flag = 1
    for i in l2_lower:
        if i in l1_lower:
            pass
        else:
            flag = 0
            break
    return flag

def s2_in_s1(s1, s2):
    s1_lower = s1.lower()
    s2_lower = s2.lower()
    if ',' in s1_lower:
        s1_list = s1_lower.split(',')
        if s2_lower in s1_list:
            return 1
        else:
            return 0
    elif s1_lower == s2_lower:
        return 1
    else:
        return 0
        
    
def compare_attributs(file_attr_list , soft_attr_list):
    #如果软件识别的属性列表包含于文件的属性列表则返回1
    #file_attr_list:[{'Processor':'GATK'}]
    #soft_attr_list:[{'FileFormat': 'FASTQ'},{'Strategy': 'RNA-Seq'},{'Layout': 'Pair-end'},{'Processor':'hisat,tophat'}]
    file_attr_list_keys = []
    for i in file_attr_list:
        file_attr_list_keys.extend(i.keys())
    soft_attr_list_keys = []
    for i in soft_attr_list:
        soft_attr_list_keys.extend(i.keys())    
    #print file_attr_list_keys
    #print soft_attr_list_keys
    flag = 1
    if l2_in_l1(file_attr_list_keys, soft_attr_list_keys):
        for s_attr in soft_attr_list:
            for k,v in s_attr.items():
                pos = file_attr_list_keys.index(k)
                fv = file_attr_list[pos][k]
            if s2_in_s1(fv, v):
                pass
            else:
                flag = 0
                break
    else:
        flag = 0
    return flag
                

if __name__ == '__main__':
    description = 'Find file and tools connection based on the file attributs and t_cwl_soft!\n'
    quick_usage = 'python '+sys.argv[0]+' -indir_uuid cbb9f45d-2925-4909-bfcf-ec141b89e60d\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-indir_uuid', dest='indir_uuid', help='indir uuid in t_file, can be checked by url', default='cbb9f45d-2925-4909-bfcf-ec141b89e60d' );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    indir_uuid = argsDict['indir_uuid']
    
    conn = MySQLdb.connect(host='10.3.128.50', user='dev_cloud', passwd='dev_cloud.123', db='dev_biocloud_files')
    cursor = conn.cursor()  
    #SELECT * FROM t_file f WHERE f.file_uuid='cbb9f45d-2925-4909-bfcf-ec141b89e60d';
    #先获取owner_user_uuid
    cursor.execute('select * FROM t_file f WHERE f.file_uuid="'+indir_uuid+'"')
    search_result =  cursor.fetchone()
    #cursor.scroll(0,mode='absolute') #将光标重置
    owner_user_uuid = search_result[6]
    #SELECT file_uuid,name FROM t_file f WHERE f.pid='cbb9f45d-2925-4909-bfcf-ec141b89e60d' AND f.owner_user_uuid='8a828b82518483d30151848a950d05e4';
    cursor.execute('SELECT file_uuid FROM t_file f WHERE f.pid="'+indir_uuid+'" AND f.owner_user_uuid="'+owner_user_uuid+'"')
    files_uuid = cursor.fetchall()
    cursor.execute('SELECT file_uuid,name,type FROM t_file f WHERE file_uuid in ("'+'","'.join([i[0] for i in files_uuid])+'")')
    files_type = cursor.fetchall()
    #print files_type
    
    cursor.execute('SELECT * FROM t_metadata WHERE file_uuid in ("'+'","'.join([i[0] for i in files_uuid])+'")')
    files_expand_attributs = cursor.fetchall() #((10031487L, '058d30ac-2726-4e5c-8997-9c1014448789', 'Processor', 'GATK'))
    files_expand_attributs_dic = {}
    for f in files_expand_attributs:
        tmp_dic = {}
        tmp_dic[f[2]] = f[3]
        files_expand_attributs_dic.setdefault(f[1], []).append(tmp_dic)
    ##{'058d30ac-2726-4e5c-8997-9c1014448789': [{'Processor':'GATK'}]}

    files_expand_attributs_dic = combine_file_attributs(files_type, files_expand_attributs_dic)
    print "=====files_expand_attributs_dic====="
    for k,v in files_expand_attributs_dic.items():
        print k,v
        
    cursor.execute('select soft_name,soft_version,soft_uuid,inputs_attribute FROM t_cwl_soft')
    softwares = cursor.fetchall()
    #('cufflinks','bams:FileFormat=BAM;Processor=hisat,tophat;;gtf:FileFormat=GFF\r')
    softwares_attributs_dic = {}
    for software in softwares:
        for infile in software[3].strip().split(';;'):
            file_prefix = infile.split(':')[0]
            file_attributs = infile.split(':')[1]
            tmp_dic = {}
            for a in file_attributs.split(';'):
                d = {}
                d[a.split('=')[0]] = a.split('=')[1]
                tmp_dic.setdefault(file_prefix, []).append(d)
            softwares_attributs_dic.setdefault(software[0], []).append(tmp_dic)
    print "=====softwares_attributs_dic====="
    for k,v in softwares_attributs_dic.items():
        print '%-10s' % k,v   
    #{'tophat': [{'fqs': [{'FileFormat': 'FASTQ'},{'Strategy': 'RNA-Seq'},{'Layout': 'Pair-end'}]},{'ref': [{'FileFormat': 'FASTA'}, {'TaxonomyID': '?'}, {'Assembly': '?'}]}]}
    
    file_cor_soft_dic = {}
    for file_uuid in files_expand_attributs_dic:
        file_attr_list = files_expand_attributs_dic[file_uuid]
        #print "=====file_attr_list====="
        #print file_attr_list
        for soft_name, soft_attr_list in softwares_attributs_dic.items():
            for i in soft_attr_list:
                for input_prefix,input_attr_list in i.items():
                    #print "=====input_attr_list====="
                    #print input_attr_list
                    if compare_attributs(file_attr_list, input_attr_list):
                        #print "Findddddd"
                        file_cor_soft_dic.setdefault(file_uuid, []).append(soft_name)
                        break                
    #print file_cor_soft_dic
    print "=====final resutls====="
    for k,v in file_cor_soft_dic.items():
        for f in files_type:
            if k == f[0]:
                print '%-50s==>\t%-30s' % (f[1],','.join(v))
                
    #select max(id) from t_metadata;
    #insert into t_metadata value (11075064,'894ca628-5245-49e9-8a53-7ec0a85563d2', 'Layout', 'Pair-end') ;