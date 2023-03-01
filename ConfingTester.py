import configparser

config = configparser.ConfigParser()
config.read('config.ini')

#Load config to variable
#version = config['API']['Version']
#authKey = config['API']['authKey']
#investor_id = config['API']['investorId']

#portfolio_id = config['Account']['portfolioId']


#print(invest_amount)

for cfg in config:
    #print(cfg)
    for sub_cfg in config[cfg]:
        value = config[cfg][sub_cfg].split()

        if value[0] == 'eq':
            print(" -", sub_cfg, "==", value[1])
        elif value[0] == 'gt': 
            print(" -", sub_cfg, ">", value[1])
        elif value[0] == 'lt':
            print(" -", sub_cfg, "<", value[1])
        elif value[0] == 'le':
            print(" -", sub_cfg, "<=", value[1])
        elif value[0] == 'ge':
            print(" -", sub_cfg, ">=", value[1])
        elif value[0] == 'ne':
            print(" -", sub_cfg, "!=", value[1])
        elif value[0] == 'nin':
            value_array = value[1].split(',')
            print(" -", sub_cfg, "is not in", value_array)
        elif value[0] == 'ne':
            value_array = value[1].split(',')
            print(" -", sub_cfg, "is in", value[1])
        
