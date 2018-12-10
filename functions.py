from keystoneauth1 import session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client as ks3client
from neutronclient.v2_0 import client as nt3client
from novaclient.v2.client import client as nv2client
# from credentials import get_nova_creds
import glanceclient.v2.client as glclient

import json
import sys
import re
import subprocess
import os
import time
# from colorama import Fore, Back, Style
# from termcolor import colored, cprint


def get_var(varname):

    '''
    MENGAMBIL VARENV DARI LUARM PYTHON

    '''

    nf = open("rc.api3", "r")
    rc = nf.read()

    CMD = 'echo $(source ' + rc + '; echo $%s)' % varname
    p = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    out_ = p.stdout.readlines()[0].strip()
    return out_.decode('utf-8')


def get_auth():

    OS_PROJECT_DOMAIN_NAME = get_var('OS_PROJECT_DOMAIN_NAME')
    OS_USER_DOMAIN_NAME = get_var('OS_USER_DOMAIN_NAME')
    OS_PROJECT_NAME = get_var('OS_PROJECT_NAME')
    OS_USERNAME = get_var('OS_USERNAME')
    OS_PASSWORD = get_var('OS_PASSWORD')
    OS_AUTH_URL = get_var('OS_AUTH_URL')

    '''
    print('OS_PASSWORD ' + OS_PASSWORD)
    print('OS_AUTH_URL ' + OS_AUTH_URL)
    print('OS_PROJECT_DOMAIN_NAME ' + OS_PROJECT_DOMAIN_NAME)
    print('OS_USER_DOMAIN_NAME ' + OS_USER_DOMAIN_NAME)
    print('OS_PROJECT_NAME ' + OS_PROJECT_NAME)
    print('OS_USERNAME ' + OS_USERNAME)
    print('\n\n\t\t------------------------\n\n')
    '''

    auth = v3.Password(auth_url=OS_AUTH_URL,
                       username=OS_USERNAME,
                       password=OS_PASSWORD,
                       project_name=OS_PROJECT_NAME,
                       user_domain_name=OS_USER_DOMAIN_NAME,
                       project_domain_id=OS_PROJECT_DOMAIN_NAME
                       )
    return auth


def get_sess():
    return session.Session(auth=get_auth())


def get_keystone():
    return ks3client.Client(session=get_sess())


def get_neutron():
    return nt3client.Client(session=get_sess())


def get_nova():
    return nv2client.Client(version='2.0', session=get_sess())


def get_glance():
    return glclient.Client(session=get_sess())


def jsonBeauty(str):
    '''
    https://stackoverflow.com/questions/9105031/how-to-beautify-json-in-python#32093503
    '''

    from pygments import highlight, lexers, formatters

    formatted_json = json.dumps(json.loads(str), indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    return colorful_json


def customprint(string):
    ul_ = str(string)
    if ul_ == '[]':
        ul_ = '(not found)'
    else:
        if re.search('\[\]', str(ul_)) is None:
            ul_ = ul_.replace('[', '[\n')
            ul_ = ul_.replace(']', '\n]')
        ul_ = ul_.replace('>, <', '>\n,\n<')
        ul_ = ul_.replace('}, {', '}\n,\n{')
        ul_ = ul_.replace(', ', '\n,\t')
    return ul_


def toJSON(listOutput):
    datas = []
    typedata = type(listOutput)
    # print(typedata)
    if re.search("'list'", str(typedata)):
        for data in listOutput:
            datas.append(str(data.to_dict()))
        joindata = ', ' . join(datas)
        jsonString_merged = json.dumps(joindata, indent=4)
        return customprint(jsonString_merged)
    else:
        # print('listOutput = ' + str(listOutput))
        try:
            return customprint(str(listOutput.to_dict()))
        except IndexError:
            return ''


def search_respond204(string):
    return re.search('\[204\]', str(string))


def parsing(data, var):
    if re.search(var, str(data)):
        out = data.strip().split(' ' + var + '=')[1]
        out = out.strip().split(',')[0]
        return out
    else:
        return ''


def domainList():
    print('=====================')
    print('List Domain')
    print('---------------------')
    print('DOMAIN'.ljust(15, ' '), 'ID'.ljust(35, ' '), 'DESC.'.ljust(35, ' '), 'CREATOR.'.ljust(35, ' '))
    ks = get_keystone()
    dl = ks.domains.list()
    for dom in dl:
        json_str = json.dumps(dom.to_dict())
        resp = json.loads(json_str)
        # print(resp)
        if re.search('createdby', str(json_str)):
            createdby = resp['createdby'].ljust(20, ' ')
        else:
            createdby = ''
        print(f.bold + fg.green + resp['name'].ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), resp['description'].ljust(35, ' '), createdby)
    print('=====================\n')


def userList(cari_name=''):
    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List User' + f.reset)
    if cari_name != '':
        cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
        print('name = ' + cari_name_)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    ks = get_keystone()
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    UserRC_username = get_var('OS_USERNAME')
    print('USERNAME'.ljust(15, ' '), 'ID'.ljust(35, ' '), 'DOMAIN'.ljust(15, ' '), 'PROJECT'.ljust(15, ' '), 'DESC.'.ljust(35, ' '), 'CREATOR.'.ljust(35, ' '))
    if is_admin(UserRC_username):
        getuserlist = ks.users.list()
    else:
        getuserlist = ks.users.list(domain=UserRC_domain_id)
    for data in getuserlist:
        json_str = json.dumps(data.to_dict())
        resp = json.loads(json_str)
        if resp['domain_id'] is not None:
            getdomain = parsing(data=str(ks.domains.get(domain=resp['domain_id'])), var='name')
        else:
            getdomain = ''
        if re.search('default_project_id', str(data)):
            def_pro_id = parsing(str(data), 'default_project_id')
            if len(def_pro_id) == 32:
                # print('def_pro_id = ' + def_pro_id)
                getproject = parsing(data=str(ks.projects.get(project=def_pro_id)), var='name')
            else:
                getproject = def_pro_id + ' (?)'
        else:
            getproject = ''
        if re.search('createdby', str(json_str)):
            createdby = resp['createdby'].ljust(35, ' ')
        else:
            createdby = ''
        if re.search('description', str(json_str)):
            description = resp['description'].ljust(35, ' ')
        else:
            description = ''

        if cari_name != '':
            if re.search(cari_name, resp['name']):
                print(f.bold + fg.green + resp['name'].ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), getdomain.ljust(15, ' '), getproject.ljust(15, ' '), description, createdby)
        else:
            print(f.bold + fg.green + resp['name'].ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), getdomain.ljust(15, ' '), getproject.ljust(15, ' '), description, createdby)
    print('=====================\n')


def projectList(domain=''):
    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Project' + f.reset)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    print('PROJECT'.ljust(15, ' '), 'ID'.ljust(35, ' '), 'DOMAIN'.ljust(15, ' '), 'DESC.'.ljust(35, ' '), 'CREATOR.'.ljust(35, ' '))
    UserRC_username = get_var('OS_USERNAME')
    ks = get_keystone()
    if is_admin(UserRC_username):
        if domain != '':
            pl = ks.projects.list(domain=domain)
        else:
            pl = ks.projects.list()
    else:
        if domain == get_var('OS_PROJECT_DOMAIN_NAME'):
            pl = ks.projects.list(domain=get_var('OS_PROJECT_DOMAIN_NAME'))
        else:
            pl = ks.projects.list(domain=None)
    for pro in pl:
        json_str = json.dumps(pro.to_dict())
        resp = json.loads(json_str)
        if re.search('createdby', str(json_str)):
            createdby = resp['createdby'].ljust(20, ' ')
        else:
            createdby = ''
        if resp['domain_id'] is not None:
            getdomain = parsing(data=str(ks.domains.get(domain=resp['domain_id'])), var='name')
        else:
            getdomain = ''
        print(f.bold + fg.green + resp['name'].ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), getdomain.ljust(15, ' '), resp['description'].ljust(35, ' '), createdby)
    print('=====================\n')


def roleList():
    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Role' + f.reset)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    UserRC_username = get_var('OS_USERNAME')
    ks = get_keystone()
    if is_admin(UserRC_username):
        getDomainList = ks.domains.list()
        print('ROLE'.ljust(15, ' '), 'ID'.ljust(35, ' '), 'DOMAIN'.ljust(15, ' '))
        for dom in getDomainList:
            json_str = json.dumps(dom.to_dict())
            resp = json.loads(json_str)
            # print('dom id = ' + resp['id'])
            getRoleList = ks.roles.list(domain_id=resp['id'])
            for role in getRoleList:
                json_str = json.dumps(role.to_dict())
                resp = json.loads(json_str)
                # print(resp['domain_id'])
                if resp['domain_id'] is not None:
                    getdomain = parsing(data=str(ks.domains.get(domain=resp['domain_id'])), var='name')
                else:
                    getdomain = ''
                respname = resp['name']
                print(f.bold + fg.green + respname.ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), getdomain)
        getRoleList2 = ks.roles.list()
        for role2 in getRoleList2:
            json_str = json.dumps(role2.to_dict())
            resp = json.loads(json_str)
            if resp['domain_id'] is not None:
                getdomain = parsing(data=str(ks.domains.get(domain=resp['domain_id'])), var='name')
            else:
                getdomain = ''
            respname = resp['name']
            print(f.bold + fg.green + respname.ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), getdomain)
    else:
        getRoleList = ks.roles.list(domain_id=UserRC_domain_id)
        for role in getRoleList:
            json_str = json.dumps(role.to_dict())
            resp = json.loads(json_str)
            if resp['domain_id'] is not None:
                getdomain = parsing(data=str(ks.domains.get(domain=resp['domain_id'])), var='name')
            else:
                getdomain = ''
            print(f.bold + fg.green + resp['name'] + f.reset)
            print('id :', resp['id'])
            print('domain :', getdomain)
            print('\n')
    print('=====================\n')


def networkList(cari_name='', cari_id='', childs=False, header=True):
    ks = get_keystone()
    nt = get_neutron()
    if header is True:
        if cari_id != '':
            caption = 'Show '
        else:
            caption = 'List '
        print('\n')
        print(f.bold + fg.blue + '=====================' + f.reset)
        print(f.bold + fg.blue + caption + 'Network' + f.reset)
        if cari_name != '':
            cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
            print('name = ' + cari_name_)
        print(f.bold + fg.blue + '---------------------' + f.reset)
    else:
        pass
    if cari_id != '':
        netlist = nt.show_network(network=cari_id)
        jdumps = json.dumps(netlist, indent=4, sort_keys=True)
        jloads = json.loads(jdumps)
        print(customprint(jloads))

    else:
        # project_id = ks.projects.list
        netlist = nt.list_networks()
        jdumps = json.dumps(netlist, indent=4, sort_keys=True)
        jloads = json.loads(jdumps)
        print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'PROJECT'.ljust(15, ' '), 'STATUS.'.ljust(10, ' '), 'DESC.'.ljust(35, ' '))
        for data in jloads['networks']:
            if len(data['project_id']) == 32:
                getproject = parsing(data=str(ks.projects.get(project=data['project_id'])), var='name')
            else:
                getproject = data['project_id'] + '(?)'
            if cari_name != '':
                if re.search(cari_name, data['name']):
                    print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))
                    print('\n')
                    print(data)
                    print('\n\n')
                    # if childs is True:
                    #     subnetList(cari_name='', cari_network=data['id'], printout=True, header=False)
                    #     portList(cari_name='', cari_network=data['id'], header=False)
            else:
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))
            if childs is True:
                print(fg.blue + 'Subnet List' + f.reset)
                subnetList(cari_name='', cari_network=data['id'], printout=True, header=False)
                print(fg.blue + 'Port List' + f.reset)
                portList(cari_name='', cari_network=data['id'], parents=False, header=False)
                print('\n\n')


def subnetList(cari_name='', cari_network='', printout=True, header=True):
    if printout is True:
        if header is True:
            print('\n')
            print(f.bold + fg.blue + '=====================' + f.reset)
            print(f.bold + fg.blue + 'List Subnet.' + f.reset)
            if cari_name != '':
                cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
                print('name = ' + cari_name_)
            print(f.bold + fg.blue + '---------------------' + f.reset)
        else:
            pass
    else:
        pass

    ks = get_keystone()
    nt = get_neutron()
    subnetlist = nt.list_subnets()
    jdumps = json.dumps(subnetlist, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    if printout is True:
        print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'PROJECT'.ljust(15, ' '), 'NET.'.ljust(17, ' '), 'GATEWAY.'.ljust(17, ' '), 'DESC.'.ljust(35, ' '))
    output_count_num = 0
    for data in jloads['subnets']:
        if len(data['project_id']) == 32:
            getproject = parsing(data=str(ks.projects.get(project=data['project_id'])), var='name')
        else:
            getproject = data['project_id'] + '(?)'
        if len(data['network_id']) == 36:
            listnet = nt.list_networks(id=data['network_id'])
            listnet_json_loads = json.loads(json.dumps(listnet))
            # print(listnet_json_loads['networks'][0]['name'])
            getnet = listnet_json_loads['networks'][0]['name']
        else:
            getnet = data['network_id'] + '(?)'
        # getnet = ''
        if cari_name != '':
            if re.search(cari_name, data['name']):
                output_count_num += 1
                if printout is True:
                    print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getnet.ljust(17, ' '), data['gateway_ip'].ljust(17, ' '), data['description'].ljust(35, ' '))
                    print('\n')
                    print(data)
        elif cari_network != '':
            if re.search(cari_network, data['network_id']):
                # print('\n')
                # print(data)
                output_count_num += 1
                if printout is True:
                    print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getnet.ljust(17, ' '), data['gateway_ip'].ljust(17, ' '), data['description'].ljust(35, ' '))
        else:
            output_count_num += 1
            if printout is True:
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getnet.ljust(17, ' '), data['gateway_ip'].ljust(17, ' '), data['description'].ljust(35, ' '))

    if output_count_num > 0:
        if printout is True:
            # print('Num. Data = ' + str(output_count_num))
            # print('=========================\n')
            pass
        else:
            return str(output_count_num)


def routerList(cari_name=''):

    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Router' + f.reset)
    if cari_name != '':
        cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
        print('name = ' + cari_name_)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    ks = get_keystone()
    nt = get_neutron()
    netlist = nt.list_routers()
    jdumps = json.dumps(netlist, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    # print(jloads)
    # print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'EXT-IP'.ljust(15, ' '), 'PROJECT'.ljust(15, ' '), 'STATUS.'.ljust(10, ' '), 'DESC.'.ljust(35, ' '))
    print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'EXT-IP'.ljust(15, ' '), 'NET.'.ljust(20, ' '), 'PROJECT'.ljust(15, ' '), 'STATUS.'.ljust(10, ' '))
    for data in jloads['routers']:
        net_id = ''
        net_name = ''
        ext_ip = ''
        getproject = ''
        if len(data['project_id']) == 32:
            getproject = parsing(data=str(ks.projects.get(project=data['project_id'])), var='name')
        else:
            getproject = data['project_id'] + '(?)'
        if re.search('external_fixed_ips', str(data)):
            try:
                ext_ip = data['external_gateway_info']['external_fixed_ips'][0]['ip_address']
            except IndexError:
                ext_ip = '(not set)'
        else:
            ext_ip = '(not set)'
        # print(data['external_gateway_info'])
        if re.search('network_id', str(data)):
            try:
                net_id = data['external_gateway_info']['network_id']
                net = nt.show_network(network=net_id)
                net_name = net['network']['name']
            except IndexError:
                net_id = ''
                net_name = ''
        if cari_name != '':
            # 'external_gateway_info': {'enable_snat': True, 'external_fixed_ips': [{'ip_address': '103.30.145.206'
            if re.search(cari_name, data['name']):
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), ext_ip.ljust(15, ' '), net_name.ljust(20, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '))
                print('\n')
                print(data)
                print('\n\n')
        else:
            print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), ext_ip.ljust(15, ' '), net_name.ljust(20, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '))


def portList(cari_name='', cari_id='', cari_network='', parents=True, header=True):
    if header is True:
        if cari_id != '':
            caption = 'Show '
        else:
            caption = 'List '
        print('\n')
        print(f.bold + fg.blue + '=====================' + f.reset)
        print(f.bold + fg.blue + caption + 'Port' + f.reset)
        if cari_name != '':
            cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
            print('name = ' + cari_name_)
        print(f.bold + fg.blue + '---------------------' + f.reset)
    ks = get_keystone()
    nt = get_neutron()
    if cari_id != '':
        portlist = nt.show_port(port=cari_id)
        jdumps = json.dumps(portlist, indent=4, sort_keys=True)
        jloads = json.loads(jdumps)
        print(customprint(jloads))
    elif cari_name != '':
        portlist = nt.list_ports()
        jdumps = json.dumps(portlist, indent=4, sort_keys=True)
        jloads = json.loads(jdumps)
        # print(jloads)
        print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'PROJECT'.ljust(15, ' '), 'ROUTER'.ljust(25, ' '), 'STATUS.'.ljust(10, ' '), 'DESC.'.ljust(35, ' '))
        for data in jloads['ports']:
            # print(data)
            if len(data['project_id']) == 32:
                getproject = parsing(data=str(ks.projects.get(project=data['project_id'])), var='name')
            else:
                getproject = data['project_id'] + '(?)'
            getroutername = ''
            if data['device_id'] != '':
                getrouterlist = nt.list_routers(id=data['device_id'])
                try:
                    getroutername = getrouterlist['routers'][0]['name']
                except IndexError:
                    pass
            if cari_name != '':
                if re.search(cari_name, data['name']):
                    print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getroutername.ljust(25, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))
                    print('\n')
                    print(data)
                    print('\n\n')
            elif cari_network != '':
                # if re.search(cari_network, data['network_id']):
                if data['network_id'] == cari_network:
                    # print('\n')
                    # print(data)
                    print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getroutername.ljust(25, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))
                    if parents is True:
                        print('Network:')
                        networkList(cari_name='', cari_id=data['network_id'], childs=False, header=False)
                        print('\n')
            else:
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getroutername.ljust(25, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))
                if parents is True:
                    print('Network:')
                    networkList(cari_name='', cari_id=data['network_id'], childs=False, header=False)
                    print('\n')


def floatinIPList(cari_name=''):

    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Floating IP' + f.reset)
    if cari_name != '':
        cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
        print('name = ' + cari_name_)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    ks = get_keystone()
    nt = get_neutron()
    floatingiplist = nt.list_floatingips()
    jdumps = json.dumps(floatingiplist, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    # print(jloads)
    print('Floating IP'.ljust(20, ' '), 'ID'.ljust(40, ' '), 'PROJECT'.ljust(15, ' '), 'Fixed IP'.ljust(15, ' '), 'STATUS.'.ljust(10, ' '), 'NET.'.ljust(35, ' '))
    for data in jloads['floatingips']:
        # print(data)
        if len(data['project_id']) == 32:
            getproject = parsing(data=str(ks.projects.get(project=data['project_id'])), var='name')
        else:
            getproject = data['project_id'] + '(?)'
        if data['port_details'] is not None:
            if len(data['port_details']['network_id']) == 36:
                listnet = nt.list_networks(id=data['port_details']['network_id'])
                listnet_json_loads = json.loads(json.dumps(listnet))
                # print(listnet_json_loads['networks'][0]['name'])
                getnet = listnet_json_loads['networks'][0]['name']
            else:
                getnet = data['port_details']['network_id'] + '(?)'
        else:
            getnet = '(not set)'
        if data['floating_ip_address'] is not None:
            floatingip = data['floating_ip_address']
        else:
            floatingip = '(not set)'
        if data['fixed_ip_address'] is not None:
            fixedip = data['fixed_ip_address']
        else:
            fixedip = '(not set)'
        if cari_name != '':
            if re.search(cari_name, data['name']):
                print('\n')
                print(data)
                print(f.bold + fg.green + floatingip.ljust(20, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), fixedip.ljust(10, ' '), data['status'].ljust(10, ' '), getnet.ljust(35, ' '))
        else:
            print(f.bold + fg.green + floatingip.ljust(20, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), fixedip.ljust(15, ' '), data['status'].ljust(10, ' '), getnet.ljust(35, ' '))


def imageList(cari_name=''):

    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Image' + f.reset)
    if cari_name != '':
        cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
        print('name = ' + cari_name_)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    # ks = get_keystone()
    # nt = get_neutron()
    gl = get_glance()
    imagelist = list(gl.images.list())
    # print(imagelist)
    jdumps = json.dumps(imagelist, indent=4, sort_keys=True)
    # print(jdumps)
    jloads = json.loads(jdumps)
    # print(jloads)
    # print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'EXT-IP'.ljust(15, ' '), 'PROJECT'.ljust(15, ' '), 'STATUS.'.ljust(10, ' '), 'DESC.'.ljust(35, ' '))
    print('NAME'.ljust(35, ' '), 'ID'.ljust(40, ' '), 'SIZE'.ljust(15, ' '), 'STATUS.'.ljust(10, ' '))
    for data in jloads:
        # print(data)
        if cari_name != '':
            if re.search(cari_name, data['name']):
                # print('\n')
                # print(data)
                print(f.bold + fg.green + data['name'].ljust(35, ' ') + f.reset, data['id'].ljust(40, ' '), str('{:,}' . format(data['size'])).rjust(15, ' '), data['status'].ljust(20, ' '))
        else:
            print(f.bold + fg.green + data['name'].ljust(35, ' ') + f.reset, data['id'].ljust(40, ' '), str('{:,}' . format(data['size'])).rjust(15, ' '), data['status'].ljust(20, ' '))


def flavorList():

    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Flavor' + f.reset)
    print(f.bold + fg.blue + '---------------------' + f.reset)

    flavorList = nv.flavors.list()
    # print(flavorList)
    flavorList = str(flavorList).strip().split('<Flavor: ')
    # print(flavorList)
    for data in flavorList:
        # print(str(data))
        if re.search('jc', data):
            print(data.strip().split('>')[0])


def nextName_network_v1():
    nt = get_neutron()
    list_ = nt.list_networks()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    data_coll = ''
    coll = []
    next_name = ''
    for data in jloads['networks']:
        if re.search('network', data['name']) and re.search('.' + get_var('OS_USERNAME'), data['name']):
            data_name = data['name'].strip().split('network')[1]
            data_queu = data_name.strip().split('.')[0]
            coll.append(data_queu)
        data_coll = ' ' . join(coll)
    for tryQue in range(1, 20):
        if re.search(str(tryQue), data_coll):
            print('sudah ada >> network' + str(tryQue) + '.' + get_var('OS_USERNAME'))
        else:
            next_name = 'network' + str(tryQue) + '.' + get_var('OS_USERNAME')
            break
    data_coll = ''
    return next_name


def nextName_network():
    import time
    next_name = 'network' + str(time.time()).strip().split('.')[0] + '.' + get_var('OS_USERNAME')
    return next_name


def nextName_subnet_v1():
    nt = get_neutron()
    list_ = nt.list_subnets()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    data_coll = ''
    coll = []
    for data in jloads['subnets']:
        if re.search('subnet', data['name']) and re.search('.' + get_var('OS_USERNAME'), data['name']):
            data_name = data['name'].strip().split('subnet')[1]
            data_queu = data_name.strip().split('.')[0]
            coll.append(data_queu)
        data_coll = ' ' . join(coll)
    for tryQue in range(1, 20):
        if re.search(str(tryQue), data_coll):
            print('sudah ada >> subnet' + str(tryQue) + '.' + get_var('OS_USERNAME'))
        else:
            next_name = 'subnet' + str(tryQue) + '.' + get_var('OS_USERNAME')
            break
    data_coll = ''
    return next_name


def nextName_subnet():
    import time
    next_name = 'subnet' + str(time.time()).strip().split('.')[0] + '.' + get_var('OS_USERNAME')
    return next_name


def nextName_router_v1():
    nt = get_neutron()
    list_ = nt.list_routers()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    data_coll = ''
    coll = []
    for data in jloads['routers']:
        if re.search('router', data['name']) and re.search('.' + get_var('OS_USERNAME'), data['name']):
            data_name = data['name'].strip().split('router')[1]
            data_queu = data_name.strip().split('.')[0]
            coll.append(data_queu)
        data_coll = ' ' . join(coll)
    print(data_coll)
    for tryQue in range(1, 20):
        if re.search(str(tryQue), data_coll):
            print('sudah ada >> router' + str(tryQue) + '.' + get_var('OS_USERNAME'))
        else:
            next_name = 'router' + str(tryQue) + '.' + get_var('OS_USERNAME')
            break
    data_coll = ''
    return next_name


def nextName_router():
    import time
    next_name = 'router' + str(time.time()).strip().split('.')[0] + '.' + get_var('OS_USERNAME')
    return next_name


def nextName_port_v1():
    nt = get_neutron()
    list_ = nt.list_ports()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    data_coll = ''
    coll = []
    for data in jloads['ports']:
        if re.search('port', data['name']) and re.search('.' + get_var('OS_USERNAME'), data['name']):
            data_name = data['name'].strip().split('port')[1]
            data_queu = data_name.strip().split('.')[0]
            coll.append(data_queu)
        data_coll = ' ' . join(coll)
    for tryQue in range(1, 20):
        if re.search(str(tryQue), data_coll):
            print('sudah ada >> port' + str(tryQue) + '.' + get_var('OS_USERNAME'))
        else:
            next_name = 'port' + str(tryQue) + '.' + get_var('OS_USERNAME')
            break
    data_coll = ''
    return next_name


def nextName_port():
    import time
    next_name = 'port' + str(time.time()).strip().split('.')[0] + '.' + get_var('OS_USERNAME')
    return next_name


def nextName_instance_v1():
    nv = get_nova()
    list_ = nv.servers.list()
    if len(list_) > 0:
        data_coll = ''
        coll = []
        for data in list_:
            if data is not None or data != '':
                data = str(data)
                # print(data)
                try:
                    if re.search('instance', data) and re.search('.' + get_var('OS_USERNAME'), data):
                        data_name = data.strip().split('instance')[1]
                        # print(data_name)
                        data_queu = data_name.strip().split('.')[0]
                        # print(data_queu)
                        coll.append(data_queu)
                    data_coll = ' ' . join(coll)
                except IndexError:
                    data_coll = ''
        for tryQue in range(1, 20):
            if re.search(str(tryQue), data_coll):
                print('sudah ada >> instance' + str(tryQue) + '.' + get_var('OS_USERNAME'))
            else:
                next_name = 'instance' + str(tryQue) + '.' + get_var('OS_USERNAME')
                break
        data_coll = ''
    else:
        next_name = 'instance.' + get_var('OS_USERNAME')
    return next_name


def nextName_instance():
    import time
    next_name = 'instance' + str(time.time()).strip().split('.')[0] + '.' + get_var('OS_USERNAME')
    return next_name


def is_admin(username):
    ks = get_keystone()
    userlogin_id = ks.users.list(name=get_var('OS_USERNAME'))
    userlogin_id = parsing(data=str(userlogin_id), var='id')
    # print('userlogin_id = ' + userlogin_id)
    role_assignments = ks.role_assignments.list(user=userlogin_id)
    is_admin = False
    if re.search('19c6ed1d6fce4b38952193ab6b25dce9', str(role_assignments)):
        is_admin = True
        # print('is_admin = ' + is_admin)
    return is_admin


def cek_ada_data(object, name, domain=''):
    nama = False
    if object == 'domains':
        cek1 = ks.domains.list(name=name)
    if object == 'projects':
        cek1 = ks.projects.list(name=name)
    if object == 'users':
        cek1 = ks.rules.list(name=name)
    if object == 'rules':
        cek1 = ks.users.list(name=name)
    for data in cek1:
        json_str = json.dumps(data.to_dict())
        resp = json.loads(json_str)
        nama = resp['name']
    if nama == name:
        return True
    else:
        return False


def availableIpPublic(ipprefix, inputstr):
    # ipprefix : 111.111.111.
    ip_avail = subprocess.check_output('nmap -sP ' + ipprefix + '0/24', shell=True)
    x = str(ip_avail).strip().split(ipprefix)
    found = 0
    for xx in x:
        xxx = str(xx).strip().split(')\\n')
        if str(xxx[0]) == str(inputstr):
            # 1 : not avail
            found = 1
            break
        else:
            found = 0
    return found


def get_availableIpPublic(ipprefix):
    # ipprefix : 111.111.111.
    ip_avail = subprocess.check_output('nmap -sP ' + ipprefix + '0/24', shell=True)
    x = str(ip_avail).strip().split('WIB')
    x = str(x[1]).strip().split(ipprefix)
    for tryIP in range(171, 220):
        deret_ipup = ''
        ips_up = []
        for xx in list(x):
            ip_suffix = str(xx).strip().split(")\\nHost ")[0]
            ips_up.append(str(ip_suffix))
        deret_ipup = ' ' . join(ips_up)
        if re.search(str(tryIP), deret_ipup) is None:
            break
    return ipprefix + str(tryIP)


def get_availableGatewayIp():

    nt = get_neutron()
    sl = nt.list_subnets()
    ips_ready = []
    deret_gateway = ''
    for tryIP in range(100, 200):
        deret_gateway = ''
        ips_ready = []
        for dsl in sl['subnets']:
            dsl1 = ''
            if dsl['gateway_ip'] != '':
                try:
                    dsl1 = str(dsl['gateway_ip']).strip().split('192.168.')[1]
                    # print(dsl1)
                    dsl2 = dsl1.strip().split('.')[0]
                    ips_ready.append(str(dsl2))
                except IndexError:
                    continue
        deret_gateway = ' ' . join(ips_ready)
        if re.search(str(tryIP), deret_gateway) is None:
            break

    return tryIP


class f:
    '''Colors class:reset all colors with colors.reset; two
    sub classes fg for foreground
    and bg for background; use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.greenalso, the generic bold, disable,
    underline, reverse, strike through,
    and invisible work with the main class i.e. colors.bold'''
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'


class fg:
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'
    lightgrey = '\033[37m'
    darkgrey = '\033[90m'
    lightred = '\033[91m'
    lightgreen = '\033[92m'
    yellow = '\033[93m'
    lightblue = '\033[94m'
    pink = '\033[95m'
    lightcyan = '\033[96m'


class bg:
    black = '\033[40m'
    red = '\033[41m'
    green = '\033[42m'
    orange = '\033[43m'
    blue = '\033[44m'
    purple = '\033[45m'
    cyan = '\033[46m'
    lightgrey = '\033[47m'
