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

        if name != '':
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
    ks = get_keystone()
    nt = get_neutron()
    if cari_id != '':
        netlist = nt.show_network(network=cari_id)
        jdumps = json.dumps(netlist, indent=4, sort_keys=True)
        jloads = json.loads(jdumps)
        print(customprint(jloads))

    else:
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
    coll = []
    next_name = ''
    for tryQue in range(1, 20):
        for data in jloads['networks']:
            if re.search('network', data['name']) and re.search('.' + get_var('OS_USERNAME'), data['name']):
                data_name = data['name'].strip().split('network')[1]
                data_queu = data_name.strip().split('.')[0]
                coll.append(data_queu)
        data_coll = ' ' . join(coll)
        if re.search(str(tryQue), data_coll):
            print('sudah ada >> network' + str(tryQue) + '.' + get_var('OS_USERNAME'))
        else:
            next_name = 'network' + str(tryQue) + '.' + get_var('OS_USERNAME')
            break
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
    coll = []
    for tryQue in range(1, 20):
        for data in jloads['subnets']:
            if re.search('subnet', data['name']) and re.search('.' + get_var('OS_USERNAME'), data['name']):
                data_name = data['name'].strip().split('subnet')[1]
                data_queu = data_name.strip().split('.')[0]
                coll.append(data_queu)
        data_coll = ' ' . join(coll)
        if re.search(str(tryQue), data_coll):
            print('sudah ada >> subnet' + str(tryQue) + '.' + get_var('OS_USERNAME'))
        else:
            next_name = 'subnet' + str(tryQue) + '.' + get_var('OS_USERNAME')
            break
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
    return next_name


def nextName_port():
    import time
    next_name = 'port' + str(time.time()).strip().split('.')[0] + '.' + get_var('OS_USERNAME')
    return next_name


def nextName_instance_v1():
    list_ = nv.servers.list()
    if len(list_) > 0:
        num = 0
        for data in list_:
            if re.search('instance', str(data)):
                num += 1
        if num > 0:
            num = num + 1
            next_name = 'instance' + str(num) + '.' + get_var('OS_USERNAME')
        else:
            next_name = 'instance.' + get_var('OS_USERNAME')
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


argv1 = ''
try:
    argv1 = sys.argv[1]
except IndexError:
    print('\n$ os {condition}')
    thisfile = open(__file__, "r")
    tfc = str(thisfile.read())
    tfc = tfc.replace('      ', ' ')
    tfc = tfc.replace('     ', ' ')
    tfc = tfc.replace('    ', ' ')
    tfc = tfc.replace('   ', ' ')
    tfc = tfc.replace('  ', ' ')
    tfc = tfc.replace('\t', ' ')
    tfc = tfc.replace('\n', '')
    argv = tfc.strip().split('# start argv ---')[2]
    prints = argv.strip().split('if argv1 == \'')
    print('\nConditions :')
    x = 0
    printsplit_1 = ''
    printsplit_2 = ''
    for argv_1 in prints:
        split1 = str(argv_1).strip().split('\': \'\'\'')
        for split2 in split1:
            if x == 0:
                # deskripsi
                printsplit_1 = split2
                printsplit_1_split = printsplit_1.strip().split("'''")[0]
            elif x == 1:
                # kondisi
                printsplit_2 = split2
            x += 1
            if x == 2:
                x = 0
        if printsplit_2 != '':
            print(f.bold + fg.green + printsplit_2.ljust(20, ' ') + f.reset, f.disable + printsplit_1_split + f.reset)
    print('\n')


# start argv ---

if argv1 == 'rc':
    '''
    source login dari file rc

    '''
    ks = get_keystone()
    print('==================')
    print('Mengganti file rc.')
    print('==================')
    nf = open("rc.api3", "r")
    rc = nf.read()
    print('rc aktif = ' + rc.strip())
    os.system('cat ' + rc.strip())
    try:
        rcname = sys.argv[2]
    except IndexError:
        os.system('echo "" ; echo "------- LIST FILE RC -------" ; echo "" ; ls *rc ; echo "" ; echo "---------------------" ; echo "" ;')
        rcname = input('Pilih file rc : ')

    if os.path.exists(rcname) and os.access(rcname, os.R_OK):
        if rcname is None:
            rcname = 'ajirc'
            print('Default rc : ' + rcname)
        else:
            print('Ganti rc : ' + rcname)
        f = open("rc.api3", "w+")
        f.write(rcname)
        f.close()
        os.system('cat ' + rcname)
    else:
        print('rc tsb tidak ada.')

elif argv1 == 'dlist':
    '''
    domain list
    '''
    print('\n-----------------\nDOMAIN LIST\n------------------\n')
    try:
        _keypress = ''
        ks = get_keystone()

        print('Tunggu...')

        domainList()

    except IndexError:
        print('ERROR')

elif argv1 == 'dcreate':
    '''
    create domain
    '''
    print('\n-----------------\nCREATE DOMAIN\n------------------\n')
    UserRC_username = get_var('OS_USERNAME')
    ks = get_keystone()

    try:
        name = sys.argv[2]
    except IndexError:
        name = input('Nama domain : ')

    if name == '':
        exit('Batal bikin domain.')

    if cek_ada_data(object='domains', name=name):
        exit('Nama domain "' + name + '" sudah ada.')

    desc = 'dibikin pake ' + __file__

    print('Tunggu...')

    if name is not None:

        try:
            dc = ks.domains.create(name=name, description=desc, createdby=UserRC_username)
            # print(toJSON(dc))
            if dc:
                print('"' + name + '" created !')
                domainList()
            else:
                print('Failde while create domain "' + name + '"')

        except IndexError:
            print('Error while create domain.')

    else:

        print('Lengkapi input!')

elif argv1 == 'ddisable':
    '''
    disable domain
    '''
    print('\n-----------------\nDISABLE DOMAIN\n------------------\n')
    ks = get_keystone()
    try:
        name = sys.argv[2]
    except IndexError:
        domainList()
        name = input('Nama domain : ')
    if name == '':
        exit('Batal disable domain.')
    if cek_ada_data(object='domains', name=name):
        dl = ks.domains.list(name=name)
        domain_id = parsing(data=str(dl), var='id')
        print('domain_id = ' + domain_id)
        update = ks.domains.update(domain=domain_id, enabled=False)
        print(toJSON(update))

elif argv1 == 'ddelete':
    '''
    delete domain
    '''
    print('\n-----------------\nDELETE DOMAIN\n------------------\n')
    ks = get_keystone()
    try:
        name = sys.argv[2]
    except IndexError:
        domainList()
        name = input('Nama domain : ')
    if name == '':
        exit('Batal bikin domain.')
    if cek_ada_data(object='domains', name=name):

        dl = ks.domains.list(name=name)
        strdl = str(dl)
        print('\nData yang akan dihapus : ')
        print(toJSON(dl))

        # status enable ??
        isEnabled = parsing(data=strdl, var='enabled')

        # id domain
        strid = parsing(data=strdl, var='id')

        # domain dipake di user ?
        domuser = ks.users.list(domain=strid)
        domuser_count = len(domuser)

        # domain dipake di project ?
        projectuser = ks.projects.list(domain=strid)
        projectuser_count = len(projectuser)

        if isEnabled != 'True':
            if domuser_count < 1:
                if projectuser_count < 1:
                    if strid is not None:
                        try:
                            ud = ks.domains.delete(domain=strid)
                            if search_respond204(ud):
                                print('Domain "' + name + '" sudah dihapus')
                            else:
                                print('Domain "' + name + '" tidak terhapus')
                        except IndexError:
                            print('Proses hapus gagal.')
                    else:
                        print('ID domain tidak ditemukan.')
                else:
                    print('Domain dipake project.')
            else:
                print('Domain dipake user.')
        else:
            print('Domain "' + name + '" tidak bisa dihapus karena masih "Enabled"')
    else:

        print('Lengkapi input!')

elif argv1 == 'ulist':
    '''
    user list
    '''
    print('\n-----------------\nUSER LIST\n------------------\n')
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    ks = get_keystone()
    try:
        name = sys.argv[2]
    except IndexError:
        name = input('Cari nama user : ')
    print('Tunggu...')
    # if name is None or name == '':
    #     ul = ks.users.list(domain=UserRC_domain_id)
    # else:
    #     ul = ks.users.list(name=name, domain=UserRC_domain_id)
    # print(toJSON(ul))
    # print('Jum. data : {0}' . format(len(ul)))
    userList(cari_name=name)

elif argv1 == 'ucreate':
    '''
    create user
    '''
    print('\n-----------------\nCREATE USER\n------------------\n')

    ks = get_keystone()
    name = ''
    cek = ''
    desc = 'dibikin pake ' + __file__
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    UserRC_domain_name = get_var('OS_USER_DOMAIN_NAME')
    UserRC_username = get_var('OS_USERNAME')

    try:
        name = sys.argv[2]
    except IndexError:
        name = input('Nama user : ')

    if len(name) < 1:
        exit()

    if UserRC_domain_id == 'default':
        domainList()
        domain = input('Pilih domain: ')
    else:
        domain = UserRC_domain_id

    if len(domain) < 1:
        exit()

    if UserRC_domain_id == 'default':
        dl = ks.domains.list(name=domain)
    else:
        dl = ks.domains.list(name=UserRC_domain_name)
    if len(dl) < 1:
        print('Domain tidak ditemukan.')
        exit()
    else:
        if UserRC_domain_id == 'default':
            domain = parsing(data=str(dl), var='id')
        else:
            domain = UserRC_domain_id
        domain_name = parsing(data=str(dl), var='name')

    if UserRC_domain_id == 'default':
        cek = ks.users.list(name=name, domain=domain)
    else:
        cek = ks.users.list(name=name, domain=UserRC_domain_id)
    if len(cek) >= 1:
        print('User "' + name + '" sudah terdaftar dengan domain "' + domain_name + '".')
        exit()

    print('Tunggu...')

    if name is not None and domain is not None:

        try:
            uc = ks.users.create(name=name, domain=domain, description=desc, createdby=UserRC_username)
            print(toJSON(uc))
            # print(customprint(uc))

        except IndexError:
            print('Error while create user.')

    else:

        print('Lengkapi input!')

elif argv1 == 'uupdate':
    '''
    update user
    '''
    print('\n-----------------\nUPDATE USER\n------------------\n')

    ks = get_keystone()
    name = ''
    cek = ''
    desc = 'dibikin pake ' + __file__
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    UserRC_domain_name = get_var('OS_USER_DOMAIN_NAME')

    userList()
    name = input('Pilih id user yang akan diupdate : ')
    if len(name) <= 0:
        exit()
    # cekuser = ks.users.get(user=name)
    # print('cekuser = ' + str(cekuser))

    '''
    domainList()
    domain = input('Pilih id domain baru: ')
    if domain is not None:
        try:
            uu = ks.users.update(user=name, domain=domain)
            print(toJSON(uu))
        except IndexError:
            print('Error while update user domain.')
    >>> keystoneauth1.exceptions.http.BadRequest: Cannot change Domain ID (HTTP 400)

    '''
    try:
        what = sys.argv[2]
        if sys.argv[2] == 'project':
            print('\n-----------------\nUPDATE USER : PROJECT\n------------------\n')
            projectList()
            project = input('Pilih project baru: ')
            if len(project) > 0:
                try:
                    upro = ks.users.update(user=name, project=project)
                    print(toJSON(upro))

                except IndexError:
                    print('Error while update user project.')
            else:
                pass

            # uu = ks.users.update(user=name, domain=domain)
            # NameError: name 'domain' is not defined

        if sys.argv[2] == 'password':
            print('\n-----------------\nUPDATE USER : PASSWORD\n------------------\n')
            password = ''
            while password == '' or len(password) < 5:
                password = input('Pasang password baru (min. 5 karakter): ')

            try:
                upass = ks.users.update(user=name, password=password)
                print(toJSON(upass))
            except IndexError:
                print('Error while update user password.')
    except IndexError:
        print('Error :\nContoh cmd : ks uupdate {project|password}')

elif argv1 == 'udelete':
    '''
    delete user
    '''
    print('\n-----------------\nDELETE USER\n------------------\n')
    ks = get_keystone()
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    UserRC_username = get_var('OS_USERNAME')
    try:
        name = sys.argv[2]
    except IndexError:
        userList()
        name = input('Pilih id user : ')
    if name == '':
        exit('Batal hapus user.')
    print('Tunggu...')

    if name != '':
        if is_admin(UserRC_username):
            ul = ks.users.get(user=name)
        else:
            ul = ks.users.get(user=name, domain=UserRC_domain_id)
        cek = parsing(str(ul), 'id')
        # print(ul)
        # print(cek)
        if cek == name:
            strul = str(ul)
            project_id = parsing(data=strul, var='default_project_id')
            ul_user_domain_id = str(parsing(data=strul, var='domain_id'))
            if UserRC_domain_id == ul_user_domain_id:
                if project_id == '':
                    print('\nData yang akan dihapus : ')
                    print(customprint(ul))
                    strid = strul.strip().split(' id=')[1]
                    strid = strid.strip().split(',')[0]
                    try:
                        ud = ks.users.delete(user=strid)
                        if search_respond204(ud):
                            print('User "' + name + '" sudah dihapus')
                        else:
                            print('User "' + name + '" tidak terhapus')
                    except IndexError:
                        print('Proses hapus gagal.')
                else:
                    print(toJSON(ul))
                    print('User tersebut tidak bisa dihapus karena memiliki Project.')
            else:
                print('User tersebut tidak bisa dihapus karena bukan domain anda.')
        else:
            print('User tersebut tidak ada.')
    else:
        print('Lengkapi input!')

elif argv1 == 'plist':
    '''
    project list
    '''
    print('\n-----------------\nPROJECT LIST\n------------------\n')
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    try:
        ks = get_keystone()

        print('Tunggu...')

        projectList()

        # if is_admin(UserRC_username):
        #     pl = ks.projects.list()
        # else:
        #     pl = ks.projects.list(domain=UserRC_domain_id)
        # print(toJSON(pl))
        # print('Jum. data : {0}' . format(len(pl)))

    except IndexError:
        print('ERROR')

elif argv1 == 'pcreate':
    '''
    create project
    '''
    print('\n-----------------\nCREATE PROJECT\n------------------\n')
    ks = get_keystone()
    UserRC_username = get_var('OS_USERNAME')
    UserRC_domain_name = get_var('OS_USER_DOMAIN_NAME')
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    desc = 'dibikin pake ' + __file__

    name = input('Nama project : ')
    if name == '':
        exit('Batal bikin project.')

    if is_admin(UserRC_username):
        domainList()
        domain = input('Pilih id domain: ')
    else:
        domain = UserRC_domain_id

    if cek_ada_data(object='projects', name=name, domain=UserRC_domain_name):
        exit('Nama project tsb sudah ada.')

    print('Tunggu...')

    if name != '' and domain != '':

        pc = ks.projects.create(name=name, domain=domain, description=desc, createdby=UserRC_username)
        print(toJSON(pc))

    else:

        print('Lengkapi input!')

elif argv1 == 'pupdate':
    '''
    update project
    '''
    print('\n-----------------\nUPDATE PROJECT\n------------------\n')
    ks = get_keystone()
    UserRC_username = get_var('OS_USERNAME')
    UserRC_domain_name = get_var('OS_USER_DOMAIN_NAME')
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    desc = 'dibikin pake ' + __file__

    if is_admin(UserRC_username):
        projectList()
    else:
        projectList(domain=UserRC_domain_id)
    project = input('Pilih id project : ')
    if project == '':
        exit('Batal update project.')

    pget = ks.projects.get(project=project)
    strpl = str(pget)
    dom_id = parsing(strpl, 'domain_id')
    pro_name = parsing(strpl, 'name')
    if is_admin(UserRC_username) is False:
        if dom_id != UserRC_domain_id:
            exit('Project "' + pro_name + '" bukan domain anda')

    new_name = ''
    psearch = ''
    n = 0
    while len(new_name) < 5 or str(psearch) != '[]':
        new_name = input('Update dengan nama baru (min. 5 karakter) : ')
        psearch = ks.projects.list(name=new_name)
        # print(str(psearch))
        if str(psearch) != '[]':
            print('Nama project "' + new_name + '" sudah ada.')
        n += 1
        if n > 3:
            exit('Batal update nama baru.')

    pd = ks.projects.update(project=project, name=new_name, description=desc)
    # print(str(pd))
    updated_pro_name = parsing(str(pd), 'name')
    # print(updated_pro_name + ' == ' + new_name)
    if updated_pro_name == new_name:
        print('Project "' + pro_name + '" sudah diupdate menjadi "' + new_name + '"')
    else:
        print('Project "' + pro_name + '" tidak terupdate')

elif argv1 == 'pdelete':
    '''
    delete project
    '''
    print('\n-----------------\nDELETE PROJECT\n------------------\n')
    ks = get_keystone()
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')

    projectList()
    project = input('Pilih id project :')

    print('Tunggu...')

    if project != '':
        pget = ks.projects.get(project=project)
        strpl = str(pget)
        # print('\nData yang akan dihapus : ')
        # # print(strpl)
        # print(toJSON(pget))
        pro_id = parsing(strpl, 'id')
        dom_id = parsing(strpl, 'domain_id')
        pro_name = parsing(strpl, 'name')
        # print(dom_id)
        # print(UserRC_domain_id)
        if dom_id == UserRC_domain_id:
            pd = ks.projects.delete(project=pro_id)
            if search_respond204(pd):
                print('Project "' + pro_name + '" sudah dihapus')
            else:
                print('Project "' + pro_name + '" tidak terhapus')
        else:
            print('Project "' + pro_name + '" bukan domain anda')
    else:

        print('Lengkapi input!')

elif argv1 == 'rlist':
    '''
    role list
    '''
    print('\n-----------------\nROLE LIST\n------------------\n')
    try:
        _keypress = ''
        # ks = get_keystone()

        print('Tunggu...')

        roleList()

    except IndexError:
        print('ERROR')

elif argv1 == 'rgrant':
    '''
    grant role
    '''

    print('\n-----------------\nROLE GRANT\n------------------\n')
    ks = get_keystone()

    roleList()
    role = ''
    n = 0
    while role == '':
        n += 1
        role = input('Pilih id role : ')
        if n == 3:
            exit()
    get_role_dom = ks.roles.get(role=role)
    get_role_dom = parsing(data=str(get_role_dom), var='domain_id')

    userList()
    name = ''
    n = 0
    while name == '':
        n += 1
        name = input('Pilih id user yang akan di-role : ')
        if n == 3:
            exit()

    projectList(domain=get_role_dom)
    project = ''
    n = 0
    while project == '':
        n += 1
        project = input('Pilih id project yang akan di-role : ')
        if n == 3:
            exit()
    get_project_dom = ks.projects.get(project=project)
    get_project_dom = parsing(data=str(get_project_dom), var='domain_id')

    if role and name and project:
        getuser = ks.users.get(user=name)
        user_dom = parsing(data=str(getuser), var='domain_id')
        if get_role_dom == get_project_dom:
            update_role = ks.roles.grant(role=role, user=name, project=project)
            update_role = ks.roles.grant(role=role, user=name, domain=user_dom)
            # print(toJSON(update_role))
            ra = ks.role_assignments.list(user=name)
            print(toJSON(ra))
        else:
            print('Role dan Project harus di domain yang sama')

    '''
    user_pro = parsing(data=str(getuser), var='default_project_id')
    update_role = ks.roles.grant(user=name, role=role, project=user_pro)

    keystoneauth1.exceptions.http.Forbidden: Project 1c9f9000989b41939b18f670a8792bd8 must be in the same domain as the role 58451c34b78648caad45e6f9bf5f5191 being assigned. (HTTP 403) (Request-ID: req-9ce372f1-df24-4430-97ce-5e114adb237f)

    '''

# NEUTRON

elif argv1 == 'netlist':
    '''
    network list
    '''
    print('\n-----------------\nNETWORK LIST\n------------------\n')

    try:
        cari_name = sys.argv[2]
    except IndexError:
        cari_name = input('Cari nama network (kosongkan = semua nama) : ')
        networkList(cari_name=cari_name, childs=False, header=False)

elif argv1 == 'netcreate':
    '''
    create network
    * versi 2
    * network + subnet
    '''
    print('\n-----------------\nCREATE NETWORK\n------------------\n')
    ks = get_keystone()
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    name = ''
    n = 0
    networks = ''
    while name == '' or len(name) < 5 or len(networks['networks']) > 0:
        name = input('Nama network (min. 5 hurup) : ')
        networks = nt.list_networks(name=name)
        lennet = len(networks['networks'])
        if lennet > 0:
            print('Nama network "' + name + '" sudah ada.')
        n += 1
        if n >= 5:
            exit('Batal bikin network.')

    project_name = get_var('OS_PROJECT_NAME')
    p = ks.projects.list(name=project_name)
    project = parsing(data=str(p), var='id')

    if name != '' and project != '':
        network = {"name": name, "admin_state_up": True, "description": "via createnetcomplete@" + __file__ + ". createdby=" + UserRC_username, "project_id": project, "tenant_id": project}
        # print(network)
        result = nt.create_network({'network': network})
        j = json.dumps(result, indent=4)
        jl = json.loads(j)
        if name == jl['network']['name'] and project == jl['network']['project_id']:
            print('Network baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
            network_id = jl['network']['id']
            networkList(cari_name=name)
        else:
            print(f.red + 'Network baru ' + f.bold + name + f.reset + f.bold + ' tidak jadi.' + f.reset)

    print('\n-----------------\nCREATE SUBNET\n------------------\n')
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    name = nextName_subnet()
    network = network_id
    project_name = get_var('OS_PROJECT_NAME')
    p = ks.projects.list(name=project_name)
    project = parsing(data=str(p), var='id')

    gateway_parse3 = str(get_availableGatewayIp())

    if name != '':
        subnets = {'subnets': [
            {
                "name": name,
                "description": "via createnetcomplete@" + __file__ + ". createdby aji2",
                "enable_dhcp": "True",
                "dns_nameservers": ["8.8.8.8"],
                "allocation_pools": [{
                    "start": "192.168." + gateway_parse3 + ".2",
                    "end": "192.168." + gateway_parse3 + ".5",
                }],
                "gateway_ip": "192.168." + gateway_parse3 + ".1",
                "cidr": "192.168." + gateway_parse3 + ".0/24",
                'ip_version': 4,
                "network_id": network,
                "project_id": project,
                "tenant_id": project,
            }
        ]}
        # print(subnet)
        result = nt.create_subnet(body=subnets)
        j = json.dumps(result, indent=4)
        jl = json.loads(j)
        print(jl)
        if name == jl['subnets'][0]['name']:
            print('subnet baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
            subnetList(cari_name=name)
        else:
            print(f.red + 'subnet baru ' + f.bold + name + f.reset + f.bold + ' tidak jadi.' + f.reset)

elif argv1 == 'netcreate.v1':
    '''
    create network
    versi 1
    '''
    print('\n-----------------\nCREATE NETWORK\n------------------\n')
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    name = ''
    n = 0
    networks = ''
    while name == '' or len(name) < 5 or len(networks['networks']) > 0:
        name = input('Nama network (min. 5 hurup) : ')
        networks = nt.list_networks(name=name)
        lennet = len(networks['networks'])
        if lennet > 0:
            print('Nama network "' + name + '" sudah ada.')
        n += 1
        if n >= 5:
            exit('Batal bikin network.')

    if is_admin(UserRC_username):
        projectList()
    else:
        projectList(domain=UserRC_domain_id)
    project = ''
    n = 0
    while len(project) != 32:
        project = input('Pilih id project : ')
        n += 1
        if n >= 5:
            exit('Batal bikin network.')

    if name != '' and project != '':
        network = {"name": name, "admin_state_up": True, "description": "via createnetcomplete@" + __file__ + ". createdby=" + UserRC_username, "project_id": project, "tenant_id": project}
        # print(network)
        result = nt.create_network({'network': network})
        j = json.dumps(result, indent=4)
        jl = json.loads(j)
        if name == jl['network']['name'] and project == jl['network']['project_id']:
            print('Network baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
            networkList(cari_name=name)
        else:
            print(f.red + 'Network baru ' + f.bold + name + f.reset + f.bold + ' tidak jadi.' + f.reset)

elif argv1 == 'netupdate':
    '''
    update network
    '''
    print('\n-----------------\nUPDATE NETWORK\n------------------\n')
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    oname = ''
    n = 0
    networks = ''
    networkList()
    while oname == '':
        oname = input('Pilih id network : ')
        n += 1
        if n >= 5:
            exit('Batal update network.')

    name = ''
    n = 0
    networks = ''
    while name == '' or len(name) < 5 or len(networks['networks']) > 0:
        name = input('Nama baru network (min. 5 hurup) : ')
        networks = nt.list_networks(name=name)
        lennet = len(networks['networks'])
        if lennet > 0:
            print('Nama network "' + name + '" sudah ada.')
        n += 1
        if n >= 5:
            exit('Batal update network.')

    if oname != '' and name != '':
        network = {"name": name}
        # print(network)
        result = nt.update_network(network=oname, body={'network': network})
        print(result)
        j = json.dumps(result, indent=4)
        jl = json.loads(j)
        if name == jl['network']['name']:
            print('Ganti nama baru ' + f.bold + fg.green + name + f.reset + ' sukses.')
            networkList(cari_name=name)
        else:
            print(f.red + 'Ganti nama baru ' + f.bold + name + f.reset + f.bold + ' gagal.' + f.reset)

elif argv1 == 'subnetlist':
    '''
    network list
    '''
    print('\n-----------------\nSUBNET LIST\n------------------\n')

    try:
        cari_name = sys.argv[2]
    except IndexError:
        cari_name = input('Cari nama subnet (kosongkan = semua nama) : ')
    subnetList(cari_name)

elif argv1 == 'subnetcreate':
    '''
    create subnet
    '''
    print('\n-----------------\nCREATE SUBNET\n------------------\n')
    ks = get_keystone()
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    name = nextName_subnet()
    networkList()
    network = ''
    n = 0
    while len(network) != 36:
        network = input('Pilih id network : ')
        n += 1
        if n >= 5:
            exit('Batal bikin subnet.')

    project_name = get_var('OS_PROJECT_NAME')
    p = ks.projects.list(name=project_name)
    project = parsing(data=str(p), var='id')

    gateway_parse3 = str(get_availableGatewayIp())

    if name != '':
        subnets = {'subnets': [
            {
                "name": name,
                "description": "via createnetcomplete@" + __file__ + ". createdby aji2",
                "enable_dhcp": "True",
                "dns_nameservers": ["8.8.8.8"],
                "allocation_pools": [{
                    "start": "192.168." + gateway_parse3 + ".2",
                    "end": "192.168." + gateway_parse3 + ".5",
                }],
                "gateway_ip": "192.168." + gateway_parse3 + ".1",
                "cidr": "192.168." + gateway_parse3 + ".0/24",
                'ip_version': 4,
                "network_id": network,
                "project_id": project,
                "tenant_id": project,
            }
        ]}
        # print(subnet)
        result = nt.create_subnet(body=subnets)
        j = json.dumps(result, indent=4)
        jl = json.loads(j)
        print(jl)
        if name == jl['subnets'][0]['name']:
            print('subnet baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
            subnetList(cari_name=name)
        else:
            print(f.red + 'subnet baru ' + f.bold + name + f.reset + f.bold + ' tidak jadi.' + f.reset)

elif argv1 == 'routerlist':
    '''
    router list
    '''
    print('\n-----------------\nROUTER LIST\n------------------\n')

    try:
        cari_name = sys.argv[2]
    except IndexError:
        cari_name = input('Cari nama router (kosongkan = semua nama) : ')
    routerList(cari_name)

elif argv1 == 'routercreate':
    '''
    create router
    versi 2
    '''
    ks = get_keystone()
    nt = get_neutron()

    router_name = nextName_router_v1()
    print('\n\n' + fg.yellow + 'Bikin router "' + router_name + '"' + f.reset)

    project_name = get_var('OS_PROJECT_NAME')
    p = ks.projects.list(name=project_name)
    project_id = parsing(data=str(p), var='id')
    if len(project_id) != 32:
        exit('Project tidak dikenal : ' + project_id)
    nt.format = 'json'

    # ip_add = ''
    # print('\n\n' + fg.lightgrey + 'Cari available ip....' + f.reset)
    # while ip_add is False or ip_add == '':
    #     ip_add = get_availableIpPublic(ipprefix='103.30.145.')
    # print('\n\n' + fg.lightgrey + 'available ip : "' + fg.green + ip_add + '"' + f.reset)

    request = {
        'router':
        {
            "name": router_name,
            "admin_state_up": True,
            "description": "via createnetcomplete@" + __file__ + ". createdby=" + get_var('OS_USERNAME'),
            "project_id": project_id,
            "tenant_id": project_id,
            "external_gateway_info": {
                "enable_snat": "True",
                "external_fixed_ips": [{
                    # "ip_address": ip_add,
                    "subnet_id": "4639e018-1cc1-49cc-89d4-4cad49bd4b89"
                }],
                "network_id": "d10dd06a-0425-49eb-a8ba-85abf55ac0f5"
            }
        }
    }
    router = nt.create_router(request)
    router_id = router['router']['id']
    router = nt.show_router(router_id)
    # print(router)
    routerList(cari_name=router_name)

    if router_id is not None:
        networkList()
        network_id = ''
        n = 0
        while len(network_id) != 36:
            network_id = input('Pilih id network : ')
            n += 1
            if n >= 5:
                exit('Batal bikin subnet.')
                nt.delete_router(router_id)
        port_name = nextName_port_v1()
        print('\n\n' + fg.yellow + 'Bikin port "' + port_name + '"' + f.reset)

        subnet_search_network = nt.list_subnets(network_id=network_id)
        # print(subnet_search_network)
        subnet_id = subnet_search_network['subnets'][0]['id']
        # print(subnet_id)
        gateway_parse3_1 = str(subnet_search_network['subnets'][0]['cidr']).strip().split('192.168.')[1]
        # print(gateway_parse3_1)
        gateway_parse3 = gateway_parse3_1.strip().split('.0')[0]
        # print(gateway_parse3)

        body_value = {
            'port': {
                'admin_state_up': True,
                'device_id': router_id,
                'name': port_name,
                'network_id': network_id,
                # 'binding:host_id': 'rocky-controller.jcamp.net',
                # 'binding:profile': {},
                # 'binding:vnic_type': 'normal',
                'fixed_ips': [{
                    'subnet_id': subnet_id,
                    'ip_address': '192.168.' + gateway_parse3 + '.1'
                }],
            }
        }
        print(customprint(body_value))

        response = nt.create_port(body=body_value)
        # print(response)
        portList(cari_name=port_name)

elif argv1 == 'routercreate.v1':
    '''
    create router
    versi 1
    '''
    print('\n-----------------\nCREATE ROUTER\n------------------\n')
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    name = ''
    n = 0
    routers = ''
    while name == '' or len(name) < 5 or len(routers['routers']) > 0:
        name = input('Nama router (min. 5 hurup) : ')
        routers = nt.list_routers(name=name)
        lennet = len(routers['routers'])
        if lennet > 0:
            print('Nama router "' + name + '" sudah ada.')
        n += 1
        if n >= 5:
            exit('Batal bikin router.')

    if is_admin(UserRC_username):
        projectList()
    else:
        projectList(domain=UserRC_domain_id)

    project = ''
    n = 0
    while len(project) != 32:
        project = input('Pilih id project : ')
        n += 1
        if n >= 5:
            exit('Batal bikin router.')

    if name != '' and project != '':
        router = {"name": name, "admin_state_up": True, "description": "via createnetcomplete@" + __file__ + ". createdby=" + UserRC_username, "project_id": project, "tenant_id": project}
        # print(router)
        result = nt.create_router({'router': router})
        j = json.dumps(result, indent=4)
        jl = json.loads(j)
        if name == jl['router']['name'] and project == jl['router']['project_id']:
            print('router baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
            routerList(cari_name=name)
        else:
            print(f.red + 'router baru ' + f.bold + name + f.reset + f.bold + ' tidak jadi.' + f.reset)

elif argv1 == 'routerupdate':
    '''
    update router
    '''
    print('\n-----------------\nUPDATE ROUTER\n------------------\n')
    print('\n+ ip_address: 103.30.145.0/24\n+ sub-ext-net(ready)\n+ ext-net(ready)\n')
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    name = ''
    n = 0
    router = ''
    routerList()
    while router == '':
        router = input('\nPilih id router : ')
        n += 1
        if n >= 3:
            exit('Batal update router.')

    ip_add = ''
    israngetrue = False
    val = ''
    while ip_add == '' or israngetrue is not True or availableIpPublic == 1:
        ip_add = input('\nMemasang Ip untuk router ini.\nTambahkan akhiran ip antara 171 ~ 220 : 103.30.145.')
        # print('akan diproses : 103.30.145.' + str(ip_add))
        # print(int(ip_add))
        availableIpPublic = availableIpPublic(ipprefix='103.30.145.', inputstr=ip_add)
        if availableIpPublic == 1:
            print('\nIP "' + ip_add + '" tidak bisa digunakan.')
            ip_add = ''
        elif int(ip_add) < 221 or int(ip_add) > 170:
            israngetrue = True
        elif int(ip_add) > 221 or int(ip_add) < 170:
            israngetrue = False
            print('\nPilih antara 171 ~ 220 !')
            ip_add = ''
        else:
            exit('Batal pasang IP.')
    ip_add = '103.30.145.' + str(ip_add)
    yakin = ''
    while yakin != 'ya':
        yakin = input('\nYakin akan menggunakan ip "' + ip_add + '" ? (ya/tidak)')
        if yakin == 'tidak' or yakin == '':
            exit('Batal pasang IP.')
    if ip_add != '':
        bodyu = {
            'router':
            {
                "external_gateway_info": {
                    "enable_snat": "True",
                    "external_fixed_ips": [{
                        "ip_address": ip_add,
                        "subnet_id": "4639e018-1cc1-49cc-89d4-4cad49bd4b89"
                    }],
                    "network_id": "d10dd06a-0425-49eb-a8ba-85abf55ac0f5"
                }
            }
        }
        ur = nt.update_router(router=router, body=bodyu)


# 'external_gateway_info': {'enable_snat': True, 'external_fixed_ips': [{'ip_address': '103.30.145.206', 'subnet_id': '4639e018-1cc1-49cc-89d4-4cad49bd4b89'}], 'network_id': 'd10dd06a-0425-49eb-a8ba-85abf55ac0f5'}

elif argv1 == 'port':
    '''
    * port list
    * -c = create
    * id:xxxxxxx = cari id port
    '''
    try:
        arg2 = sys.argv[2]
    except IndexError:
        arg2 = ''
    if arg2 == '':
        print('\n-----------------\nPORT LIST\n------------------\n')

        try:
            cari_name = sys.argv[2]
        except IndexError:
            cari_name = input('Cari nama port (kosongkan = semua nama) : ')
        portList(cari_name)

    elif re.search('id:', arg2):
        print('\n-----------------\nCARI PORT by ID\n------------------\n')
        try:
            cari_id = sys.argv[2]
            if len(cari_id) > 3:
                cari_id = cari_id.strip().split("id:")[1]
            else:
                cari_id = input('Cari id port : ')
        except IndexError:
            cari_id = input('Cari id port : ')
        portList(cari_id=cari_id)

    elif arg2 == '-c':

        print('\n-----------------\nCREATE PORT\n------------------\n')
        nt = get_neutron()
        UserRC_username = get_var('OS_USERNAME')

        n = 0
        router = ''
        routerList()
        while router == '':
            router = input('\nPilih id router : ')
            n += 1
            if n >= 3:
                exit('Batal update port.')

        networkList()
        network = ''
        n = 0
        while len(network) != 36:
            network = input('\nPilih id network : ')
            n += 1
            if n >= 5:
                exit('Batal bikin port.')

        # name = ''
        # n = 0
        # ports = ''
        # while name == '' or len(name) < 5 or len(ports['ports']) > 0:
        #     name = input('Nama port (min. 5 hurup) : ')
        #     ports = nt.list_ports(name=name)
        #     lennet = len(ports['ports'])
        #     if lennet > 0:
        #         print('Nama port "' + name + '" sudah ada.')
        #     n += 1
        #     if n >= 5:
        #         exit('Batal bikin port.')
        name = nextName_port()
        subnet_search_network = subnet_id = nt.list_subnets(network_id=network)
        subnet = subnet_search_network['subnets'][0]['id']
        gateway_parse3_1 = str(subnet_search_network['subnets'][0]['cidr']).strip().split('192.168.')[1]
        gateway_parse3 = gateway_parse3_1.strip().split('.0')[0]
        # exit(gateway_parse3)
        if name != '':
            # device_id = router_id
            body_value = {
                'port': {
                    'admin_state_up': True,
                    'device_id': router,
                    'name': name,
                    'network_id': network,
                    'binding:host_id': 'rocky-controller.jcamp.net',
                    'binding:profile': {},
                    'binding:vnic_type': 'normal',
                    # 'fixed_ips': [{
                    #     'subnet_id': subnet,
                    #     'ip_address': '192.168.' + gateway_parse3 + '.1'
                    # }],
                }
            }
            result = nt.create_port(body=body_value)
            j = json.dumps(result, indent=4)
            jl = json.loads(j)
            if name == jl['port']['name']:
                print('port baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
                portList(cari_name=name)
            else:
                print(f.red + 'port baru ' + f.bold + name + f.reset + f.bold + ' tidak jadi.' + f.reset)

    else:
        print(arg2)
        print('\n \
        * -c = create \
        * id:xxxxxxx = cari id port \
        \n')

elif argv1 == 'server':
    '''
    * server list
    * -c = create
    '''
    try:
        arg2 = sys.argv[2]
    except IndexError:
        arg2 = ''
    if arg2 == '':
        nv = get_nova()
        nv_slist = nv.servers.list()
        print(nv_slist)

    elif arg2 == '-c':

        print('\n-----------------\nCREATE INSTANCE\n------------------\n')

        nv = get_nova()

        # instance_name = ''
        # n = 0
        # servers = ''
        # while instance_name == '' or len(instance_name) < 5 or len(servers) > 0:
        #     instance_name = input('Nama instance (min. 5 hurup) : ')
        #     servers = nv.servers.list(search_opts={'name': instance_name})
        #     if len(servers) > 0:
        #         print('Nama instance "' + instance_name + '" sudah ada.')
        #     n += 1
        #     if n >= 5:
        #         exit('Batal bikin instance.')
        instance_name = nextName_instance()
        image = '82189ef1-2c20-475c-9d40-325eb567df56'
        flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'

        networkList()
        network = ''
        n = 0
        while len(network) != 36:
            network = input('Pilih id network : ')
            n += 1
            if n >= 5:
                exit('Batal bikin instance.')
        # if image != '' and flavor != '' and network != '':
        #     try:
        #         create_instance = nv.servers.create(name=instance_name, image=image, flavor=flavor, nics=[{'net-id': network, "v4-fixed-ip": ''}], security_groups={'default'}, createdby=get_var('OS_USERNAME'))
        #         print(create_instance)
        #     except IndexError:
        #         print('create instance "' + instance_name + '" gagal !')
        #     finally:
        #         print('Instance created : "' + instance_name + '"')
        # else:
        #     print('Periksa inputan !')

        # instance_name = nextName_instance()
        # print('\n\n' + fg.yellow + 'Bikin instance "' + instance_name + '"' + f.reset)
        # image = '82189ef1-2c20-475c-9d40-325eb567df56'
        # flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'
        # network = network_id
        if image != '' and flavor != '' and network != '':
            try:
                create_instance = nv.servers.create(name=instance_name, image=image, flavor=flavor, nics=[{'net-id': network, "v4-fixed-ip": ''}], security_groups={'4bed540c-266d-4cc2-8225-3e02ccd89ff1'}, createdby=get_var('OS_USERNAME'))
                print(create_instance)
            except IndexError:
                print('create instance gagal !')
        else:
            print('Periksa inputan !')

elif argv1 == 'createnetcomplete':
    '''
    create :
        + network
        + subnet
        + router
        + port
    '''
    ks = get_keystone()
    nt = get_neutron()
    nv = get_nova()
    UserRC_username = get_var('OS_USERNAME')
    print('\n\n\n')

    network_name = nextName_network()

    # project.aji     56a2cb6964d94577af24a7aa0269f25e    domain.aji
    # project = '56a2cb6964d94577af24a7aa0269f25e'
    project_name = get_var('OS_PROJECT_NAME')
    p = ks.projects.list(name=project_name)
    project = parsing(data=str(p), var='id')
    if len(project) != 32:
        exit('Project tidak dikenal : ' + project_id)

    if network_name != '' and project != '':
        try:
            print('\n\n' + fg.yellow + 'Bikin network "' + network_name + '"' + f.reset)
            nt.format = 'json'
            body_sample = {'network': {'name': network_name, 'admin_state_up': True, "description": "via createnetcomplete@" + __file__ + ". createdby=" + UserRC_username, "project_id": project, "tenant_id": project}}

            result_create_network = nt.create_network(body=body_sample)
            net_dict = result_create_network['network']
            network_id = net_dict['id']
            networkList(cari_id=network_id)

            time.sleep(5)
            subnet_name = nextName_subnet()
            print('\n\n' + fg.yellow + 'Bikin subnet "' + subnet_name + '"' + f.reset)

            gateway_parse3 = str(get_availableGatewayIp())
            body_create_subnet = {'subnets': [
                {
                    "name": subnet_name,
                    "description": "via createnetcomplete@" + __file__ + ". createdby=" + UserRC_username,
                    "enable_dhcp": "True",
                    "dns_nameservers": ["8.8.8.8"],
                    "allocation_pools": [{
                        "start": "192.168." + gateway_parse3 + ".2",
                        "end": "192.168." + gateway_parse3 + ".200",
                    }],
                    "gateway_ip": "192.168." + gateway_parse3 + ".254",
                    "cidr": "192.168." + gateway_parse3 + ".0/24",
                    'ip_version': 4,
                    "network_id": network_id,
                    "project_id": project,
                    "tenant_id": project,
                }
            ]}

            # body_create_subnet = {'subnets': [{'cidr': '192.168.199.0/24',
            #                       'ip_version': 4, 'network_id': network_id}]}

            nt.format = 'json'
            result_create_subnet = nt.create_subnet(body=body_create_subnet)

            subnetlist = nt.list_subnets(name=subnet_name)
            jdumps = json.dumps(subnetlist, indent=4, sort_keys=True)
            jloads = json.loads(jdumps)
            for data in jloads['subnets']:
                if re.search(subnet_name, data['name']):
                    subnet_output = data
                    break
            subnet_id = subnet_output['id']
            # print('Created subnet %s' % subnet)
            subnetList(cari_name=subnet_name)
        finally:
            print("Execution completed : network + subnet")

        try:

            time.sleep(5)
            router_name = nextName_router()
            print('\n\n' + fg.yellow + 'Bikin router "' + router_name + '"' + f.reset)
            nt.format = 'json'

            # ip_add = ''
            # print('\n\n' + fg.lightgrey + 'Cari available ip...."' + router_name + '"' + f.reset)
            # while ip_add is False or ip_add == '':
            #     ip_add = get_availableIpPublic(ipprefix='103.30.145.')
            # print('\n\n' + fg.lightgrey + 'available ip : "' + ip_add + '"' + f.reset)

            request = {
                'router':
                {
                    "name": router_name,
                    "admin_state_up": True,
                    "description": "via createnetcomplete@" + __file__ + ". createdby=" + UserRC_username,
                    "project_id": project,
                    "tenant_id": project,
                    "external_gateway_info": {
                        "enable_snat": "True",
                        "external_fixed_ips": [{
                            # "ip_address": ip_add,
                            "subnet_id": "4639e018-1cc1-49cc-89d4-4cad49bd4b89"
                        }],
                        "network_id": "d10dd06a-0425-49eb-a8ba-85abf55ac0f5"
                    }
                }
            }
            router = nt.create_router(request)
            router_id = router['router']['id']
            router = nt.show_router(router_id)
            # print(router)
            routerList(cari_name=router_name)

            time.sleep(5)
            port_name = nextName_port()
            print('\n\n' + fg.yellow + 'Bikin port "' + port_name + '"' + f.reset)
            body_value = {
                'port': {
                    'admin_state_up': True,
                    'device_owner': 'network:router_interface',
                    'device_id': router_id,
                    'name': port_name,
                    'network_id': network_id,
                    'security_groups': {'4bed540c-266d-4cc2-8225-3e02ccd89ff1'},
                    'binding:host_id': 'rocky-controller.jcamp.net',
                    'binding:profile': {},
                    'binding:vnic_type': 'normal',
                    'fixed_ips': [{
                        'subnet_id': subnet_id,
                        'ip_address': '192.168.' + gateway_parse3 + '.1'
                    }],
                }
            }

            response = nt.create_port(body=body_value)
            # portList(cari_name=port_name)
        finally:
            print("Execution completed : + router + port")
    for numin in range(0, 2):
        time.sleep(5)
        instance_name = nextName_instance()
        print('\n\n' + fg.yellow + 'Bikin instance "' + instance_name + '"' + f.reset)
        image = '82189ef1-2c20-475c-9d40-325eb567df56'
        flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'
        network = network_id
        if image != '' and flavor != '' and network != '':
            try:
                create_instance = nv.servers.create(name=instance_name, image=image, flavor=flavor, nics=[{'net-id': network, "v4-fixed-ip": ''}], security_groups={'4bed540c-266d-4cc2-8225-3e02ccd89ff1'}, createdby=get_var('OS_USERNAME'))
                print(create_instance)
            except IndexError:
                print('create instance gagal !')
        else:
            print('Periksa inputan !')

    print('\n\n\n')

elif argv1 == 'floatingip':
    '''
    * flating ip list
    * -c = create
    '''
    nt = get_neutron()
    try:
        arg2 = sys.argv[2]
    except IndexError:
        arg2 = ''
    if arg2 == '':
        floatinIPList()
    elif arg2 == '-c':
        # floatingip = {
        #     'floatingips': {
        #         'description': 'via python shell',
        #         'project_id': '56a2cb6964d94577af24a7aa0269f25e',
        #         'tenant_id': '56a2cb6964d94577af24a7aa0269f25e',
        #         'floating_network_id': 'd10dd06a-0425-49eb-a8ba-85abf55ac0f5',
        #         'port_details': {
        #             'name': 'port_details',
        #             'admin_state_up': True,
        #             'network_id': 'a15e19b0-77a7-4d5c-9132-f06c9f4742f2',
        #             'device_owner': 'compute:nova',
        #             'device_id': '16b27d36-2c04-4d14-b762-24655c9d6a97'
        #         },
        #         'fixed_ip_address': '192.168.51.2',
        #         'port_id': '5d229609-8248-415a-98c3-75129e0840fa',
        #     }
        # }

        floatingip = {
            'floatingips': {
                'description': 'via ' + __file__,
                'project_id': '56a2cb6964d94577af24a7aa0269f25e',
                'floating_network_id': 'd10dd06a-0425-49eb-a8ba-85abf55ac0f5',
            }
        }

        result_create_floatingip = nt.create_floatingip(body=floatingip)

elif argv1 == 'test':
    '''
    test only
    '''
    # get_availableIpPublic('103.30.145.')
    # floatinIPList()
    # subnetList(cari_name='aji', printout=False)
    # get_availableGatewayIp()
    # get_availableIpPublic('103.30.145.')
    # print(nextName_port())
    # print(nextName_network())
    # print(nextName_port())
    # networkList(cari_name='', cari_id='1f7d1582-afd6-41a0-bc60-e366c81ff4d8', childs=True, header=True)
    # networkList(cari_id='d68ce00e-943b-45fe-ae0c-487b667d398c')
    print(nextName_port_v1())
