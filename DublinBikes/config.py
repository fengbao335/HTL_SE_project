import json
config={}
config['URI']='dbbikes.c48xjvxqywhq.us-east-1.rds.amazonaws.com'
config['PORT']='3306'
config['DB']='dbbikes'
config['USER']='HTL'
config['PASSWORD']='HTL123456'

with open('config.config', 'w') as f:
    json.dump(config, f)
