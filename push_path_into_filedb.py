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

def write_file(file_handle, line):
    if line != '':
        file_handle.write(line+'\n')
    
def generate_sql_and_exec(created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, location, sql_output_handle):
    if type == 'folder':
        sql1 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, type, data_uuid, pid, recycle) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %d);' % (created_date, file_uuid, modified_date, name, owner_user_uuid, type, data_uuid, pid, 0)
        sql2 = ''
    else:
        sql1 = 'insert into t_file (created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, recycle) values ("%s", "%s", "%s", "%s", "%s", %d, "%s", "%s", "%s", %d);' % (created_date, file_uuid, modified_date, name, owner_user_uuid, size, type, data_uuid, pid, 0)
        sql2 = 'insert into t_file_data (created_date, data_uuid, location, size, status, storage_type, owner_user_uuid) values ("%s", "%s", "%s", %d, "FINISH", "FS", "%s");' % (created_date, data_uuid, location, size, owner_user_uuid)
    write_file(sql_output_handle, sql1)
    write_file(sql_output_handle, sql2)
 
#推送单个文件 
def push_file(physical_dir_path, pid, owner_user_uuid, sql_output_handle):
    if os.path.exists(physical_dir_path):
        created_date = get_file_create_time(physical_dir_path)
        file_uuid = uuid.uuid1()
        feedback = subprocess.Popen('/share/nas1/limh/judgeFileType/judgeFileType %s' % physical_dir_path, stdout=subprocess.PIPE, shell=True)
        type = feedback.stdout.read().strip()
        parent_uuid = pid
        size = os.path.getsize(physical_dir_path)
        name = physical_dir_path.rstrip('/').split('/')[-1]
        data_uuid = uuid.uuid1()
        generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, pid, physical_dir_path, sql_output_handle)
        return file_uuid
    else:
        pass
        
#只推送一层目录        
def push_only_one_dir(physical_dir_path, pid, owner_user_uuid, sql_output_handle):
    dir_name = os.path.basename(physical_dir_path)
    cursor.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and name="%s" and pid="%s" and recycle!=1 and field_1!="delete" ' % (user_uuid, dir_name, pid))
    search_result = cursor.fetchone()

    if not search_result and os.path.exists(physical_dir_path):
        created_date = get_file_create_time(physical_dir_path)
        file_uuid = uuid.uuid1()
        type = 'folder'
        parent_uuid = pid
        name = physical_dir_path.rstrip('/').split('/')[-1]
        data_uuid = uuid.uuid1()
        size = 'NULL' #文件夹不会插入size字段
        generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, physical_dir_path, sql_output_handle)
        return file_uuid
    elif search_result and os.path.exists(physical_dir_path):
        cursor.scroll(0,mode='absolute')
        return search_result[0]
    else:
        print '%s is not exists!' % physical_dir_path
        return ''

#迭代推送指定目录下所有文件和文件夹
def push_dir(physical_dir_path, physical_dir_pid, owner_user_uuid, sql_output_handle):
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
                generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, abs_path, sql_output_handle)
                push_dir(abs_path, file_uuid, owner_user_uuid, sql_output_handle)
            else:
                feedback = subprocess.Popen('/share/nas1/limh/judgeFileType/judgeFileType %s' % abs_path, stdout=subprocess.PIPE, shell=True)
                type = feedback.stdout.read().strip()
                size = os.path.getsize(abs_path)
                generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, abs_path, sql_output_handle)
    else:
        print '%s is not exists!' % physical_dir_path

#只推送目录下的所有文件，不推送文件夹
def push_dir_files(physical_dir_path, physical_dir_pid, owner_user_uuid, sql_output_handle):
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
                generate_sql_and_exec(created_date, file_uuid, created_date, name, owner_user_uuid, size, type, data_uuid, parent_uuid, abs_path, sql_output_handle)
    else:
        print '%s is not exists!' % physical_dir_path

def file_not_in_db_then_push(cursor, file_path, pid, user_uuid, sql_output_handle):
    file_name = file_path.rstrip('/').split('/')[-1]
    cursor.execute('select file_uuid, name, owner_user_uuid, type, pid from t_file where owner_user_uuid="%s" and pid="%s" and name="%s" and recycle!=1 and field_1!="delete"' % (user_uuid, pid, file_name))
    search_result = cursor.fetchone()
    if not search_result and os.path.exists(file_path):
        pushed_file_uuid = push_file(file_path, pid, user_uuid, sql_output_handle)
    elif search_result and os.path.exists(file_path):
        cursor.scroll(0,mode='absolute')
        pushed_file_uuid = ''
    else:    
        print '[[ERROR]] %s does not exists!' % file_path
        pushed_file_uuid = ''
    return pushed_file_uuid

def write_dic_into_file(file_handle, d):
    for k,v in d.items():
        write_file(file_handle, k+' ==> '+v)
    
if __name__ == '__main__':
    description = ''
    quick_usage = 'python '+sys.argv[0]+' -user_name 8a828b82518483d30151848a950d05e4 -pid xxxx\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-user_name', dest='user_name', help='user_name', default='ref_dev' );
    newParser.add_argument( '-file_path', dest='file_path', help='file_path:file or dir' );
    newParser.add_argument( '-pid', dest='pid', help='pid');
    newParser.add_argument( '-env', dest='env', help='envirenment:dev/rtm/online/yz', default='online' );
    
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
    pid = argsDict['pid']
    file_path = argsDict['file_path']
    env = argsDict['env']
    
    if env=='dev':
        host = '10.3.128.50'
        user = 'dev_cloud'
        passwd = 'dev_cloud.123'
        main_db = 'dev_cloud'
        file_db = 'dev_biocloud_files'
        file_db_user = 'dev_cloud'
        file_db_passwd = 'dev_cloud.123'
        modules = 'http://10.3.128.98:8093'
    if env=='rtm':
        host = '10.3.129.50'
        user = 'rtm_cloud'
        passwd = '123.rtm_cloud..bmk'
        main_db = 'rtm_cloud'
        file_db = 'rtm_biocloud_files'
        file_db_user = 'rtm_cloud'
        file_db_passwd = '123.rtm_cloud..bmk'
        modules = 'http://10.3.128.91:8091'
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
        main_db = 'cloud'
        file_db = 'biocloud_files'
        modules = 'http://10.3.128.38:8091'
    
    temp_file = '/share/nas1/liuw/sql_files/push_file_into_filedb.log'
    os.system('touch '+temp_file)
    log_file = open(temp_file, 'a')
    sql_output_file = '/share/nas1/liuw/sql_files/push_file_into_filedb.sql'
    os.system('rm '+sql_output_file)
    os.system('touch '+sql_output_file)
    sql_output_handle = open(sql_output_file, 'w')
    
    conn_cloud = MySQLdb.connect(host=host, user=user, passwd=passwd, db=main_db, charset="utf8")
    cursor = conn_cloud.cursor()
    cursor.execute("SET NAMES utf8");
    cursor.execute('select id from t_user where username="'+user_name+'";')
    user_uuid = cursor.fetchone()
    user_uuid = user_uuid[0]
    write_file(log_file, 'user_uuid %s' % user_uuid)
    write_file(log_file, 'pid %s' % pid)
    write_file(log_file, 'file_path %s' % file_path)
    cursor.scroll(0,mode='absolute') #将光标重置
    
    file_db_port = 3306
    if env=='online':
        feedback = subprocess.Popen( 'python /share/nas2/genome/cloud_soft/api_monitor/fileSystem/getDataBaseByUserId.py '+user_uuid, stdout=subprocess.PIPE, shell=True )
        feedback_lines = feedback.stdout.read()
        pattern = re.compile(r'.*host="(.*)", db="publish_biocloud_files", port=(\d+).*', re.S)
        file_db_host = pattern.match(feedback_lines).groups()[0]
        host = file_db_host
        file_db_port = pattern.match(feedback_lines).groups()[1]
        file_db_port = int(file_db_port)
        print 'file_db_host: %s' % file_db_host
        print 'file_db_port: %s' % file_db_port
    
    conn_biocloud_files = MySQLdb.connect(host=host, user=file_db_user, passwd=file_db_passwd, db=file_db, port=file_db_port, charset="utf8")
    cursor = conn_biocloud_files.cursor()
    if os.path.exists(file_path) and os.path.isfile(file_path):
        file_not_in_db_then_push(cursor, file_path, pid, user_uuid, sql_output_handle)
    elif os.path.exists(file_path) and os.path.isdir(file_path):
        dir_uuid = push_only_one_dir(file_path, pid, user_uuid, sql_output_handle)
        push_dir(file_path, dir_uuid, user_uuid, sql_output_handle)
    else:
        write_file(log_file, '%s is not exists!' % file_path)
    write_file(log_file, '===========finish============')
    log_file.close()
    sql_output_handle.close()