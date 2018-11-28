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


def networkList(cari_name=''):

    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Network' + f.reset)
    if cari_name != '':
        cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
        print('name = ' + cari_name_)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    ks = get_keystone()
    nt = get_neutron()
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
                print('\n')
                print(data)
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))
        else:
            print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))


def subnetList(cari_name='', output_count=False):

    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Subnet' + f.reset)
    if cari_name != '':
        cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
        print('name = ' + cari_name_)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    ks = get_keystone()
    nt = get_neutron()
    subnetlist = nt.list_subnets()
    jdumps = json.dumps(subnetlist, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'PROJECT'.ljust(15, ' '), 'NET.'.ljust(17, ' '), 'GATEWAY.'.ljust(17, ' '), 'DESC.'.ljust(35, ' '))
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
                print('\n')
                print(data)
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getnet.ljust(17, ' '), data['gateway_ip'].ljust(17, ' '), data['description'].ljust(35, ' '))
        else:
            print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getnet.ljust(17, ' '), data['gateway_ip'].ljust(17, ' '), data['description'].ljust(35, ' '))


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
                print('\n')
                print(data)
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), ext_ip.ljust(15, ' '), net_name.ljust(20, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '))
        else:
            print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), ext_ip.ljust(15, ' '), net_name.ljust(20, ' '), getproject.ljust(15, ' '), data['status'].ljust(10, ' '))


def portList(cari_name=''):

    print('\n')
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Port' + f.reset)
    if cari_name != '':
        cari_name_ = fg.yellow + f.bold + '"' + cari_name + '"' + f.reset
        print('name = ' + cari_name_)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    ks = get_keystone()
    nt = get_neutron()
    portlist = nt.list_ports()
    jdumps = json.dumps(portlist, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    # print(jloads)
    print('NAME'.ljust(25, ' '), 'ID'.ljust(40, ' '), 'PROJECT'.ljust(15, ' '), 'ROUTER'.ljust(15, ' '), 'STATUS.'.ljust(10, ' '), 'DESC.'.ljust(35, ' '))
    for data in jloads['ports']:
        # print(data)
        if len(data['project_id']) == 32:
            getproject = parsing(data=str(ks.projects.get(project=data['project_id'])), var='name')
        else:
            getproject = data['project_id'] + '(?)'
        # try:
        #     getrouter = nt.list_routers()
        #     # print(getrouter)
        #     if re.search(data['device_id'], str(getrouter)):
        #         # print(data['device_id'])
        #     # exit()
        # except IndexError:
        #     getrouter = ''
        getrouter = ''
        if cari_name != '':
            if re.search(cari_name, data['name']):
                print('\n')
                print(data)
                print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), data['device_id'].ljust(10, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))
        else:
            print(f.bold + fg.green + data['name'].ljust(25, ' ') + f.reset, data['id'].ljust(40, ' '), getproject.ljust(15, ' '), getrouter.ljust(15, ' '), data['status'].ljust(10, ' '), data['description'].ljust(35, ' '))


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


def nextName_network():

    list_ = nt.list_networks()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    num = 0
    for data in jloads['networks']:
        if re.search('network', data['name']):
            if re.search('.' + get_var('OS_USERNAME'), data['name']):
                num += 1

    if num > 0:
        num = num + 1
        next_name = 'network' + str(num) + '.' + get_var('OS_USERNAME')
    else:
        next_name = 'network.' + get_var('OS_USERNAME')

    return next_name


def nextName_subnet():

    list_ = nt.list_subnets()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    num = 0
    for data in jloads['subnets']:
        if re.search('subnet', data['name']):
            if re.search('.' + get_var('OS_USERNAME'), data['name']):
                num += 1

    if num > 0:
        num = num + 1
        next_name = 'subnet' + str(num) + '.' + get_var('OS_USERNAME')
    else:
        next_name = 'subnet.' + get_var('OS_USERNAME')

    return next_name


def nextName_router():

    list_ = nt.list_routers()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    num = 0
    for data in jloads['routers']:
        if re.search('router', data['name']):
            if re.search('.' + get_var('OS_USERNAME'), data['name']):
                num += 1

    if num > 0:
        num = num + 1
        next_name = 'router' + str(num) + '.' + get_var('OS_USERNAME')
    else:
        next_name = 'router.' + get_var('OS_USERNAME')

    return next_name


def nextName_port():

    list_ = nt.list_ports()
    jdumps = json.dumps(list_, indent=4, sort_keys=True)
    jloads = json.loads(jdumps)
    num = 0
    for data in jloads['ports']:
        if re.search('port', data['name']):
            if re.search('.' + get_var('OS_USERNAME'), data['name']):
                num += 1

    if num > 0:
        num = num + 1
        next_name = 'port' + str(num) + '.' + get_var('OS_USERNAME')
    else:
        next_name = 'port.' + get_var('OS_USERNAME')

    return next_name


def nextName_instance():
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
    # print(x[1])
    x = str(x[1]).strip().split('103.30.145.')
    # print(list(x))
    ips = 171
    found = False
    for xx in list(x):
        if re.search('Host is up', xx):
            ips += 1
            ip_suffix = str(xx).strip().split(")\\nHost ")[0]
            if ips != ip_suffix:
                found = ipprefix + str(ips)
                break
    return found


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


'''
def add_ports_to_network(task, network_uuid, is_flat=False):
    """Create neutron ports to boot the ramdisk.

    Create neutron ports for each pxe_enabled port on task.node to boot
    the ramdisk.

    :param task: a TaskManager instance.
    :param network_uuid: UUID of a neutron network where ports will be
        created.
    :param is_flat: Indicates whether it is a flat network or not.
    :raises: NetworkError
    :returns: a dictionary in the form {port.uuid: neutron_port['id']}
    """
    client = get_client(task.context.auth_token)
    node = task.node

    LOG.debug('For node %(node)s, creating neutron ports on network '
              '%(network_uuid)s using %(net_iface)s network interface.',
              {'net_iface': task.driver.network.__class__.__name__,
               'node': node.uuid, 'network_uuid': network_uuid})
    body = {
        'port': {
            'network_id': network_uuid,
            'admin_state_up': True,
            'binding:vnic_type': 'baremetal',
            'device_owner': 'baremetal:none',
        }
    }

    if not is_flat:
        # NOTE(vdrok): It seems that change
        # I437290affd8eb87177d0626bf7935a165859cbdd to neutron broke the
        # possibility to always bind port. Set binding:host_id only in
        # case of non flat network.
        body['port']['binding:host_id'] = node.uuid

    # Since instance_uuid will not be available during cleaning
    # operations, we need to check that and populate them only when
    # available
    body['port']['device_id'] = node.instance_uuid or node.uuid

    ports = {}
    failures = []
    portmap = get_node_portmap(task)
    pxe_enabled_ports = [p for p in task.ports if p.pxe_enabled]
    for ironic_port in pxe_enabled_ports:
        body['port']['mac_address'] = ironic_port.address
        binding_profile = {'local_link_information':
                           [portmap[ironic_port.uuid]]}
        body['port']['binding:profile'] = binding_profile
        client_id = ironic_port.extra.get('client-id')
        if client_id:
            client_id_opt = {'opt_name': 'client-id', 'opt_value': client_id}
            extra_dhcp_opts = body['port'].get('extra_dhcp_opts', [])
            extra_dhcp_opts.append(client_id_opt)
            body['port']['extra_dhcp_opts'] = extra_dhcp_opts
        try:
            port = client.create_port(body)
        except neutron_exceptions.NeutronClientException as e:
            failures.append(ironic_port.uuid)
            LOG.warning(_LW("Could not create neutron port for node's "
                            "%(node)s port %(ir-port)s on the neutron "
                            "network %(net)s. %(exc)s"),
                        {'net': network_uuid, 'node': node.uuid,
                         'ir-port': ironic_port.uuid, 'exc': e})
        else:
            ports[ironic_port.uuid] = port['port']['id']

    if failures:
        if len(failures) == len(pxe_enabled_ports):
            rollback_ports(task, network_uuid)
            raise exception.NetworkError(_(
                "Failed to create neutron ports for any PXE enabled port "
                "on node %s.") % node.uuid)
        else:
            LOG.warning(_LW("Some errors were encountered when updating "
                            "vif_port_id for node %(node)s on "
                            "the following ports: %(ports)s."),
                        {'node': node.uuid, 'ports': failures})
    else:
        LOG.info(_LI('Successfully created ports for node %(node_uuid)s in '
                     'network %(net)s.'),
                 {'node_uuid': node.uuid, 'net': network_uuid})

    return ports
'''


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
    print('Mengganti file rc.')
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
    networkList(cari_name)

elif argv1 == 'netcreate':
    '''
    create network
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
        network = {"name": name, "admin_state_up": True, "description": "dibikin via " + __file__ + ". createdby:" + UserRC_username, "project_id": project, "tenant_id": project}
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
    nt = get_neutron()
    UserRC_username = get_var('OS_USERNAME')

    name = ''
    n = 0
    subnets = ''
    while name == '' or len(name) < 5 or len(subnets['subnets']) > 0:
        name = input('Nama subnet (min. 5 hurup) : ')
        subnets = nt.list_subnets(name=name)
        lennet = len(subnets['subnets'])
        if lennet > 0:
            print('Nama subnet "' + name + '" sudah ada.')
        n += 1
        if n >= 5:
            exit('Batal bikin subnet.')

    # networkList()
    # network = ''
    # n = 0
    # while len(network) != 36:
    #     network = input('Pilih id network : ')
    #     n += 1
    #     if n >= 5:
    #         exit('Batal bikin subnet.')

    # if is_admin(UserRC_username):
    #     projectList()
    # else:
    #     projectList(domain=UserRC_domain_id)

    # project = ''
    # n = 0
    # while len(project) != 32:
    #     project = input('Pilih id project : ')
    #     n += 1
    #     if n >= 5:
    #         exit('Batal bikin subnet.')

    if name != '':
        subnets = {'subnets': [
            {
                "name": name,
                "description": "dibikin via python shell. createdby aji2",
                "enable_dhcp": "True",
                "dns_nameservers": ["8.8.8.8"],
                "allocation_pools": [{
                    "start": "192.168.31.2",
                    "end": "192.168.31.5",
                }],
                "gateway_ip": "192.168.31.1",
                "cidr": "192.168.31.0/24",
                'ip_version': 4,
                "network_id": "71cd19e8-0b9c-423c-ac6e-63028e12acce",
                "project_id": "56a2cb6964d94577af24a7aa0269f25e",
                "tenant_id": "56a2cb6964d94577af24a7aa0269f25e",
            }
        ]}
        # print(subnet)
        result = nt.create_subnet(body=subnets)
        j = json.dumps(result, indent=4)
        jl = json.loads(j)
        if name == jl['subnet']['name']:
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
        router = {"name": name, "admin_state_up": True, "description": "dibikin via " + __file__ + ". createdby:" + UserRC_username, "project_id": project, "tenant_id": project}
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
        bodyu = {'router':
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


elif argv1 == 'portlist':
    '''
    port list
    '''
    print('\n-----------------\nPORT LIST\n------------------\n')

    try:
        cari_name = sys.argv[2]
    except IndexError:
        cari_name = input('Cari nama port (kosongkan = semua nama) : ')
    portList(cari_name)

elif argv1 == 'portcreate':
    '''
    create router
    '''
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
            exit('Batal update router.')

    networkList()
    network = ''
    n = 0
    while len(network) != 36:
        network = input('Pilih id network : ')
        n += 1
        if n >= 5:
            exit('Batal bikin subnet.')

    name = ''
    n = 0
    ports = ''
    while name == '' or len(name) < 5 or len(ports['ports']) > 0:
        name = input('Nama port (min. 5 hurup) : ')
        ports = nt.list_ports(name=name)
        lennet = len(ports['ports'])
        if lennet > 0:
            print('Nama port "' + name + '" sudah ada.')
        n += 1
        if n >= 5:
            exit('Batal bikin port.')

    if name != '':
        # device_id = router_id
        body_value = {
            'port': {
                'admin_state_up': True,
                'device_id': router,
                'name': name,
                'network_id': network,
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

elif argv1 == 'serverlist':
    '''
    server list
    '''
    nv = get_nova()
    nv_slist = nv.servers.list()
    print(nv_slist)

elif argv1 == 'servercreate':
    '''
    create server/instance
    '''
    print('\n-----------------\nCREATE INSTANCE\n------------------\n')

    nv = get_nova()

    # instance_name = ''
    # n = 0
    # while instance_name == '' or len(instance_name) < 5 or len(servers) > 0:
    #     instance_name = input('Nama instance (min. 5 hurup) : ')
    #     servers = nv.servers.list(search_opts={'name': instance_name})
    #     if len(servers) > 0:
    #         print('Nama instance "' + instance_name + '" sudah ada.')
    #     n += 1
    #     if n >= 5:
    #         exit('Batal bikin instance.')
    instance_name = nextName_instance()
    # imageList()
    # image = ''
    # n = 0
    # while len(image) != 36:
    #     image = input('Pilih id image : ')
    #     n += 1
    #     if n >= 5 or image == '':
    #         exit('Batal bikin instance.')
    image = '82189ef1-2c20-475c-9d40-325eb567df56'
    # image = nv.images.find(name='CentOS-7-x86_64-GenericCloud')

    # flavorList()
    # flavor = ''
    # n = 0
    # while len(flavor) != 8:
    #     flavor = input('Pilih flavor : ')
    #     n += 1
    #     if n >= 5 or flavor == '':
    #         exit('Batal bikin instance.')

    # flavor = nv.flavors.find(ram=1024)
    # if flavor == '':
    #     flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'
    flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'
    # flavor = nv.flavors.find(name='jc010120')

    # networkList()
    # network = ''
    # n = 0
    # while len(network) != 36:
    #     network = input('Pilih id network : ')
    #     n += 1
    #     if n >= 5:
    #         exit('Batal bikin instance.')
    # network = nv.networks.find(name='network.aji2')
    # network = nv.networks.find(id='a15e19b0-77a7-4d5c-9132-f06c9f4742f2')
    network = 'a15e19b0-77a7-4d5c-9132-f06c9f4742f2'
    print(image)
    print(flavor)
    print(network)
    if image != '' and flavor != '' and network != '':
        try:
            create_instance = nv.servers.create(name=instance_name, image=image, flavor=flavor, nics=[{'net-id': network, "v4-fixed-ip": ''}], security_groups={'default'}, createdby=get_var('OS_USERNAME'))
            # , security_groups='default'
            # novaclient.exceptions.BadRequest: Unable to find security_group with name or id 'a' (HTTP 400) (Request-ID: req-dc8384f6-b8ab-4cbc-acde-4122d573d2f4)

            # , security_groups='4bed540c-266d-4cc2-8225-3e02ccd89ff1'
            # novaclient.exceptions.BadRequest: Unable to find security_group with name or id 'c' (HTTP 400) (Request-ID: req-caf4c1cb-32d6-45f7-9ab4-ba26cb2f7c2f)

            print(create_instance)
            print(type(create_instance))

        except IndexError:
            print('create instance "' + instance_name + '" gagal !')

        finally:
            print('Instance created : "' + instance_name + '"')

    else:
        print('Periksa inputan !')

    '''

    http://apps.e5link.com/Blog/?e=95400&d=06/16/2018&s=OpenStack%20Python%20script%20to%20Create%20instance
    (venv_os) [centos@aji-instance1b ~]$ openstack image list
    +--------------------------------------+------------------------------+--------+
    | ID                                   | Name                         | Status |
    +--------------------------------------+------------------------------+--------+
    | 82189ef1-2c20-475c-9d40-325eb567df56 | CentOS-7-x86_64-GenericCloud | active |
    | 8ad611f8-5c61-46e9-9370-f8d5ba63d9bb | adhi-snap                    | active |
    | 2906f1e3-b7ad-4b42-9494-d0d703bf84ab | aji_instance1                | active |
    | c617bcfa-af77-405c-b7aa-dc3f26ed992b | cirros                       | active |
    | c34b7c90-f907-4200-9912-2541dbd8e77d | njajal-horizon-snapshot      | active |
    +--------------------------------------+------------------------------+--------+
    (venv_os) [centos@aji-instance1b ~]$ openstack flavor list
    +--------------------------------------+----------+------+------+-----------+-------+-----------+
    | ID                                   | Name     |  RAM | Disk | Ephemeral | VCPUs | Is Public |
    +--------------------------------------+----------+------+------+-----------+-------+-----------+
    | afc68ef6-1985-4d59-ac63-a6f2c4405756 | jc010220 | 2048 |   20 |         0 |     1 | True      |
    | df0c0ef6-5ddd-4b65-bf0a-a135287df742 | jc010120 | 1024 |   20 |         0 |     1 | True      |
    +--------------------------------------+----------+------+------+-----------+-------+-----------+
    '''

elif argv1 == 'createnetcomplete':
    '''
    create :
        + network
        + subnet
        + router
        + port
    '''
    nt = get_neutron()
    nv = get_nova()
    UserRC_username = get_var('OS_USERNAME')
    print('\n\n\n')

    network_name = nextName_network()

    # project.aji     56a2cb6964d94577af24a7aa0269f25e    domain.aji
    project = '56a2cb6964d94577af24a7aa0269f25e'

    if network_name != '' and project != '':
        try:
            print('\n\n' + fg.yellow + 'Bikin network "' + network_name + '"' + f.reset)
            nt.format = 'json'
            body_sample = {'network': {'name': network_name, 'admin_state_up': True, "description": "dibikin via " + __file__ + ". createdby:" + UserRC_username, "project_id": project, "tenant_id": project}}

            result_create_network = nt.create_network(body=body_sample)
            net_dict = result_create_network['network']
            network_id = net_dict['id']
            # print('Network %s created' % network_id)
            networkList(cari_name=network_name)

            subnet_name = nextName_subnet()
            print('\n\n' + fg.yellow + 'Bikin subnet "' + subnet_name + '"' + f.reset)

            body_create_subnet = {'subnets': [
                {
                    "name": subnet_name,
                    "description": "dibikin via " + __file__ + ". createdby:" + UserRC_username,
                    "enable_dhcp": "True",
                    "dns_nameservers": ["8.8.8.8"],
                    "allocation_pools": [{
                        "start": "192.168.51.2",
                        "end": "192.168.51.5",
                    }],
                    "gateway_ip": "192.168.51.1",
                    "cidr": "192.168.51.0/24",
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

            router_name = nextName_router()
            print('\n\n' + fg.yellow + 'Bikin router "' + router_name + '"' + f.reset)
            nt.format = 'json'
            ip_add = ''
            print('\n\n' + fg.lightgrey + 'Cari available ip...."' + router_name + '"' + f.reset)
            while ip_add is False or ip_add == '':
                ip_add = get_availableIpPublic(ipprefix='103.30.145.')
            print('\n\n' + fg.lightgrey + 'available ip : "' + ip_add + '"' + f.reset)
            request = {'router':
                {
                    "name": router_name,
                    "admin_state_up": True,
                    "description": "dibikin via " + __file__ + ". createdby:" + UserRC_username,
                    "project_id": project,
                    "tenant_id": project,
                    "external_gateway_info": {
                        "enable_snat": "True",
                        # "external_fixed_ips": [{
                        #     "ip_address": ip_add,
                        #     "subnet_id": "4639e018-1cc1-49cc-89d4-4cad49bd4b89"
                        # }],
                        "network_id": "d10dd06a-0425-49eb-a8ba-85abf55ac0f5"
                    }
                }
            }
            router = nt.create_router(request)
            router_id = router['router']['id']
            router = nt.show_router(router_id)
            # print(router)
            routerList(cari_name=router_name)

            port_name = nextName_port()
            print('\n\n' + fg.yellow + 'Bikin port "' + port_name + '"' + f.reset)
            body_value = {'port': {
                'admin_state_up': True,
                'device_id': router_id,
                'name': port_name,
                'network_id': network_id,
            }
            }

            response = nt.create_port(body=body_value)
            # print(response)
            portList(cari_name=port_name)
        finally:
            print("Execution completed : + router + port")

    instance_name = nextName_instance()
    print('\n\n' + fg.yellow + 'Bikin network "' + instance_name + '"' + f.reset)
    image = '82189ef1-2c20-475c-9d40-325eb567df56'
    flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'
    network = network_id
    if image != '' and flavor != '' and network != '':
        try:
            create_instance = nv.servers.create(name=instance_name, image=image, flavor=flavor, nics=[{'net-id': network, "v4-fixed-ip": ''}])
            # , security_groups='4bed540c-266d-4cc2-8225-3e02ccd89ff1'
            print(create_instance)
            print(type(create_instance))
            nv_slist = nv.servers.list()
            print(nv_slist)
        except IndexError:
            print('create instance gagal !')
    else:
        print('Periksa inputan !')

    print('\n\n\n')

elif argv1 == 'flipcreate':
    '''
    create flating ip
    '''


elif argv1 == 'test':
    get_availableIpPublic('103.30.145.') 
