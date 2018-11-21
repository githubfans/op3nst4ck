from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client


def get_var(varname):

    '''
    MENGAMBIL VARENV DARI LUARM PYTHON

    '''

    import subprocess
    CMD = 'echo $(source ocrc; echo $%s)' % varname
    p = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    out_ = p.stdout.readlines()[0].strip()
    return out_.decode('utf-8')


def get_auth():
    # OS_PROJECT_DOMAIN_NAME = get_var('OS_PROJECT_DOMAIN_NAME')
    # OS_USER_DOMAIN_NAME = get_var('OS_USER_DOMAIN_NAME')
    OS_PROJECT_NAME = get_var('OS_PROJECT_NAME')
    print(OS_PROJECT_NAME)
    OS_USERNAME = get_var('OS_USERNAME')
    print(OS_USERNAME)
    OS_PASSWORD = get_var('OS_PASSWORD')
    print(OS_PASSWORD)
    OS_AUTH_URL = get_var('OS_AUTH_URL')
    print(OS_AUTH_URL)

    # print(OS_AUTH_URL)

    auth = v3.Password(auth_url=OS_AUTH_URL, username=OS_USERNAME, password=OS_PASSWORD, project_name=OS_PROJECT_NAME)

    if auth is True:
        print('AUTH OK...')
    else:
        print('AUTH tdk True...')

    return auth


sess = session.Session(auth=get_auth())
print(sess)
keystone = client.Client(session=sess)
print(keystone)
token = str(keystone.auth_ref)
print('keystone.auth_ref = ' + token)
keystone_list = keystone.projects.list()
print(keystone_list)
project = keystone.projects.create(name="test", description="My new Project!", domain="default", enabled=True)
project.delete()


# keystone_list = keystone.domains.list()
# print(keystone_list)
# project = keystone.domains.create(name="test", description="My new Domain!", domain="default", enabled=True)
# project.delete()
