# def getConfig():
#
#     '''Gets all database parameters from file and returns them in dictionary format'''
#
#     f=open('config.config','r').read().split('\n')
#     d={}
#     d['database']=f[1]
#     d['user']=f[0]
#     d['host']=f[2]
#     d['port']=int(f[3])
#     d['passw']=f[4]
#
#     return d
#
# HTL
# dbbikes
# dbbikes.cfhvz7o7yt2w.us-east-1.rds.amazonaws.com
# 3306
# HTL123456

import json
config={}
config['URI']='dbbikes.cfhvz7o7yt2w.us-east-1.rds.amazonaws.com'
config['PORT']='3306'
config['DB']='dbbikes'
config['USER']='HTL'
config['PASSWORD']='HTL123456'

with open('config.config', 'w') as f:
    json.dump(config, f)
