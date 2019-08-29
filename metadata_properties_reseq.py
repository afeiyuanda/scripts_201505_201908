#!/share/nas2/genome/biosoft/Python/2.7.8/bin/python
#-*- coding:utf-8 -*-

import sys 
import os
import argparse as ap
import time
import re
import shutil
from os.path import abspath
import json

SCRIPTDIR,SCRIPTNAME = os.path.split(abspath(sys.argv[0]))

def arg_parse():
    parser = ap.ArgumentParser(
          formatter_class=ap.RawTextHelpFormatter)
    arg = parser.add_argument
    arg("-prt", dest = "web_report", help = "the dir of web_report", required = True)
    args = parser.parse_args()
    return vars(args)

def read_config(config):
    f = open(config)
    lines = f.readlines()
    f.close()
    cfg_dic = {}
    for line in lines:
        if not line.strip() or line.startswith('#'):
            continue
        else:
            line_list = re.split('\t+|\s+', line.strip())
            cfg_dic[line_list[0]] = line_list[1]
    return cfg_dic

    
def change_real_path(real_path):
    temp_list = []
    flag = 0
    data_marker = ''
    for i in real_path.split('/'):
        if flag:
            temp_list.append(i)
        if i == 'Personal_data':
            if 'BMK-Genome_data' in i or 'BMK_sample_data' in i:
                data_marker='/公共数据'
                flag=1
            else:
                data_marker='/个人数据'
                flag=1
    return data_marker+'/'+'/'.join(temp_list)
    
    
def read_data_cfg(data_cfg):
    """
    input:[data_cfg]

    <R01>
        fq1     /share/bioCloud/user_data/uRHxX48/Personal_data/BMK_sample_data/APP/reseq_demo_data/Cucumber_G55-R01-I_good_1.fq
        fq1_size        157228849
        fq1_uuid        8ed725b9-7f3b-4175-894c-ebfaf2737e37
        fq2     /share/bioCloud/user_data/uRHxX48/Personal_data/BMK_sample_data/APP/reseq_demo_data/Cucumber_G55-R01-I_good_2.fq
        fq2_size        157228967
        fq2_uuid        c42f5a84-e064-4620-ab04-fcb51288f257
        raw_fq1 Cucumber_G55-R01-I_good_1.fq
        raw_fq2 Cucumber_G55-R01-I_good_2.fq
    </R01>
    """

    f = open(data_cfg)
    lines = f.readlines()
    f.close()
    new_lines = lines[1:]

    try:
        print '10'
        samples_block = [new_lines[i: i + 10] for i in range(0, len(new_lines), 10)]
        samples_data_ul_dic = {}
        for block in samples_block:
            print 'block[0] = '+block[0]
            pattern = re.compile('<(.+)>')
            sample = pattern.match(block[0]).group(1)
            for line in block[1:9]:
                (k, v) = line.strip().split('\t')
                v = v.replace('//', '/')
                try:
                    samples_data_ul_dic[sample][k] = v
                except:
                    samples_data_ul_dic[sample] = {}
                    samples_data_ul_dic[sample][k] = v
    except:
        print '6'
        samples_block = [new_lines[i: i + 6] for i in range(0, len(new_lines), 6)]
        samples_data_ul_dic = {}
        for block in samples_block:
            pattern = re.compile('<(.+)>')
            sample = pattern.match(block[0]).group(1)
            for line in block[1:5]:
                (k, v) = line.strip().split('\t')
                v = v.replace('//', '/')
                try:
                    samples_data_ul_dic[sample][k] = v
                except:
                    samples_data_ul_dic[sample] = {}
                    samples_data_ul_dic[sample][k] = v
    
    samples_data_path_list = []
    if 'Personal_data' not in samples_data_ul_dic.values()[0]['fq1']:
        return samples_data_path_list
    else:
        samples_data_path_list = []
        for k in samples_data_ul_dic.keys():
            file_dir = os.path.dirname( change_real_path(samples_data_ul_dic[k]['fq1']) )
            if file_dir not in samples_data_path_list:
                samples_data_path_list.append(file_dir)
            
    return samples_data_path_list

def main():
    args = arg_parse()
    web_report_dir = abspath(args['web_report'])

    metadata_properties_file=os.path.join(web_report_dir,'..','metadata.properties')
    if os.path.exists(metadata_properties_file):
        exit(0)
    #metadata_properties_file=os.path.join('./','metadata.properties')
    metadata_properties_list=[]

    ##read config file of this project
    need_data_dir= os.path.join(web_report_dir,'../Needed_Data')
    
    project_cfg=os.path.join(need_data_dir,'detail.cfg')
    project_cfg_dict=read_config(project_cfg)
  
    try:
        ## project name; 
        project_name={    "name":'项目名称',
        "enName": "project_name",
        "value": ['项目名称: %s ' %(project_cfg_dict['title_Project1'])],
        "enValue":['项目名称: %s ' %(project_cfg_dict['title_Project1'])]
        }
    except:
        ## project name; 
        project_name={    "name":'项目名称',
        "enName": "project_name",
        "value": ['项目名称: %s ' %(project_cfg_dict['tital_Project1'])],
        "enValue":['项目名称: %s ' %(project_cfg_dict['tital_Project1'])]
        }
    metadata_properties_list.append(project_name)

    ## pipeline version;
    version ={
    "name": "流程版本",
    "enName": "version",
    "value": ["流程版本: %s "  %(project_cfg_dict['version'])],
    "enValue": ["流程版本: %s "  %(project_cfg_dict['version'])]
    }
    metadata_properties_list.append(version)

    ## project ref ;
    ref={
    "name": "参考基因组信息",
    "enName": "reference",
    "value": ["物种及组装版本: %s " %(project_cfg_dict['taxo']+','+project_cfg_dict['ref_version']) ],
    "enValue": ["物种及组装版本: %s " %(project_cfg_dict['taxo']+','+project_cfg_dict['ref_version']) ]
    }
    metadata_properties_list.append(ref)

    if project_cfg_dict.has_key('step') and project_cfg_dict['step']=='snp_indel_only':
        analyse_module = 'SNP/InDel分析'
    elif project_cfg_dict.has_key('step') and project_cfg_dict['step']=='all':
        analyse_module = 'SNP/InDel/SV/CNV分析'
    else:
        analyse_module = ''
    
    ## 分析内容 ; 
    if analyse_module:
        Marker_type={
        "name": "分析内容",
        "enName": "analyse_module",
        "value": ["分析内容:%s" %analyse_module],
        "enValue": ["分析内容:%s" %analyse_module]

        }
        metadata_properties_list.append(Marker_type)

    ## project samples data path info ;

    samples_data_file=os.path.join(need_data_dir,'data.cfg')
    samples_data_path_list=[]
    samples_data_path_list = read_data_cfg(samples_data_file)

    if samples_data_path_list:
        samples_data_path= {
        "name": "测序数据路径",
        "enName": "samples_data_path",
        "value": samples_data_path_list,
        "enValue": samples_data_path_list
        }
        metadata_properties_list.append(samples_data_path)
    #print(metadata_properties_list) 
    ## write into metadata.properties

    json_string=json.dumps(metadata_properties_list, ensure_ascii=False)
    with open(metadata_properties_file, "w") as fn:
        fn.write('project_details='+json_string)

if __name__ == '__main__':
    main()
