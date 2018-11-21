import requests
import json
import os
import sys
import time


import subprocess


def get_var(varname):
    CMD = 'echo $(source adminrc; echo $%s)' % varname
    p = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    out_ = p.stdout.readlines()[0].strip()
    # out_ = out_.strip().split("b'")[1]
    # out_ = out_.strip().split("'")[0]
    return out_.decode('utf-8')


# print(get_var('OS_USERNAME'))


'''
def call_func(funcname):
    CMD = 'echo $(source adminrc; echo $(%s))' % funcname
    p = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    return p.stdout.readlines()[0].strip()


print(call_func('OS_USERNAME'))
'''


def getTOKEN():
    '''
    generate token

    '''
    OS_PROJECT_DOMAIN_NAME = get_var('OS_PROJECT_DOMAIN_NAME')
    OS_USER_DOMAIN_NAME = get_var('OS_USER_DOMAIN_NAME')
    OS_PROJECT_NAME = get_var('OS_PROJECT_NAME')
    OS_USERNAME = get_var('OS_USERNAME')
    OS_PASSWORD = get_var('OS_PASSWORD')
    OS_AUTH_URL = get_var('OS_AUTH_URL')
    # OS_IDENTITY_API_VERSION = get_var('OS_IDENTITY_API_VERSION')
    # OS_IMAGE_API_VERSION = get_var('OS_IMAGE_API_VERSION')

    headers = {
        'Content-Type': 'application/json',
    }

    OSAUTHURL = OS_AUTH_URL + 'auth/tokens/'
    # print(OSAUTHURL)
    # OS_AUTH_URL = 'http://rocky-controller.jcamp.net:5000/v3/auth/tokens/'

    data = '{ "auth": { "identity": { "methods": ["password"],"password": {"user": {"domain": {"name": "' + OS_USER_DOMAIN_NAME + '"},"name": "' + OS_USERNAME + '", "password": "' + OS_PASSWORD + '"} } }, "scope": { "project": { "domain": { "name": "' + OS_PROJECT_DOMAIN_NAME + '" }, "name": "' + OS_PROJECT_NAME + '" } } }}'

    response = requests.post(OSAUTHURL, headers=headers, data=data)
    headers_ = str(response.headers)

    # print(headers_)

    # output ----------------------------
    # {
    #     'Server': 'nginx/1.12.2',
    #     'Date': 'Fri, 26 Oct 2018 06:50:40 GMT',
    #     'Content-Type': 'application/json',
    #     'Content-Length': '3588',
    #     'Connection': 'keep-alive',
    #     'X-Subject-Token': 'gAAAAABb0rk_X03NoG6fgG2ain1aS1QeeTxQLmYq98cvperjbwQqS5BEz0kajL7yGRdkRd3WGXWmJhA1T1a_tMwwp2577m2dcNNYcUt_YYaL1RWjRI8WTFRorm55GkRIh1mbfY3pKbFFkCTsRsknb1imFS7Rk3w3TQmqzJlAcyYBg63X46N68wk',
    #     'Vary': 'X-Auth-Token',
    #     'x-openstack-request-id': 'req-53668c3b-ab2e-4402-a40f-cda6108f11f9'
    # }

    json_ = json.dumps(headers_)
    json_ = json.loads(json_)

    temp_ = json_.strip().split("'X-Subject-Token': '")[1]
    token = temp_.strip().split("',")[0]

    return token


def getSERVERS():
    '''
    server list / instance list
    '''

    # if os.environ['OS_USERNAME'] is None:
    #     os.system('source adminrc')

    getOSTOKEN = getTOKEN()
    headers = {
        'X-Auth-Token': getOSTOKEN,
    }
    # project > network > networks > subnet
    project_id = getNETWORKS__TENANT_ID()
    # 'c0b89f614b5a457cb5acef8fe8c2b320'

    response = requests.get('http://rocky-controller.jcamp.net:8774/v2.1/' + project_id + '/servers', headers=headers)

    text_ = str(response.text)

    return text_


def createSERVERS():
    '''

    create instance


    '''

    import time

    getOSTOKEN = getTOKEN()

    headers = {
        'User-Agent': 'python-novaclient',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Auth-Token': getOSTOKEN,
    }
    ts = time.time()
    image_id = '2906f1e3-b7ad-4b42-9494-d0d703bf84ab'
    project_id = getNETWORKS__TENANT_ID()
    flavor_id = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'

    '''
    server_name = 'test-from-image-' + ts
    network_uuid = 'a3a60875-f2b6-4e7c-9959-2d5529da869b'

    data = '{"server": {"name": "' + server_name + '", "imageRef": "' + image_id + '", "flavorRef": "' + flavor_id + '", "max_count": 1, "min_count": 1, "networks": [{"uuid": "' + network_uuid + '"}], "security_groups": [{"name": "default"}, {"name": "default"}]}}'
    '''

    server_name = 'autonetwork-from-image-{0}' . format(ts)
    data = '{"server": {"name": "' + server_name + '","imageRef": "' + image_id + '","flavorRef": "' + flavor_id + '","networks": "auto"}}'

    response = requests.post('http://rocky-controller.jcamp.net:8774/v2.0/' + project_id + '/servers/', headers=headers, data=data)

    text_ = str(response.text)

    return text_


def createSERVERS2():
    '''

    create instance
    https://ask.openstack.org/en/question/83166/help-in-rest-api-to-create-instance/


    '''

    getOSTOKEN = getTOKEN()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-OpenStack-Nova-API-Version': '2.11',
        'X-Auth-Token': getOSTOKEN
    }

    # APIport=NOVAport CMDpath="/v2/"+tenantid+"/servers" url="http://"+hostIP+":"+APIport+CMDpath print "URL: ",url

    ts = time.time()
    server_name = 'autonetwork-from-image-{0}' . format(ts)
    image_id = '2906f1e3-b7ad-4b42-9494-d0d703bf84ab'
    project_id = getNETWORKS__TENANT_ID()
    flavor_id = 'df0c0ef6-5ddd-4b65-bf0a-a135287df742'
    network_uuid = 'a3a60875-f2b6-4e7c-9959-2d5529da869b'

    # data = '{"server": {"name": "' + server_name + '","imageRef": "' + image_id + '","flavorRef": "' + flavor_id + '","max_count": 1,"min_count": 1,"networks": "auto"}}'
    # data = '{"server": {"name": "' + server_name + '","imageRef": "' + image_id + '","flavorRef": "' + flavor_id + '","max_count": 1, "min_count": 1}}'

    data = '{"server": {"name": "' + server_name + '","imageRef": "' + image_id + '","flavorRef": "1","max_count": 1,"min_count": 1,"networks": [{"uuid":"' + network_uuid + '"}],"security_groups": [{"name": "default"}]}}'

    project_id = getNETWORKS__TENANT_ID()

    response = requests.post('http://rocky-controller.jcamp.net:8774/v2.0/' + project_id + '/servers/', headers=headers, data=data)

    text_ = str(response.text)

    return text_


def getNETWORKS():

    # if os.environ['OS_USERNAME'] is None:
    #     os.system('source adminrc')

    getOSTOKEN = getTOKEN()
    headers = {
        'X-Auth-Token': getOSTOKEN,
    }
    response = requests.get('http://rocky-controller.jcamp.net:9696/v2.0/networks.json?limit=2', headers=headers)

    text_ = str(response.text)

    return text_


def getNETWORKS__TENANT_ID():

    text_ = getNETWORKS()
    # print(text_)
    gett_ = json.dumps(text_)
    dump_ = json.loads(gett_)
    dump_1 = dump_.strip().split('"tenant_id":"')[1]
    dump_2 = dump_1.strip().split('",')[0]
    # print(dump_2)

    return dump_2


def getTENANTS():

    import requests

    # print('OS_TOKEN:' + os.environ['OS_TOKEN'])
    getOSTOKEN = getTOKEN()
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'X-Auth-Token': getOSTOKEN,
    }

    # base on : https://ask.openstack.org/en/question/50636/which-rest-api-can-get-all-tenant-instance-information/
    project_id = getNETWORKS__TENANT_ID()
    response = requests.get('http://rocky-controller.jcamp.net:8774/v2.0/' + project_id + '/servers/detail?all_tenants=1', headers=headers)
    # 2018-10-31 : "{"forbidden": {"message": "Policy doesn't allow os_compute_api:servers:detail:get_all_tenants to be performed.", "code": 403}}"

    '''
    response = requests.get('http://rocky-controller.jcamp.net:35357/v3/users/2661ef095ffc4899a62cd8afd8b422fc/projects', headers=headers)

    # 2018-10-31
    # <html>
    # <head><title>502 Bad Gateway</title></head>
    # <body bgcolor="white">
    # <center><h1>502 Bad Gateway</h1></center>
    # <hr><center>nginx/1.12.2</center>
    # </body>
    # </html>
    '''

    text_ = str(response.text)

    return text_


def jsonBeauty(str):
    '''
    https://stackoverflow.com/questions/9105031/how-to-beautify-json-in-python#32093503
    '''

    from pygments import highlight, lexers, formatters

    formatted_json = json.dumps(json.loads(str), indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    return colorful_json


# print(sys.argv)
# print(sys.argv[0])
# print(sys.argv[1])
# print(sys.argv[2])


if sys.argv[1] == 'token':
    print('\n-----------------\nTOKEN\n------------------\n')

    getTOKEN = getTOKEN()

    print('\nSET OS_TOKEN\n----------------------------------')
    os.putenv('OS_TOKEN', getTOKEN)
    os.putenv('OS_PROJECT_DOMAIN_NAME', get_var('OS_PROJECT_DOMAIN_NAME'))
    os.putenv('OS_USER_DOMAIN_NAME', get_var('OS_USER_DOMAIN_NAME'))
    os.putenv('OS_PROJECT_NAME', get_var('OS_PROJECT_NAME'))
    os.putenv('OS_USERNAME', get_var('OS_USERNAME'))
    os.putenv('OS_PASSWORD', get_var('OS_PASSWORD'))
    os.putenv('OS_AUTH_URL', get_var('OS_AUTH_URL'))
    # OS_IDENTITY_API_VERSION = get_var('OS_IDENTITY_API_VERSION')
    # OS_IMAGE_API_VERSION = get_var('OS_IMAGE_API_VERSION')

    # print('\n>>> echo OS_TOKEN')
    # os.system('echo $OS_TOKEN')
    os.system('/bin/bash')
    # print('\n>>> echo-2 OS_TOKEN')
    # os.system('echo $OS_TOKEN')

elif sys.argv[1] == 'server':
    print('\n-----------------\nSERVER / INSTANCE\n------------------\n')
    print(jsonBeauty(getSERVERS()))
    print('\n\n')

elif sys.argv[1] == 'create_instance':
    print('\n-----------------\nCREATE INSTANCE\n------------------\n')
    # print('v2.0')
    # print(jsonBeauty(createSERVERS()))
    # print('v3')
    print(jsonBeauty(createSERVERS2()))
    print('\n\n')

elif sys.argv[1] == 'net':
    print('\n-----------------\nNETWORKS\n------------------\n')
    print(jsonBeauty(getNETWORKS()))
    # print('\n\nNETWORKS__TENANT_ID - aka project_id :')
    # print(getNETWORKS__TENANT_ID())
    print('\n\n')

elif sys.argv[1] == 'tenant':
    print('\n-----------------\nTENANT\n------------------\n')
    print(jsonBeauty(getTENANTS()))
    print('\n\n')
