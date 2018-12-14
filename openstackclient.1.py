from functions import *


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

elif argv1 == 'rolelist':
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

elif argv1 == 'rolegrant':
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

    # name = ''
    # n = 0
    # networks = ''
    # while name == '' or len(name) < 5 or len(networks['networks']) > 0:
    #     name = input('Nama network (min. 5 hurup) : ')
    #     networks = nt.list_networks(name=name)
    #     lennet = len(networks['networks'])
    #     if lennet > 0:
    #         print('Nama network "' + name + '" sudah ada.')
    #     n += 1
    #     if n >= 5:
    #         exit('Batal bikin network.')
    name = nextName_network_v1()

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

    name = name + '-' + nextName_subnet_v1()
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
        # print(jl)
        if name == jl['subnets'][0]['name']:
            print('subnet baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
            # subnetList(cari_name=name)
            subnet_baru = nt.show_subnet(subnet=jl['subnets'][0]['id'])
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

    subnet_name = nextName_subnet()
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

    ipnet_available = str(get_availableGatewayIp())

    if subnet_name != '':
        show_net = nt.show_network(network=network)
        subnets = {'subnets': [
            {
                "name": show_net['network']['name'] + '-' + subnet_name,
                "description": "via " + __file__ + ". createdby aji2",
                "enable_dhcp": "True",
                "dns_nameservers": ["8.8.8.8"],
                "allocation_pools": [{
                    "start": "192.168." + ipnet_available + ".2",
                    "end": "192.168." + ipnet_available + ".100",
                }],
                "gateway_ip": "192.168." + ipnet_available + ".1",
                "cidr": "192.168." + ipnet_available + ".0/24",
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
        # port_name = router_name + '-' + nextName_port_v1()
        # print('\n\n' + fg.yellow + 'Bikin port "' + port_name + '"' + f.reset)

        # subnet_search_network = nt.list_subnets(network_id=network_id)
        # # print(subnet_search_network)
        # subnet_id = subnet_search_network['subnets'][0]['id']
        # # print(subnet_id)
        # gateway_parse3_1 = str(subnet_search_network['subnets'][0]['cidr']).strip().split('192.168.')[1]
        # # print(gateway_parse3_1)
        # gateway_parse3 = gateway_parse3_1.strip().split('.0')[0]
        # # print(gateway_parse3)

        # body_value = {
        #     'port': {
        #         'admin_state_up': True,
        #         'device_id': router_id,
        #         'name': port_name,
        #         'network_id': network_id,
        #         # 'binding:host_id': 'rocky-controller.jcamp.net',
        #         # 'binding:profile': {},
        #         # 'binding:vnic_type': 'normal',
        #         # 'fixed_ips': [{
        #         #     'subnet_id': subnet_id,
        #         #     'ip_address': '192.168.' + gateway_parse3 + '.1'
        #         # }],
        #     }
        # }
        # print(customprint(body_value))

        # response = nt.create_port(body=body_value)
        # # print(response)
        # portList(cari_name=port_name)
        json_str = {
            'network_id': network_id,
            'router_id': router_id
        }
        portCreate(json_str)

elif argv1 == 'routercreate.v1.1':
    '''
    create router
    versi 1.1
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

elif argv1 == 'port':
    '''
    * port list
    * id:xxxxxxx = cari id port
    * -c = create
    * -c2 = create versi 2
    '''
    nt = get_neutron()
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
                exit('Batal bikin port.')

        networkList()
        network = ''
        n = 0
        while len(network) != 36:
            network = input('\nPilih id network : ')
            n += 1
            if n >= 5:
                exit('Batal bikin port.')

        # name = nextName_port_v1_1()
        # subnet_search_network = subnet_id = nt.list_subnets(network_id=network)
        # subnet = subnet_search_network['subnets'][0]['id']
        # gateway_parse3_1 = str(subnet_search_network['subnets'][0]['cidr']).strip().split('192.168.')[1]
        # gateway_parse3 = gateway_parse3_1.strip().split('.0')[0]
        # exit(gateway_parse3)
        # if name != '':
            # device_id = router_id
            # body_value = {
            #     'port': {
            #         'admin_state_up': True,
            #         'device_id': router,
            #         'name': name,
            #         'network_id': network,
            #         'binding:host_id': 'rocky-controller.jcamp.net',
            #         'binding:profile': {},
            #         'binding:vnic_type': 'normal',
            #         # 'fixed_ips': [{
            #         #     'subnet_id': subnet,
            #         #     'ip_address': '192.168.' + gateway_parse3 + '.1'
            #         # }],
            #     }
            # }
            # result = nt.create_port(body=body_value)
            # j = json.dumps(result, indent=4)
            # jl = json.loads(j)
            # if name == jl['port']['name']:
            #     print('port baru ' + f.bold + fg.green + name + f.reset + ' sudah jadi.')
            #     portList(cari_name=name)
            # else:
            #     print(f.red + 'port baru ' + f.bold + name + f.reset + f.bold + ' tidak jadi.' + f.reset)
        json_str = {
            'network_id': network_id,
            'router_id': router_id
        }
        portCreate(json_str)

    elif arg2 == '-c2':

        n = 0
        router = ''
        routerList()
        while router == '':
            router = input('\nPilih id router : ')
            n += 1
            if n >= 3:
                exit('Batal bikin port.')
        router_id = router

        networkList()
        network = ''
        n = 0
        while len(network) != 36:
            network = input('\nPilih id network : ')
            n += 1
            if n >= 5:
                exit('Batal bikin port.')

        network_id = network
        show_router = nt.show_router(router=router)
        print(customprint(show_router))
        if router_id != '' and show_router['router']['name'] != '' and network != '':
            port_name = show_router['router']['name'] + '-' + nextName_port_v1()
            print('\n\n' + fg.yellow + 'Bikin port "' + port_name + '"' + f.reset)

            try:
                body_value = {
                    'port': {
                        'admin_state_up': True,
                        'name': port_name,
                        'network_id': network_id,
                    }
                }
                create_port = nt.create_port(body=body_value)
                if port_name == create_port['port']['name']:
                    print('port baru ' + f.bold + fg.green + port_name + f.reset + ' sudah jadi.')
                    port_baru = nt.show_port(port=create_port['port']['id'])
                    print(port_baru)

                print('\n\n' + fg.yellow + 'Bikin interface "' + show_router['router']['name'] + '"' + f.reset)
                pl = {}
                pl['port_id'] = create_port['port']['id']
                attch = nt.add_interface_router(router=router_id, body=pl)
                print(customprint(attch))
            except IndexError:
                print('Gagal bikin Port')

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
    * -c --network:{nework_id} = create with network
    '''
    try:
        arg2 = sys.argv[2]
    except IndexError:
        arg2 = ''

    if arg2 == '':
        cari_name = input('Nama Server / Instance : ')
        if cari_name == '':
            cari_name = ''
            detail = False
        else:
            detail = True
        print(fg.yellow + 'Tunggu....' + f.reset)
        serverList(cari_name=cari_name, cari_project=GetUserRCProjectID(), detail=detail, header=True)
    elif arg2 == '-c':
        network = ''
        try:
            arg3 = sys.argv[3]
        except IndexError:
            arg3 = ''
        if re.search('--network:', arg3):
            try:
                network = arg3.strip().split('--network:')[1]
            except IndexError:
                network = ''

        print('\n-----------------\nCREATE INSTANCE\n------------------\n')

        nt = get_neutron()
        nv = get_nova()

        instance_name = nextName_instance_v1()
        image = '82189ef1-2c20-475c-9d40-325eb567df56'
        flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'

        if network == '':
            networkList()
            network = ''
            n = 0
            while len(network) != 36:
                network = input('Pilih id network : ')
                n += 1
                if n >= 5:
                    exit('Batal bikin instance.')

        show_network = nt.show_network(network=network)
        instance_name = show_network['network']['name'] + '-' + instance_name
        if instance_name != '' and image != '' and flavor != '' and network != '':
            try:
                json_str = {
                    'instance_name': instance_name,
                    'image': image,
                    'flavor': flavor,
                    'network': network
                }
                createServer(json_str)
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

    network_name = nextName_network_v1()

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
            subnet_name = network_name + '-' + nextName_subnet_v1()
            print('\n\n' + fg.yellow + 'Bikin subnet "' + subnet_name + '"' + f.reset)

            gateway_parse3 = str(get_availableGatewayIp())

            body_create_subnet = {
                'subnets': [{
                    'name': subnet_name,
                    'description': '',
                    'enable_dhcp': 'True',
                    'dns_nameservers': ["8.8.8.8"],
                    'allocation_pools': [{
                        'start': '192.168.' + gateway_parse3 + '.2',
                        'end': '192.168.' + gateway_parse3 + '.254'
                    }],
                    'gateway_ip': '192.168.' + gateway_parse3 + '.1',
                    'cidr': '192.168.' + gateway_parse3 + '.0/24',
                    'ip_version': 4,
                    "network_id": network_id,
                    "project_id": project,
                    "tenant_id": project,
                }]
            }

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
            subnetList(cari_name=subnet_name)
        finally:
            print("Execution completed : network + subnet")

        try:

            time.sleep(5)
            router_name = nextName_router_v1()
            print('\n\n' + fg.yellow + 'Bikin router "' + router_name + '"' + f.reset)
            nt.format = 'json'

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
                            "subnet_id": "4639e018-1cc1-49cc-89d4-4cad49bd4b89"
                        }],
                        "network_id": "d10dd06a-0425-49eb-a8ba-85abf55ac0f5"
                    }
                }
            }

            router = nt.create_router(request)
            router_id = router['router']['id']
            show_router = nt.show_router(router_id)
            # print(router)
            routerList(cari_name=router_name)
        finally:
            print("Execution completed : + router")
        try:
            time.sleep(5)
            port_name = router_name + '-' + nextName_port_v1()
            print('\n\n' + fg.yellow + 'Bikin port "' + port_name + '"' + f.reset)

            try:
                # body_value = {
                #     'port': {
                #         'admin_state_up': True,
                #         'name': port_name,
                #         'network_id': network_id,
                #     }
                # }
                # create_port = nt.create_port(body=body_value)
                # if port_name == create_port['port']['name']:
                #     print('port baru ' + f.bold + fg.green + port_name + f.reset + ' sudah jadi.')
                #     port_baru = nt.show_port(port=create_port['port']['id'])
                #     print(port_baru)

                # print('\n\n' + fg.yellow + 'Bikin interface "' + show_router['router']['name'] + '"' + f.reset)
                # pl = {}
                # pl['port_id'] = create_port['port']['id']
                # attch = nt.add_interface_router(router=router_id, body=pl)
                # print(customprint(attch))
                json_str = {
                    'network_id': network_id,
                    'router_id': router_id
                }
                portCreate(json_str)
            except IndexError:
                print('Gagal bikin Port')
        finally:
            print("Execution completed : + port")
    for numin in range(0, 2):
        time.sleep(5)
        instance_name = network_name + '-' + nextName_instance_v1()
        print('\n\n' + fg.yellow + 'Bikin instance "' + instance_name + '"' + f.reset)
        image = '82189ef1-2c20-475c-9d40-325eb567df56'
        flavor = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'
        network = network_id
        if image != '' and flavor != '' and network != '':
            try:
                json_str = {
                    'instance_name': instance_name,
                    'image': image,
                    'flavor': flavor,
                    'network': network
                }
                createServer(json_str)
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
        floatingIPList()
    elif arg2 == '-c':

        floatingip = {
            'floatingips': {
                'description': 'via ' + __file__,
                'project_id': GetUserRCProjectID(),
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
    # print(nextName_instance_v1())
    # print(nextName_port_v1())
    # print(nextName_port_v1_1())
    # print(GetUserRCProjectID())
    # portList(cari_name='', cari_id='', cari_network='', parents=False, header=True)
    serverList(cari_name='', cari_id='', cari='project_id:c0b89f614b5a457cb5acef8fe8c2b320', parents=True, header=True)
