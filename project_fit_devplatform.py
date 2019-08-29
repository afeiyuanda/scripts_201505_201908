#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse,MySQLdb,time,uuid,subprocess,glob
reload(sys);
exec("sys.setdefaultencoding('utf-8')");


def get_files_in_dir(dir_path, file_list):
    for f in os.listdir(dir_path):
        full_path = os.path.join(dir_path, f)
        print full_path
        if not os.path.isdir(full_path):
            file_list.append(full_path)
        else:
            get_files_in_dir(full_path, file_list)
    return file_list

    
def get_file_create_time(physical_path):
    filemt= time.localtime(os.stat(physical_path).st_mtime)
    return time.strftime("%Y-%m-%d %H:%M:%S",filemt)

def test_or_run(flag, cmd, user_name, project_type, sql_type='insert', logfile = '/share/nas1/liuw/sql.log'):
    if sql_type == 'insert':
        temp_file = '/share/nas1/liuw/sql_files/sql_insert_'+user_name+'_'+project_type+'.txt'
    else:
        temp_file = '/share/nas1/liuw/sql_files/sql_update_'+user_name+'_'+project_type+'.txt'
    if os.path.exists(temp_file) is False:
        os.system('touch '+temp_file)
        os.system('chmod 775 '+temp_file)
    if flag == 'test' and cmd != '':
        f = open(temp_file, 'a')
        f.writelines(cmd+'\n')
        f.close()
    '''
    elif flag !='test' and cmd != '':
        rflag = os.system(cmd)
        f = open(logfile, 'w')
        f.writelines(cmd)
        if rflag == 0:
            f.writelines('%s: sucess!' % cmd)
        else:
            f.writelines('%s: failed!' % cmd)
        f.close()    
    else:
        pass
    '''
def generate_sql_and_exec(created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, location, user_name, project_type, flag):
    if type == 'folder':
        sql1 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, type, data_uuid, pid, recycle) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %d);' % (created_date, file_uuid, modified_date, name, owner_user_uuid, type, data_uuid, pid, 0)
        sql2 = ''
    else:
        sql1 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, recycle) values ("%s", "%s", "%s", "%s", "%s", %d, "%s", "%s", "%s", %d);' % (created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, 0)
        sql2 = 'insert into t_file_data (created_date, data_uuid, location, size, status, storage_type, owner_user_uuid) values ("%s", "%s", "%s", %d, "FINISH", "FS","%s");' % (created_date, data_uuid, location, size, owner_user_uuid)
    test_or_run(flag, sql1, user_name, project_type)
    test_or_run(flag, sql2, user_name, project_type)

def generate_update_sql(id, file_uuid, user_name, project_type, flag):
    sql = 'update t_personal_data set download_file="%s" where id=%s;' % (file_uuid, id)
    test_or_run(flag, sql, user_name, project_type, 'update')
 
#推送单个文件 
def push_file(physical_dir_path, pid, owner_user_uuid, user_name, project_type, flag='test'):
    if os.path.exists(physical_dir_path):
        created_date = get_file_create_time(physical_dir_path)
        file_uuid = uuid.uuid1()
        feedback = subprocess.Popen('/share/nas1/limh/judgeFileType/judgeFileType %s' % physical_dir_path, stdout=subprocess.PIPE, shell=True)
        type = feedback.stdout.read().strip()
        parent_uuid = pid
        size = os.path.getsize(physical_dir_path)
        name = physical_dir_path.rstrip('/').split('/')[-1]
        data_uuid = uuid.uuid1()
        generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, pid, physical_dir_path, user_name, project_type, flag)
        return file_uuid
    else:
        pass
        
#只推送一层目录        
def push_only_one_dir(physical_dir_path, pid, owner_user_uuid, user_name, project_type, flag='test'):
    if os.path.exists(physical_dir_path):
        created_date = get_file_create_time(physical_dir_path)
        file_uuid = uuid.uuid1()
        type = 'folder'
        parent_uuid = pid
        name = physical_dir_path.rstrip('/').split('/')[-1]
        data_uuid = uuid.uuid1()
        size = 'NULL' #文件夹不会插入size字段
        generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, physical_dir_path, user_name, project_type, flag)
        return file_uuid
    else:
        #print '%s is not exists!' % physical_dir_path
        return ''

#迭代推送目录下所有文件和文件夹        
def push_dir(physical_dir_path, physical_dir_pid, owner_user_uuid, user_name, project_type, flag='test'):
    if os.path.exists(physical_dir_path):
        files = os.listdir(physical_dir_path)
        for f in files:
            abs_path = os.path.join(physical_dir_path, f)
            created_date = get_file_create_time(abs_path)
            file_uuid = uuid.uuid1()
            name = f
            data_uuid = uuid.uuid1()
            parent_uuid = physical_dir_pid
            if os.path.isdir(abs_path):
                type = 'folder'
                size = 'NULL' #文件夹不会插入size字段
                generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, abs_path, user_name, project_type, flag)
                push_dir(abs_path, file_uuid, owner_user_uuid, user_name, project_type, flag)
            else:
                feedback = subprocess.Popen('/share/nas1/limh/judgeFileType/judgeFileType %s' % abs_path, stdout=subprocess.PIPE, shell=True)
                type = feedback.stdout.read().strip()
                size = os.path.getsize(abs_path)
                generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, abs_path, user_name, project_type, flag)
    else:
        print '%s is not exists!' % physical_dir_path

#只推送目录下的所有文件，不推送文件夹
def push_dir_files(physical_dir_path, physical_dir_pid, owner_user_uuid, user_name, project_type, flag='test'):
    if os.path.exists(physical_dir_path):
        files = os.listdir(physical_dir_path)
        for f in files:
            abs_path = os.path.join(physical_dir_path, f)
            created_date = get_file_create_time(abs_path)
            file_uuid = uuid.uuid1()
            name = f
            data_uuid = uuid.uuid1()
            parent_uuid = physical_dir_pid
            if os.path.isdir(abs_path):
                pass
            else:
                feedback = subprocess.Popen('/share/nas1/limh/judgeFileType/judgeFileType %s' % abs_path, stdout=subprocess.PIPE, shell=True)
                type = feedback.stdout.read().strip()
                size = os.path.getsize(abs_path)
                generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, abs_path, user_name, project_type, flag)
    else:
        print '%s is not exists!' % physical_dir_path

def judge_target_zipfile_exists(save_path):
    zipfile_str = 'venn.zip,COG.zip,KOG.zip,eggNOG.zip,GO_class.zip,../GO_class.zip,KEGG_class.zip,../../KEGG_class.zip,KEGG_enrichment.zip,KEGG_pathway.zip,../../KEGG_pathway.zip,GO_enrichment.zip,Trendline.zip,PCA/PCA.zip,Phylotree/Tree.zip,heatmap.zip,SNP.zip,TF.zip,SSR.zip,Vol.zip,MA.zip,../../KEGG_enrichment.zip,miRNA.zip,target.zip,Base_bias.zip,Length_Stat.zip,Result.zip'
    zipfile_list = zipfile_str.split(',')
    zipfile_path = [save_path+'/'+i for i in zipfile_list]
    exists_zipfile_list = [zipfile for zipfile in zipfile_path if os.path.exists(zipfile)]
    return exists_zipfile_list
    
    
def get_personal_result(save_path, id):
    if save_path.endswith('.zip'):
        personal_result = save_path.rstrip('.zip')+'_'+str(id)+'.zip'
        return personal_result
    elif judge_target_zipfile_exists(save_path):
        exists_zipfile_list = judge_target_zipfile_exists(save_path)
        if os.path.exists(save_path+'/personal_result_'+str(id)+'.zip'):
            personal_result = save_path+'/personal_result_'+str(id)+'.zip'
        elif len(exists_zipfile_list) > 1:
            os.system('zip -j '+save_path+'/personal_result_'+str(id)+'.zip '+' '.join(exists_zipfile_list))
            personal_result = save_path+'/personal_result_'+str(id)+'.zip'
        else:
            os.system('cp '+exists_zipfile_list[0]+' '+save_path+'/personal_result_'+str(id)+'.zip ')
            personal_result = save_path+'/personal_result_'+str(id)+'.zip'
        return personal_result
    else:
        if os.path.exists(save_path+'/personal_result_'+str(id)+'.zip'):
            personal_result = save_path+'/personal_result_'+str(id)+'.zip'
        else:
            os.system('cd '+save_path+' && zip -r '+save_path+'/personal_result_'+str(id)+'.zip *')
            personal_result = save_path+'/personal_result_'+str(id)+'.zip'
        return personal_result

def file_not_in_db_then_push(cursor, file_path, pid, user_uuid, user_name, project_type, run_mode):
    file_name = file_path.rstrip('/').split('/')[-1]
    cursor.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="%s" and recycle!=1 and field_1!="delete"' % (user_uuid, pid, file_name))
    search_result = cursor.fetchone()
    if not search_result and os.path.exists(file_path):
        pushed_file_uuid = push_file(file_path, pid, user_uuid, user_name, project_type, run_mode)
    elif search_result and os.path.exists(file_path):
        cursor.scroll(0,mode='absolute')
        pushed_file_uuid = ''
    else:    
        print '[[ERROR]] %s does not exists!' % file_path
        pushed_file_uuid = ''
    return pushed_file_uuid

def write_file(file_handle, line):
    file_handle.write(line+'\n')

def write_dic_into_file(file_handle, d):
    for k,v in d.items():
        write_file(file_handle, k+' ==> '+v)
    
if __name__ == '__main__':
    description = ''
    quick_usage = 'python '+sys.argv[0]+' -user_name 8a828b82518483d30151848a950d05e4\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-user_name', dest='user_name', help='user_name', default='ref_dev' );
    newParser.add_argument( '-app', dest='project_type', help='project_type:ref', default='ref' );
    newParser.add_argument( '-run_mode', dest='run_mode', help='run_mode:test or run', default='test' );
    newParser.add_argument( '-env', dest='env', help='envirenment:dev/rtm/online/yz', default='dev' );
    
    #mysql -hdb-web-master.bmkcloud.lan -ucloud_read -p123.bmk.liuzm  --default-character-set=utf8
    #mysql -hdb-web-master.bmkcloud.lan -ucloud -pcloud.123.bmk -P3306 --default-character-set=utf8
    #mysql -hdb-web-master-0.bmkcloud.lan -ucloud -pcloud.123.bmk -P3306 --default-character-set=utf8
    #mysql -hdb-web-master-1.bmkcloud.lan -ucloud -pcloud.123.bmk -P3306 --default-character-set=utf8
    #mysql -hdb-web-master-1.bmkcloud.lan -ucloud -pcloud.123.bmk -P3307 --default-character-set=utf8
    #mysql -hdb-web-master-0.bmkcloud.lan -ucloud -pcloud.123.bmk -P3307 --default-character-set=utf8
    #mysql -h10.19.1.250 -ucloud_read -p123.cloud_read  --default-character-set=utf8
    #mysql -h10.3.128.50 -udev_cloud -pdev_cloud.123  --default-character-set=utf8
    #mysql -h10.3.129.50 -urtm_cloud -p123.rtm_cloud..bmk   --default-character-set=utf8

    #mysql --host=10.3.128.50 --user=dev_cloud --password=dev_cloud.123 dev_cloud < /share/nas1/liuw/sql_files/sql_update_ref_dev_noref.txt
    #mysql --host=10.3.128.50 --user=dev_cloud --password=dev_cloud.123 dev_biocloud_files < /share/nas1/liuw/sql_files/sql_insert_ref_dev_noref.txt

    #mysql --host=10.3.129.50 --user=rtm_cloud --password=123.rtm_cloud..bmk rtm_biocloud_files < /share/nas1/liuw/sql_files/sql_insert_xuqing1_rtm_ref.txt
    #mysql --host=10.3.129.50 --user=rtm_cloud --password=123.rtm_cloud..bmk rtm_cloud < sql_update_xuqing1_rtm.txt
    
    #python /share/nas1/liuw/scripts/project_fit_devplatform.py -user_name xuqing1_rtm -app ref -host 10.3.129.50 -user rtm_cloud -passwd 123.rtm_cloud..bmk -main_db rtm_cloud -file_db rtm_biocloud_files
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    user_name = argsDict['user_name']
    project_type = argsDict['project_type']
    run_mode = argsDict['run_mode']
    env = argsDict['env']
    
    if env=='dev':
        host = '10.3.128.50'
        user = 'dev_cloud'
        passwd = 'dev_cloud.123'
        main_db = 'dev_cloud'
        file_db = 'dev_biocloud_files'
        modules = 'http://10.3.128.98:8093'
    if env=='rtm':
        host = '10.3.129.50'
        user = 'rtm_cloud'
        passwd = '123.rtm_cloud..bmk'
        main_db = 'rtm_cloud'
        file_db_user = 'rtm_cloud'
        file_db_passwd = '123.rtm_cloud..bmk'
        file_db = 'rtm_biocloud_files'
        modules = 'http://10.3.128.91:8091'
        file_db_port = 3306
    if env=='online':
        host = 'db-web-master.bmkcloud.lan'
        user = 'cloud_read'
        passwd = '123.bmk.liuzm'
        main_db = 'cloud'
        file_db_user = 'cloud'
        file_db_passwd = 'cloud.123.bmk'
        file_db = 'publish_biocloud_files'
        #modules = 'http://10.2.11.1:8091'
        modules = 'http://10.3.128.38:8091'
    if env=='yz':
        host = '10.19.1.250'
        user = 'cloud_read'
        passwd = '123.cloud_read'
        file_db_passwd = '123.cloud_read'
        main_db = 'cloud'
        file_db = 'biocloud_files'
        file_db_user = 'cloud_read'
        modules = 'http://10.3.128.38:8091'
    
    temp_file = '/share/nas1/liuw/sql_files/sql_insert_'+user_name+'_'+project_type+'.txt'
    os.system('rm '+temp_file)
    temp_file1 = '/share/nas1/liuw/sql_files/sql_update_'+user_name+'_'+project_type+'.txt'
    os.system('rm '+temp_file1)
    log_file = '/share/nas1/liuw/sql_files/'+user_name+'_'+project_type+'.log'
    os.system('rm '+log_file)
    log_handle = open(log_file, 'w')
    
    conn_cloud = MySQLdb.connect(host=host, user=user, passwd=passwd, db=main_db, charset="utf8")
    cursor = conn_cloud.cursor()
    cursor.execute("SET NAMES utf8");
    cursor.execute('select id from t_user where username="'+user_name+'";')
    user_uuid = cursor.fetchone()
    user_uuid = user_uuid[0]
    write_file(log_handle, 'user_uuid %s' % user_uuid)
    cursor.scroll(0,mode='absolute') #将光标重置
    
    #host="db-web-master-0.bmkcloud.lan", user="cloud", passwd="cloud.123.bmk", db="publish_biocloud_files", port=3306
    if env=='online':
        feedback = subprocess.Popen( 'python /share/nas2/genome/cloud_soft/api_monitor/fileSystem/getDataBaseByUserId.py '+user_uuid, stdout=subprocess.PIPE, shell=True )
        feedback_lines = feedback.stdout.read()
        #pattern = re.compile(r'.*host="(.*)", user="cloud", passwd="cloud.123.bmk", db="publish_biocloud_files", port=(\d+).*', re.S)
        pattern = re.compile(r'.*host="(.*)", db="publish_biocloud_files", port=(\d+).*', re.S)
        file_db_host = pattern.match(feedback_lines).groups()[0]
        host = file_db_host
        file_db_port = pattern.match(feedback_lines).groups()[1]
        file_db_port = int(file_db_port)
        print 'file_db_host: %s' % file_db_host
        print 'file_db_port: %s' % file_db_port
    
    #SELECT project_code, project_name, project_type, user_id, root_path FROM t_project where project_type='ref' and user_id='8a8300b258751c1701587537556b0834';
    #先获取指定用户所有的有参项目的root_path
    if project_type == 'ref':
        cursor.execute('SELECT id, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s","%s","%s") and user_id="%s";' % (project_type, '有ref转录组','refMedicine','医学有ref转录组', user_uuid))
    if project_type == 'srna':
        cursor.execute('SELECT id, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s","%s","%s") and user_id="%s";' % (project_type, '小RNA','srnaMedicine','医学小RNA', user_uuid))
    if project_type == 'noref':
        cursor.execute('SELECT id, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '无ref转录组', user_uuid))
    if project_type == 'lncrna':
        cursor.execute('SELECT id, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '长链非编码RNA', user_uuid))
    if project_type == 'reseq':
        cursor.execute('SELECT id, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '全基因组重测序分析平台', user_uuid))
    '''
    返回的是一个二维集合
    (('0a828b82596f649g015982a02ce326n4',
      'ref_20171012111812',
      'ref_20171012111812',
      'ref',
      '8a8300b258751c1701587537556b0834',
      '/share/bioCloud/dev/user_data/ua3Jbv4/Personal_data/biomarker_project/outputs20171012123244/Web_Report'))
    '''  
    search_result = cursor.fetchall()
    try:
        cursor.scroll(0,mode='absolute')
    except:
        pass
    project_list = {}
    project_incomplete_list = {}
    project_id_list = {}
    for project in search_result:
        if (project[-1] is None) or (os.path.exists(project[-1]) is False):
            #print project[0]+' root_path is not exists!'
            try:
                project_incomplete_list[project[-1].rstrip('/').split('/')[-2]] = project[-1]
            except:
                pass
        else:
            project_list[project[-1].rstrip('/').split('/')[-2]] = project[-1]
            project_id_list[project[-1]] = project[0]
    #print '---------------Project dirname and rootpath---------------'
    write_file(log_handle, '---------------project_list(root path is exists)---------------')
    write_dic_into_file(log_handle, project_list)
    write_file(log_handle, '---------------project_list(root path is not exists)---------------')
    write_dic_into_file(log_handle, project_incomplete_list)

    print 'host %s, user %s, passwd %s, file_db %s, port %s' % (host, file_db_user, file_db_passwd, file_db, file_db_port)
    conn_biocloud_files = MySQLdb.connect(host=host, user=file_db_user, passwd=file_db_passwd, db=file_db, port=file_db_port, charset="utf8")
    cursor1 = conn_biocloud_files.cursor()
    #select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="8a828b825182474d0151848237bc0107" and type="folder" limit 5;
    #select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="8a828b825182474d0151848237bc0107" and name="biomarker_project" and pid is NULL limit 1;
    #cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'" and name="biomarker_project" and pid is NULL limit 5;')
    cursor1.execute('select id, file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'" and name="biomarker_project" and recycle!=1 and field_1!="delete";')
    #biomarker_project这个目录会有多个么？
    biomarker_project_dir =  cursor1.fetchall()
    biomarker_project_uuid_list = [i[1] for i in biomarker_project_dir]
    biomarker_project_uuid_str = '('+','.join(['"'+i+'"' for i in biomarker_project_uuid_list])+')' 
    write_file(log_handle, 'biomarker_project_uuid_str: %s' % biomarker_project_uuid_str)
    biomarker_project_id_list = [i[0] for i in biomarker_project_dir]
    biomarker_project_id_str = '('+','.join(['"'+str(i)+'"' for i in biomarker_project_id_list])+')' 
    #print biomarker_project_id_str
    
    cursor1.scroll(0,mode='absolute') #将光标重置
    project_str = '('+','.join(['"'+i+'"' for i in project_list.keys()])+')'
    #print project_str
    #cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where pid ="'+biomarker_project_uuid+'"')
    #print 'select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'" and name in '+project_str+' and (pid in '+biomarker_project_uuid_str+' or parents_folder_id in '+biomarker_project_id_str+');'
    print 'select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'" and name in '+project_str+' and (pid in '+biomarker_project_uuid_str+' or parents_folder_id in '+biomarker_project_id_str+');'
    cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'" and recycle!=1 and field_1!="delete" and name in '+project_str+' and (pid in '+biomarker_project_uuid_str+' or parents_folder_id in '+biomarker_project_id_str+');')
    #print 'select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'" and recycle!=1 and field_1!="delete" and name in '+project_str+' and pid="7ddf3c04-dc14-11e8-b070-0242ac110004";'
    #cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'" and recycle!=1 and field_1!="delete" and name in '+project_str+' and pid="7ddf3c04-dc14-11e8-b070-0242ac110004";')
    
    project_full_info = cursor1.fetchall()
    #print '---------------project_full_info---------------'
    #print project_full_info
    project_uuid_list = [i[0] for i in project_full_info]
    project_name_list = [i[1] for i in project_full_info]
    project_dict = dict(zip(project_uuid_list, project_name_list))
    project_uuid_str = '('+','.join(['"'+i+'"' for i in project_uuid_list])+')'
    write_file(log_handle, '---------------project_dict(only including project that root path is exists)---------------')
    write_dic_into_file(log_handle, project_dict)
    
    cursor1.scroll(0,mode='absolute')
    cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="'+user_uuid+'"  and recycle!=1 and field_1!="delete" and pid in '+project_uuid_str)
    project_son_dir = cursor1.fetchall()
    #print project_son_dir
    cursor1.scroll(0,mode='absolute') #将光标重置
    project_has_needed_data = [i[-1] for i in project_son_dir if 'Needed_Data' in i]
    project_has_needed_data_id = [i[0] for i in project_son_dir if 'Needed_Data' in i]
    project_has_needed_data_dic = dict(zip(project_has_needed_data, project_has_needed_data_id))
    #needed_data有重复目录
    project_has_needed_data = project_has_needed_data_dic.keys()
    
    web_report = [i[-1] for i in project_son_dir if 'Web_Report' in i]
    web_report_id = [i[0] for i in project_son_dir if 'Web_Report' in i]
    web_report_dic = dict(zip(web_report, web_report_id))
    web_report = web_report_dic.keys()

    metadata = [i[-1] for i in project_son_dir if 'metadata.properties' in i]
    metadata_id = [i[0] for i in project_son_dir if 'metadata.properties' in i]
    metadata_dic = dict(zip(metadata, metadata_id))
    metadata = metadata_dic.keys()
    
    personal_analysis_pid = [i[-1] for i in project_son_dir if 'Personal_Analysis' in i]
    personal_analysis_id = [i[0] for i in project_son_dir if 'Personal_Analysis' in i]
    personal_analysis_dic = dict(zip(personal_analysis_pid, personal_analysis_id))
    personal_analysis_pid = personal_analysis_dic.keys()
    
    DEG_Analysis_dic = {}
    for k,v in personal_analysis_dic.items():
        cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="DEG_Analysis" and recycle!=1 and field_1!="delete"' % (user_uuid, v))
        r = cursor1.fetchone()
        if r:
            cursor1.scroll(0,mode='absolute')
            DEG_Analysis_uuid = r[0]
            DEG_Analysis_dic[k] = {v:DEG_Analysis_uuid}
        else:
            DEG_Analysis_dic[k] = {}
    
    print '---------------project_has_needed_data_dic---------------'
    print project_has_needed_data_dic
    project_no_needed_data = set(project_uuid_list).difference(set(project_has_needed_data))
    print '---------------project_no_needed_data---------------'
    print project_no_needed_data
    print '---------------web_report_dic---------------'
    print web_report_dic
    print '---------------DEG_Analysis_dic---------------'
    print DEG_Analysis_dic
    write_file(log_handle, '---------------Project rootpath and id ---------------')
    #print project_id_list
    write_dic_into_file(log_handle, project_id_list)
    
    for p in web_report_dic.keys():
        for k in project_list.keys():
            if project_dict[p] == k:
                root_path = project_list[k]
                root_path_parent = os.path.dirname(root_path.rstrip('/'))
                #root_path 带有Web_Report这一层
                #print 'root_path %s.' % root_path
                #生成并推送.report_new.html，由于有些项目没有推送时生成的xml，导致生成新的report失败
                push_xml_list = glob.glob(root_path_parent+'/*.xml')
                new_report_html = os.path.exists(root_path+'/.report_new.html')
                if push_xml_list:
                    push_xml = push_xml_list[0]
                    cmd = """ grep  'fileUuid' """ + push_xml
                    #print cmd
                    feedback = subprocess.Popen( cmd, stdout=subprocess.PIPE, shell=True )
                    file_uuid_flag = feedback.stdout.read()
                    if file_uuid_flag == '':
                        os.system('rm -rf /share/nas1/liuw/sql_files/push_%s.xml' % env)
                        #parentUuid 是整个项目目录的上一级，正常就是biomarker_project这一级目录
                        generate_push_xml_cmd = 'curl -X POST --header "Content-Type: application/json" --header "Accept: application/json;charset=UTF-8" -d "{\\"createXmlPath\\": \\"/share/nas1/liuw/sql_files/push_%s.xml\\",\\"jobName\\": \\"%s\\",\\"parentUuid\\": \\"%s\\",\\"userId\\": \\"%s\\"}" "%s/api/v2/files/push/createXml"' % (env,root_path.rstrip('/').split('/')[-2],biomarker_project_uuid_list[0],user_uuid,modules)
                        write_file(log_handle, generate_push_xml_cmd)
                        os.system(generate_push_xml_cmd)
                        os.system('cp /share/nas1/liuw/sql_files/push_%s.xml %s' % (env,root_path_parent))
                        push_xml = root_path_parent+'/push_%s.xml' % env
                else:
                    os.system('rm -rf /share/nas1/liuw/sql_files/push_%s.xml' % env)
                    generate_push_xml_cmd = 'curl -X POST --header "Content-Type: application/json" --header "Accept: application/json;charset=UTF-8" -d "{\\"createXmlPath\\": \\"/share/nas1/liuw/sql_files/push_%s.xml\\",\\"jobName\\": \\"%s\\",\\"parentUuid\\": \\"%s\\",\\"userId\\": \\"%s\\"}" "%s/api/v2/files/push/createXml"' % (env,root_path.rstrip('/').split('/')[-2],biomarker_project_uuid_list[0],user_uuid,modules)
                    write_file(log_handle, generate_push_xml_cmd)
                    os.system(generate_push_xml_cmd)
                    os.system('cp /share/nas1/liuw/sql_files/push_%s.xml %s' % (env,root_path+'/../'))
                    push_xml = root_path+'/../push_%s.xml' % env
                write_file(log_handle,'push xml is %s.' % push_xml)
                os.system('cp '+root_path+'/.report.html '+root_path+'/.report.html.bak')

                if project_type == 'noref' and os.path.exists(root_path+'/configtest_raw.xml') and os.path.getsize(root_path+'/configtest_raw.xml')!=0:
                    os.system('/share/nas2/software/node/bin/node  --max_old_space_size=20480 /share/nas2/genome/cloud_soft/word_explanation/generateReport_DevPlatform/index.js '+root_path+'/configtest_raw.xml '+push_xml+' > /dev/null')
                elif os.path.exists(root_path+'/configtest.xml') and os.path.getsize(root_path+'/configtest.xml')!=0:
                    os.system('/share/nas2/software/node/bin/node  --max_old_space_size=20480 /share/nas2/genome/cloud_soft/word_explanation/generateReport_DevPlatform/index.js '+root_path+'/configtest.xml '+push_xml+' > /dev/null')
                else:
                    write_file(log_handle, '[[ERROR]] %s not exists or is empty!!' % (root_path+'/configtest(_raw).xml'))
                    
                os.system('mv -f '+root_path+'/.report.html '+root_path+'/.report_new.html')
                os.system('mv -f '+root_path+'/.report.html.bak '+root_path+'/.report.html')
                file_not_in_db_then_push(cursor1, root_path+'/.report_new.html', web_report_dic[p], user_uuid, user_name, project_type, run_mode)
                file_not_in_db_then_push(cursor1, root_path+'/index.html', web_report_dic[p], user_uuid, user_name, project_type, run_mode)

                if project_type == 'noref':
                    os.system('mkdir -p %s' % root_path_parent+'/Needed_Data/Config/')
                    if not os.path.exists(root_path_parent+'/Needed_Data/Config/detail.cfg'):
                        os.system('cp %s/data.cfg %s/../Needed_Data/Config/' % (root_path, root_path))
                        os.system('cp %s/detail.cfg %s/../Needed_Data/Config/' % (root_path, root_path))
                    if os.path.exists(root_path+'/DEG_Analysis/DEG_PPI/ppi_qurey.ppi.cytoscapeInput.sif'):
                        os.system('cp %s/DEG_Analysis/DEG_PPI/ppi_qurey.ppi.cytoscapeInput.sif %s/../Needed_Data/PPI.txt' % (root_path, root_path))
                    elif os.path.exists(root_path+'/BMK_6_DEG_Analysis/BMK_1_All_DEG/ppi_qurey.ppi.cytoscapeInput.sif'):
                        os.system('cp %s/BMK_6_DEG_Analysis/BMK_1_All_DEG/ppi_qurey.ppi.cytoscapeInput.sif %s/../Needed_Data/PPI.txt' % (root_path, root_path))
                    else:
                        write_file(log_handle, '[[WARNING]] %s does not have PPI.txt!!' % root_path)
                if project_type == 'srna':
                    os.system('cp %s/../Needed_Data/Config/free_pipeline.cfg %s/../Needed_Data/Config/detail.cfg' % (root_path, root_path))
                    os.system('cp %s/ppi_qurey.ppi.cytoscapeInput.sif %s/../Needed_Data/PPI.txt' % (root_path, root_path))
                
                #判断Needed_Data是否存在，并推送，然后获取到needed_data_uuid
                if project_has_needed_data_dic.has_key(p):
                    needed_data_uuid = project_has_needed_data_dic[p]
                    #print 'needed_data_uuid %s' % needed_data_uuid
                else:
                    needed_data_uuid = push_only_one_dir(root_path_parent+'/Needed_Data', p, user_uuid, user_name, project_type, run_mode)
                    if needed_data_uuid != '':
                        push_dir(root_path_parent+'/Needed_Data', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    else:
                        write_file(log_handle, '[[ERROR]] %s not exists!!' % (root_path_parent+'/Needed_Data'))

                file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/biomarker_htmlReport.zip', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/biomarker_Web_Report.zip', needed_data_uuid, user_uuid, user_name, project_type, run_mode)

                #针对有参进行处理
                if project_type == 'ref':
                    #生成metadata.properties,all.gff,chroDetail.txt
                    #new_init_script = '/share/nas1/xugl/Script/ref.pl'
                    new_init_script = '/share/nas1/niulg/pipeline/tools/trans_metadata.pl'
                    deg_config_file = 'ref_trans_deg.config'
                    deg_init_script = '/share/nas2/genome/cloud_soft/app_pipeline/ref_trans_pipeline/plug-in/DEG_Init/DEG_Initialize.pl'
                    os.system('/share/nas2/genome/bin/perl %s -prt %s  -app %s > /dev/null' % (new_init_script, root_path, project_type))
                    #perl /share/nas1/niulg/pipeline/tools/trans_metadata.pl -prt Web_Report/ -app ref
                    
                    nul_seq_pos1 = glob.glob(root_path_parent+'/Needed_Data/*.longest_transcript.fa')
                    nul_seq_pos2 = glob.glob(root_path_parent+'/Needed_Data/Allgene_annoNseq/*.longest_transcript.fa')
                    #推送这个文件放到了下边
                    if nul_seq_pos1 and not nul_seq_pos2:
                        os.system('cp '+nul_seq_pos1[0]+' '+root_path_parent+'/Needed_Data/Allgene_annoNseq/')
                    elif not nul_seq_pos1 and not nul_seq_pos2:
                        write_file(log_handle, '[[ERROR]] %s does not have nucleic_seq!!' % root_path)
                    else:
                        pass
                    
                    #补充缺少文件的程序/share/nas1/xugl/Script/others/handle_ref_file.py
                    #判断gene_pos.list是否存在，并推送
                    if not os.path.exists(root_path+'/gene_pos.list'):
                        os.system('perl /share/nas1/niulg/ref_pipeline/ref_cwl_pipeline/trunk/ref_report/ref_report/bin/extract_gene_position_gff.pl -i %s -o %s' % (root_path_parent+'/Needed_Data/all.gff', root_path))
                    file_not_in_db_then_push(cursor1, root_path+'/gene_pos.list', web_report_dic[p], user_uuid, user_name, project_type, run_mode)
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/PPI.txt', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    
                    if project_has_needed_data_dic.has_key(p) and needed_data_uuid != '':
                        cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="Allgene_annoNseq" and recycle!=1 and field_1!="delete"' % (user_uuid, needed_data_uuid))
                        try:
                            Allgene_annoNseq_uuid = cursor1.fetchone()[0]
                            #print 'Allgene_annoNseq_uuid %s' % Allgene_annoNseq_uuid
                            cursor1.scroll(0,mode='absolute')
                            cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and recycle!=1 and field_1!="delete"' % (user_uuid, Allgene_annoNseq_uuid))
                            files = cursor1.fetchall()
                            cursor1.scroll(0,mode='absolute')
                            nul_file = [i[1] for i in files if 'longest_transcript.fa' in i[1]]
                            nul_file_phy_path = glob.glob(root_path_parent+'/Needed_Data/Allgene_annoNseq/*longest_transcript.fa')
                            if nul_file_phy_path and not nul_file:
                                file_uuid = push_file(nul_file_phy_path[0], Allgene_annoNseq_uuid, user_uuid, user_name, project_type, run_mode)
                        except:
                            write_file(log_handle, '[[ERROR]] %s does not have Allgene_annoNseq!' % root_path)
                        file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/all.gff', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                        file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/chroDetail.txt', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                
                #针对srna进行处理
                if project_type == 'srna':
                    #生成metadata.properties
                    new_init_script = '/share/nas1/xugl/liyl/pipeline/metadata_properties_sRNA.pl'
                    deg_config_file = 'sRNA_deg.config'
                    deg_init_script = '/share/nas2/genome/cloud_soft/developer_platform/small_RNA_pipeline/v2.0/tools/DEG_Init/DEG_Initialize.pl'
                    os.system('/share/nas2/genome/bin/perl %s -prt %s > /dev/null' % (new_init_script, root_path))
                    #print 'root path is %s' % root_path
                    #print 'select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="Config"' % (user_uuid, needed_data_uuid)
                    try:
                        cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="Config" and recycle!=1 and field_1!="delete"' % (user_uuid, needed_data_uuid))
                        config_uuid = cursor1.fetchone()[0]
                        cursor1.scroll(0,mode='absolute')
                        file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/Config/detail.cfg', config_uuid, user_uuid, user_name, project_type, run_mode)
                    except:
                        write_file(log_handle, '[[ERROR]] %s has needed data, but do not have Config dir!' % root_path)

                #针对noref进行处理
                if project_type == 'noref':
                    #生成metadata.properties
                    new_init_script = '/share/nas1/songmm/programes/metadata_properties_noref.pl'
                    deg_config_file = 'no_ref_trans_deg.config'
                    deg_init_script = '/share/nas2/genome/cloud_soft/app_pipeline/de_novo_trans_pipeline/plug-in/DEG_Init/DEG_Initialize.pl'
                    modify_pep_name_script = '/share/nas1/songmm/programes/cds_id.pl'
                    os.system('/share/nas2/genome/bin/perl %s -prt %s > /dev/null' % (new_init_script, root_path))
                    os.system('/share/nas2/genome/bin/perl %s -i %s/../Needed_Data/Unigene.pep.fa > /dev/null' % (modify_pep_name_script, root_path))
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/Unigene.fa', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/Unigene.pep.fa', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/final.snp.list', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/PPI.txt', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    try:
                        cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="Config" and recycle!=1 and field_1!="delete"' % (user_uuid, needed_data_uuid))
                        config_uuid = cursor1.fetchone()
                        #推送无参项目在Needed_Data目录下新创建的Config目录
                        if config_uuid[0]:
                            file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/Config/detail.cfg', config_uuid[0], user_uuid, user_name, project_type, run_mode)
                            file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/Config/data.cfg', config_uuid[0], user_uuid, user_name, project_type, run_mode)
                            cursor1.scroll(0,mode='absolute')
                        else:
                            config_uuid = push_only_one_dir(root_path_parent+'/Needed_Data/Config', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                            push_dir_files(root_path_parent+'/Needed_Data/Config', config_uuid, user_uuid, user_name, project_type, run_mode)
                    except Exception as e:
                        print '%s config dir not exists in db!' % root_path
                        config_uuid = push_only_one_dir(root_path_parent+'/Needed_Data/Config', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                        #print config_uuid
                        push_dir_files(root_path_parent+'/Needed_Data/Config', config_uuid, user_uuid, user_name, project_type, run_mode)
                        
                    cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="Unigene" and recycle!=1 and field_1!="delete"' % (user_uuid, web_report_dic[p]))
                    Unigene_uuid = cursor1.fetchone()
                    if not Unigene_uuid:
                        Unigene_uuid = push_only_one_dir(root_path+'/Unigene', web_report_dic[p], user_uuid, user_name, project_type, run_mode)
                        push_dir(root_path+'/Unigene', Unigene_uuid, user_uuid, user_name, project_type, run_mode)
                    else:
                        cursor1.scroll(0,mode='absolute')
                    
                #针对lncrna进行处理
                if project_type == 'lncrna':
                    #生成metadata.properties
                    new_init_script = '/share/nas1/niulg/pipeline/tools/trans_metadata.pl'
                    #deg_config_file = 'lncRNA_trans_deg.config'
                    deg_config_file = 'lnc_trans_mRNA_all_table.xls'
                    deg_init_script = '/share/nas2/genome/cloud_soft/app_pipeline/lncRNA_pipeline/plug-in/DEG_Init/lncRNA_DEG_Initialize.pl'
                    os.system('/share/nas2/genome/bin/perl %s -prt %s -app %s > /dev/null' % (new_init_script, root_path, project_type))
                    os.system('perl /share/nas1/niulg/pipeline/tools/make_file_for_cloud.pl -prodir '+root_path+'/../')
                    os.system('sh '+root_path+'/../make_fulltab_for_personnality.sh')
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/PPI.txt', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/gene_pos.list', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/LncRNA.fa', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    file_not_in_db_then_push(cursor1, root_path_parent+'/Needed_Data/lncRNA_pos.list', needed_data_uuid, user_uuid, user_name, project_type, run_mode)
                    

                #判断Personal_Analysis和DEG_Analysis两个目录是否存在，并推送，没有的话需要先创建
                if personal_analysis_dic.has_key(p) and DEG_Analysis_dic[p]:
                    personal_analysis_uuid = personal_analysis_dic[p]
                    deg_analysis_uuid = DEG_Analysis_dic[p][personal_analysis_dic[p]]
                elif personal_analysis_dic.has_key(p) and not DEG_Analysis_dic[p]:
                    personal_analysis_uuid = personal_analysis_dic[p]
                    os.system('mkdir -p '+root_path_parent+'/Personal_Analysis/DEG_Analysis')
                    deg_analysis_uuid = push_only_one_dir(root_path_parent+'/Personal_Analysis/DEG_Analysis', personal_analysis_uuid, user_uuid, user_name, project_type, run_mode)
                else:
                    os.system('mkdir -p '+root_path_parent+'/Personal_Analysis/DEG_Analysis')
                    personal_analysis_uuid = push_only_one_dir(root_path_parent+'/Personal_Analysis', p, user_uuid, user_name, project_type, run_mode)
                    deg_analysis_uuid = push_only_one_dir(root_path_parent+'/Personal_Analysis/DEG_Analysis', personal_analysis_uuid, user_uuid, user_name, project_type, run_mode)

                #判断初始化的四个文件是否推送了，并进行推送
                cursor1.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="%s" and recycle!=1 and field_1!="delete"' % (user_uuid, deg_analysis_uuid, deg_config_file))
                ref_trans_deg = cursor1.fetchone()
                if not ref_trans_deg and os.path.exists(root_path_parent+'/Personal_Analysis/DEG_Analysis/'+deg_config_file):
                    push_dir_files(root_path_parent+'/Personal_Analysis/DEG_Analysis', deg_analysis_uuid, user_uuid, user_name, project_type, run_mode)
                elif not ref_trans_deg and not os.path.exists(root_path_parent+'/Personal_Analysis/DEG_Analysis/'+deg_config_file):
                    exe_flag = os.system('/share/nas2/genome/bin/perl  %s --project %s' % (deg_init_script,root_path))
                    if exe_flag != 0:
                        write_file(log_handle, '[[ERROR]] %s deg initiate failed!!' % root_path)
                    push_dir_files(root_path_parent+'/Personal_Analysis/DEG_Analysis', deg_analysis_uuid, user_uuid, user_name, project_type, run_mode)
                else:
                    cursor1.scroll(0,mode='absolute')
                
                #推送个性化结果文件
                cursor.execute('select id, user_id, project_id, save_path from t_personal_data where user_id="%s" and project_id="%s" and save_path is not NULL' % (user_uuid, project_id_list[root_path]))
                pesonal_record_list = cursor.fetchall()
                if pesonal_record_list:
                    print pesonal_record_list
                    cursor.scroll(0,mode='absolute')
                    for pesonal_record in pesonal_record_list:
                        if len(pesonal_record[-1]) == 36:
                            generate_update_sql(pesonal_record[0], pesonal_record[-1], user_name, project_type, run_mode)
                        elif pesonal_record[-1]=='false' or not os.path.exists(pesonal_record[-1]):
                            pass
                        else:
                            personal_result = get_personal_result(pesonal_record[-1], pesonal_record[0])
                            #print 'personal_result is %s.' % personal_result
                            file_uuid = file_not_in_db_then_push(cursor1, personal_result, personal_analysis_uuid, user_uuid, user_name, project_type, run_mode)
                            if file_uuid:
                                generate_update_sql(pesonal_record[0], file_uuid, user_name, project_type, run_mode)
                else:
                    #print '%s does not have saved personal results!' % root_path
                    pass
                    
                #判断metadata.properties是否存在，并推送
                if os.path.exists(root_path+'/../metadata.properties') and not metadata_dic.has_key(p):
                    push_file(root_path+'/../metadata.properties', p, user_uuid, user_name, project_type, run_mode)

                break
    log_handle.close()