#-*- coding=utf-8 -*-
#!/usr/bin/env python
import re,os,sys,argparse,glob
from xml.dom import minidom
reload(sys) 
sys.setdefaultencoding('utf8')

def get_attrvalue(node, attrname):
     return node.getAttribute(attrname) if node else ''

def get_nodevalue(node, index = 0):
    try:
        return node.childNodes[index].nodeValue if node else ''
        #return node.childNodes[index].data if node else ''
    except:
        return ''

def get_xmlnode(node, name):
    return node.getElementsByTagName(name) if node else []

#返回子node包含的值
def get_xmlnode_return_value(node, name):
    try:
        getted_node = get_xmlnode(node, name)
        node_value = get_nodevalue(getted_node[0])
    except:
        node_value = ''
    return node_value
    
#返回子node指定属性值
def get_xmlnode_return_attrvalue(node, child_node_name, child_node_attrname):
    getted_node = get_xmlnode(node, child_node_name)
    return get_attrvalue(getted_node[0], child_node_attrname)
    
#返回第一个子node的nodeName
def get_xmlnode_return_firstchild_nodename(node, node_name):
    getted_node = get_xmlnode(node, node_name)
    firstchild = getted_node[0].firstChild
    return firstchild.nodeName

#返回第一个子node的包含的node的value
def return_firstfirstchild_nodevalue(node):
    firstchild = node.firstChild
    firstfirstchild = firstchild.firstChild
    return get_nodevalue(firstfirstchild)

#返回第一个子node包含的node的childNodes
def return_firstfirstchild_nodes(node):
    firstchild = node.firstChild
    firstfirstchild = firstchild.firstChild
    return firstfirstchild.childNodes

def parse_xml_data(filename, outfile_handle):
    doc = minidom.parse(filename) 
    root = doc.documentElement
    project_list = get_xmlnode(root, 'DocumentSummary')
    #out = open(outfile, 'w')
    for project in project_list:
        project_node = get_xmlnode(project, 'Project')
        if project_node:
            ProjectID_node = get_xmlnode(project_node[0], 'ProjectID')
            ArchiveID_node = get_xmlnode(ProjectID_node[0], 'ArchiveID')
            bioproject_accession = get_attrvalue(ArchiveID_node[0], 'accession')
            print bioproject_accession
            ProjectDescr_node = get_xmlnode(project_node[0], 'ProjectDescr')
            Title_node = get_xmlnode(ProjectDescr_node[0], 'Title')
            Title = get_nodevalue(Title_node[0])
            try:
                Description_node = get_xmlnode(ProjectDescr_node[0], 'Description')
                Description = get_nodevalue(Description_node[0])
            except:
                Description = ''

            Submission_node = get_xmlnode(project, 'Submission')
            submission_id = get_attrvalue(Submission_node[0], 'submission_id')
            submitted_time = get_attrvalue(Submission_node[0], 'submitted')
            last_update = get_attrvalue(Submission_node[0], 'last_update')
            
            project_full_info_list = [bioproject_accession, Title, Description, submission_id, submitted_time, last_update,filename]
            project_full_info = '\t'.join([i.replace('\t', ' ') for i in project_full_info_list])+'\n'
            outfile_handle.write(project_full_info)
        else:
            pass
        
if __name__ == '__main__':
    description = 'statistic sra experiment data!\n'
    quick_usage = 'python '+sys.argv[0]+' -indir indir_containing_xml\n'
    newParser = argparse.ArgumentParser( description = description, usage = quick_usage );
    newParser.add_argument( '-indir', dest='indir', help='indir containing xml', default='./20180925' );
    newParser.add_argument( '-outdir', dest='outdir', help='outdir', default=os.getcwd() );
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    indir = argsDict['indir']
    outdir = argsDict['outdir']
    indir_basename = os.path.basename(indir.rstrip('/'))
    project_outfile = outdir+'/'+indir_basename+'_project.xls'
    project_outfile_handle = open(project_outfile, 'w')
    
    for xml_file in glob.glob(indir+'/*.xml'):
        print '%s parse begin!' % xml_file
        parse_xml_data(filename = xml_file, outfile_handle = project_outfile_handle)
        #print '%s parse finished!' % xml_file
    project_outfile_handle.close()