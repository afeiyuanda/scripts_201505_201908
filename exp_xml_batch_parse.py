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
    exp_list = get_xmlnode(root, 'EXPERIMENT_PACKAGE')
    #out = open(outfile, 'w')
    for exp in exp_list:
        exp_node = get_xmlnode(exp, 'EXPERIMENT')
        exp_accession = get_attrvalue(exp_node[0], 'accession')
        print exp_accession
        exp_title = get_xmlnode_return_value(exp_node[0], 'TITLE')
        study_ref_accession = get_xmlnode_return_attrvalue(exp_node[0], 'STUDY_REF', 'accession')
        design_node = get_xmlnode(exp_node[0], 'DESIGN')
        design_description = get_xmlnode_return_value(design_node[0], 'DESIGN_DESCRIPTION')
        sample_accession = get_xmlnode_return_attrvalue(design_node[0], 'SAMPLE_DESCRIPTOR', 'accession')
        library_descriptor_node = get_xmlnode(design_node[0], 'LIBRARY_DESCRIPTOR')
        library_strategy = get_xmlnode_return_value(library_descriptor_node[0], 'LIBRARY_STRATEGY')
        library_source = get_xmlnode_return_value(library_descriptor_node[0], 'LIBRARY_SOURCE')
        library_selection = get_xmlnode_return_value(library_descriptor_node[0], 'LIBRARY_SELECTION')
        library_layout = get_xmlnode_return_firstchild_nodename(library_descriptor_node[0], 'LIBRARY_LAYOUT')
        platform_node = get_xmlnode(exp_node[0], 'PLATFORM')
        platform = return_firstfirstchild_nodevalue(platform_node[0])
        #SUBMISSION
        submission_node = get_xmlnode(exp, 'SUBMISSION')
        submission_accession = get_attrvalue(submission_node[0], 'accession')
        #Organization，有些exp xml中没有，如id=1810797
        organization_node = get_xmlnode(exp, 'Organization')
        if organization_node:
            organization_type = get_attrvalue(organization_node[0], 'type')
            organization_name = get_xmlnode_return_value(organization_node[0], 'Name')
            organization = organization_type+':'+organization_name
            #organization = organization.replace('\t', ' ')
        else:
            organization = ''
        #STUDY
        study_node = get_xmlnode(exp, 'STUDY')
        study_identifiers_node = get_xmlnode(study_node[0], 'IDENTIFIERS')
        external_id_node = get_xmlnode(study_identifiers_node[0], 'EXTERNAL_ID')
        bioproject = ''
        for n in external_id_node:
            if get_attrvalue(n, 'namespace') == 'BioProject':
                bioproject = get_nodevalue(n)
                break
            #elif get_attrvalue(n, 'namespace') == 'GEO':
            #    geoproject = get_nodevalue(n)
        external_id_node = []
        descriptor_node = get_xmlnode(study_node[0], 'DESCRIPTOR')
        study_title = get_xmlnode_return_value(descriptor_node[0], 'STUDY_TITLE')
        study_abstract = get_xmlnode_return_value(descriptor_node[0], 'STUDY_ABSTRACT')
        #有些没有项目摘要，而是项目描述：STUDY_DESCRIPTION，之后再优化吧
        try:
            study_link = get_xmlnode(study_node[0], 'STUDY_LINKS')
            xref_line_nodes = return_firstfirstchild_nodes(study_link[0])
            magazine_db = get_nodevalue(xref_line_nodes[0]) #获取杂志名字
            magazine_id = get_nodevalue(xref_line_nodes[1]) #获取文章ID
            magazine = magazine_db+':'+magazine_id
        except:
            magazine = ''
        if not bioproject:
            try:
                related_studies_node = get_xmlnode(descriptor_node[0], 'RELATED_STUDIES')
                related_link_nodes = get_xmlnode(related_studies_node[0], 'RELATED_STUDY')
                bioproject = get_xmlnode_return_value(related_link_nodes[0], 'LABEL')
            except:
                print 'bioproject info does not getted!'
        
        #SAMPLE
        sample_node = get_xmlnode(exp, 'SAMPLE')
        if sample_node:
            sample_identifiers_node = get_xmlnode(sample_node[0], 'IDENTIFIERS')
            external_id_node = get_xmlnode(sample_identifiers_node[0], 'EXTERNAL_ID')
            for n in external_id_node:
                #if n.nodeName = 'PRIMARY_ID':
                #    sample_accession = get_nodevalue(n)
                if get_attrvalue(n, 'namespace') == 'BioSample':
                    biosample = get_nodevalue(n)
                    break
            if 'biosample' not in dir():
                submitter_id_node = get_xmlnode(sample_identifiers_node[0], 'SUBMITTER_ID')
                for n in submitter_id_node:
                    if get_attrvalue(n, 'namespace') == 'BioSample':
                        biosample = get_nodevalue(n)
                        break
            # try:
                # sample_title = get_xmlnode_return_value(sample_node[0], 'TITLE')
            # except:
                # sample_title = ''
            sample_title = get_xmlnode_return_value(sample_node[0], 'TITLE')
            taxon_node = get_xmlnode(sample_node[0], 'SAMPLE_NAME')
            taxon_id = get_xmlnode_return_value(taxon_node[0], 'TAXON_ID')
            taxon_name = get_xmlnode_return_value(taxon_node[0], 'SCIENTIFIC_NAME')
            try:
                sample_attributes_node = get_xmlnode(sample_node[0], 'SAMPLE_ATTRIBUTES')
                sample_attributes = ''
                for sample_attribute in sample_attributes_node[0].childNodes:
                    tag = get_xmlnode_return_value(sample_attribute, 'TAG')
                    value = get_xmlnode_return_value(sample_attribute, 'VALUE')
                    attribute = tag+'::'+value+';;'
                    sample_attributes += attribute
                sample_attributes = sample_attributes.rstrip(';')
            except:
                sample_attributes = ''
        else:
            biosample, sample_title, taxon_id, taxon_name, sample_attributes = '','','','',''
        #RUN_SET,id=249695 has two run
        run_nodes = get_xmlnode(exp, 'RUN_SET')
        if run_nodes:
            run_info = ''
            for run_node in run_nodes[0].childNodes:
                run_accession = get_attrvalue(run_node, 'accession')
                run_total_bases = get_attrvalue(run_node, 'total_bases')
                run_size = get_attrvalue(run_node, 'size')
                run_published = get_attrvalue(run_node, 'published')
                run_info += '%s,%s,%s,%s;' % (run_accession, run_total_bases, run_size, run_published)
            run_info = run_info.rstrip(';')
        else:
            run_info = ''
        #ControlledAccess
        controlledaccess_nodes = get_xmlnode(exp, 'ControlledAccess')
        if controlledaccess_nodes:
            access = 'ControlledAccess'
        else:
            access = 'PublicAccess'
        
        exp_full_info_list = [exp_accession, exp_title, study_ref_accession, design_description, sample_accession, library_strategy, library_source, library_selection, library_layout, platform, bioproject, submission_accession, organization, study_title, study_abstract, magazine, biosample, sample_title, taxon_id, taxon_name, sample_attributes, run_info, access, filename]
        exp_full_info = '\t'.join([i.replace('\t', ' ') for i in exp_full_info_list])+'\n'
        outfile_handle.write(exp_full_info)
        
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
    exp_outfile = outdir+'/'+indir_basename+'_exp.xls'
    exp_outfile_handle = open(exp_outfile, 'w')
    
    for xml_file in glob.glob(indir+'/*.xml'):
        print '%s parse begin!' % xml_file
        parse_xml_data(filename = xml_file, outfile_handle = exp_outfile_handle)
        #print '%s parse finished!' % xml_file
    exp_outfile_handle.close()