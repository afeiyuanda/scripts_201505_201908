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
    try:
        filemt= time.localtime(os.stat(physical_path).st_mtime)
        return time.strftime("%Y-%m-%d %H:%M:%S",filemt)
    except:
        return ""
    

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
        sql2 = 'insert into t_file_data (created_date, data_uuid, location, size, status, storage_type) values ("%s", "%s", "%s", %d, "FINISH", "S3");' % (created_date, data_uuid, location, size)
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
                try:
                    size = os.path.getsize(abs_path)
                except:
                    size = 0
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
    #save_path = str(save_path)
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
    cursor.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="%s"' % (user_uuid, pid, file_name))
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

def comp_time(begin_time, new_time):
    #begin_time = '2017-12-01 00:00:00'
    bt = time.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
    nt = new_time.timetuple()
    btt = time.mktime(bt)
    ntt = time.mktime(nt)
    if (ntt - btt) >= 0:
        return 1
    else:
        return 0

if __name__ == '__main__':
    description = ''
    quick_usage = 'python '+sys.argv[0]+' -user_name 8a817f674d663d1e014d7aec4a2b52f2\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-user_name', dest='user_name', help='user_name', default='project' );
    newParser.add_argument( '-app', dest='project_type', help='project_type:ref', default='ref' );
    newParser.add_argument( '-env', dest='env', help='envirenment:dev/rtm/online', default='online' );
    
    #mysql -h10.2.12.1 -ucloud_read -p123.bmk.liuzm  --default-character-set=utf8
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
        file_db = 'rtm_biocloud_files'
        modules = 'http://10.3.128.91:8091'
    if env=='online':
        host = '10.2.12.1'
        user = 'cloud_read'
        passwd = '123.bmk.liuzm'
        main_db = 'cloud'
        file_db = 'publish_biocloud_files'
        #modules = 'http://10.2.11.1:8091'
        modules = 'http://10.3.128.38:8091'
        
    conn_cloud = MySQLdb.connect(host=host, user=user, passwd=passwd, db=main_db, charset="utf8")
    cursor = conn_cloud.cursor()
    cursor.execute("SET NAMES utf8");
    cursor.execute('select id from t_user where username="'+user_name+'";')
    user_uuid = cursor.fetchone()
    user_uuid = user_uuid[0]
    cursor.scroll(0,mode='absolute') #将光标重置
    
    #SELECT project_code, project_name, project_type, user_id, root_path FROM t_project where project_type='ref' and user_id='8a8300b258751c1701587537556b0834';
    #uv24Yfc: 8a828b81575223590157559dcb8a79b4;
    #先获取指定用户所有的有参项目的root_path
    if project_type == 'ref':
        cursor.execute('SELECT id, uptime, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '有ref转录组', user_uuid))
    if project_type == 'srna':
        cursor.execute('SELECT id, uptime, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '小RNA', user_uuid))
    if project_type == 'noref':
        cursor.execute('SELECT id, uptime, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '无ref转录组', user_uuid))
    if project_type == 'lncrna':
        cursor.execute('SELECT id, uptime, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '长链非编码RNA', user_uuid))
    if project_type == 'mbd':
        cursor.execute('SELECT id, uptime, project_code, project_name, project_type, user_id, root_path FROM t_project where project_type in ("%s","%s") and user_id="%s";' % (project_type, '微生物多样性', user_uuid))

    search_result = cursor.fetchall()
    try:
        cursor.scroll(0,mode='absolute')
    except:
        pass
    begin_time = '2017-12-01 00:00:00'
    for project in search_result:
        #uptime type: datetime.datetime(2017, 8, 3, 16, 27, 3)
        if (project[-1] is not None) and os.path.exists(project[-1]) and comp_time(begin_time, project[1]):
            root_path = project[-1]
            print root_path
            stat = os.system('/share/nas2/genome/cloud_soft/developer_platform/plug-in/search/report_init/dist/index %s %s /share/nas2/genome/cloud_soft/developer_platform/plug-in/search/report_init/report-init.conf > %s/init.log' % (project_type, project[-1]+'/../',project[-1]+'/../'))
            if stat != 0:
                print '%s init failed!!' % project[-1]
