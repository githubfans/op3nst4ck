from keystoneauth1 import session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client as ks3client

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
        ul_ = ul_.replace('>, <', '>\n\n<')
        ul_ = ul_.replace('}, {', '}\n\n{')
        ul_ = ul_.replace(', ', '\n\t')
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
    print('DOMAIN'.ljust(15, ' '), 'ID'.ljust(35, ' '))
    dl = ks.domains.list()
    for dom in dl:
        json_str = json.dumps(dom.to_dict())
        resp = json.loads(json_str)
        print(f.bold + fg.green + resp['name'].ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '))
    print('=====================\n')


def userList(name=''):
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List User' + f.reset)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    UserRC_domain_id = get_var('OS_PROJECT_DOMAIN_NAME')
    UserRC_username = get_var('OS_USERNAME')
    print('USERNAME'.ljust(15, ' '), 'ID'.ljust(35, ' '), 'DOMAIN'.ljust(15, ' '), 'PROJECT'.ljust(15, ' '))
    if is_admin(UserRC_username):
        if name != '':
            getuserlist = ks.users.list(name=name)
        else:
            getuserlist = ks.users.list()
    else:
        if name != '':
            getuserlist = ks.users.list(name=name, domain=UserRC_domain_id)
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
        print(f.bold + fg.green + resp['name'].ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), getdomain.ljust(15, ' '), getproject.ljust(15, ' '))
    print('=====================\n')


def projectList(domain=''):
    print(f.bold + fg.blue + '=====================' + f.reset)
    print(f.bold + fg.blue + 'List Project' + f.reset)
    print(f.bold + fg.blue + '---------------------' + f.reset)
    print('PROJECT'.ljust(15, ' '), 'ID'.ljust(35, ' '), 'DOMAIN'.ljust(35, ' '))
    UserRC_username = get_var('OS_USERNAME')
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
        if resp['domain_id'] is not None:
            getdomain = parsing(data=str(ks.domains.get(domain=resp['domain_id'])), var='name')
        else:
            getdomain = ''
        print(f.bold + fg.green + resp['name'].ljust(15, ' ') + f.reset, resp['id'].ljust(35, ' '), getdomain.ljust(15, ' '))
    print('=====================\n')


def roleList():
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
    print('\n$ ks {condition}')
    thisfile = open(__file__, "r")
    tfc = thisfile.read()
    argv = tfc.strip().split('# start argv ---')[2]
    prints = str(argv).strip().split('if argv1 == \'')
    # print(prints)
    print('\nConditions :')
    for argv_1 in prints:
        condition = argv_1.strip().split("':")[0]
        print(condition)
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
        rcname = input('Nama file rc : ')

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

    desc = 'dibikin pake api3.py'

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
    name = input('Cari Nama user : ')
    print('Tunggu...')
    # if name is None or name == '':
    #     ul = ks.users.list(domain=UserRC_domain_id)
    # else:
    #     ul = ks.users.list(name=name, domain=UserRC_domain_id)
    # print(toJSON(ul))
    # print('Jum. data : {0}' . format(len(ul)))
    userList(name=name)

elif argv1 == 'ucreate':
    '''
    create user
    '''
    print('\n-----------------\nCREATE USER\n------------------\n')

    ks = get_keystone()
    name = ''
    cek = ''
    desc = 'dibikin pake api3.py'
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
    desc = 'dibikin pake api3.py'
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
    desc = 'dibikin pake api3.py'

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
    desc = 'dibikin pake api3.py'

    projectList(domain=UserRC_domain_id)
    project = input('Pilih id project : ')
    if project == '':
        exit('Batal update project.')

    pget = ks.projects.get(project=project)
    strpl = str(pget)
    dom_id = parsing(strpl, 'domain_id')
    pro_name = parsing(strpl, 'name')

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

    if dom_id == UserRC_domain_id:
        pd = ks.projects.update(project=project, name=new_name)
        # print(str(pd))
        pro_name = parsing(str(pd), 'name')
        if pro_name == new_name:
            print('Project "' + pro_name + '" sudah diupdate')
        else:
            print('Project "' + pro_name + '" tidak terupdate')
    else:
        print('Project "' + pro_name + '" bukan domain anda')

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
