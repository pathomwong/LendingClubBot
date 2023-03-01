#!/usr/bin/env python
# coding: utf-8

#New loan will be list at 2AM, 6AM, 10AM and 2PM Pacific Time.

import requests
import configparser
import os
import pandas as pd
import math
import sys
import logging
import json

abs_dir = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(abs_dir, 'config.ini'))

#Load config to variable
version = config['API']['Version']
authKey = config['API']['authKey']
investor_id = config['API']['investorId']

portfolio_id = config['Account']['portfolioId']
invest_amount = float(config['Account']['investAmount'])
if invest_amount < 25.0:
    invest_amount = 25.0

header = {'Authorization' : authKey, 'Content-Type': 'application/json'}

def checkAvailableCash():
    url = 'https://api.lendingclub.com/api/investor/'+ version+'/accounts/'+investor_id+'/availablecash'
    resp = requests.get(url, headers=header)
    resp.raise_for_status()
    return float(resp.json()['availableCash'])

def getFilterID():    
    url = 'https://api.lendingclub.com/api/investor/'+ version+'/accounts/'+investor_id+'/filters'
    resp = requests.get(url, headers=header)
    print(resp.json())

def getLoadList():
    url = 'https://api.lendingclub.com/api/investor/'+version+'/loans/listing'
    payload = {'filterId' : 159961860, 'showAll' : True}
    #payload = {'showAll': True}
    resp = requests.get(url, headers=header, params=payload)
    resp.raise_for_status()
    return resp.json()['loans']

def submitLoanOrder(loan_list): #loan_list is a list of dict [{"loanId":22222,"requestedAmount":55.0,"portfolioId":44444}]
    
    if not loan_list:
        logger.info('No loan can pass criteria')
        sys.exit(0)
        
    loan_num = math.floor(float(total_cash)/float(invest_amount))
    logger.info("Cash/Loans: " + str(loan_num))
    url = 'https://api.lendingclub.com/api/investor/'+version+'/accounts/'+investor_id+'/orders'
    payload = {'aid': investor_id, 'orders': loan_list[0:loan_num]}
    logger.info('Order: ' + str(loan_list[0:loan_num]))
    
    resp = requests.post(url, headers=header, data=json.dumps(payload))

    logger.info('Order Result:' + resp.text)
    return 0#resp.json()['orderConfirmations']

def loanFilter(loan_list,filters):
   
    if not loan_list:
        logger.info('Loan List is empty')
        sys.exit(0)
    df = pd.DataFrame(loan_list)
    logger.info('Number of Loan:' + str(len(df.index)))
    #make column name lowercase for compare
    df.columns= df.columns.str.lower()
    df.fillna(0, inplace = True)
    for sub_cfg in filters:
        value = filters[sub_cfg].split()

        #if value is number, cast it to float
        if value[1].isnumeric():
            value[1] = float(value[1])
        
        if value[0] == 'eq':
            df = df[(df[sub_cfg] == value[1])]
        elif value[0] == 'gt': 
            df = df[(df[sub_cfg] > value[1])]
        elif value[0] == 'lt':
            df = df[(df[sub_cfg] < value[1])]
        elif value[0] == 'le':
            df = df[(df[sub_cfg] <= value[1])]
        elif value[0] == 'ge':
            df = df[(df[sub_cfg] >= value[1])]
        elif value[0] == 'ne':
            df = df[(df[sub_cfg] != value[1])]
        elif value[0] == 'nin':
            value_array = value[1].split(',')
            df = df[~(df[sub_cfg].isin(value_array))]
        elif value[0] == 'in':
            value_array = value[1].split(',')
            df = df[(df[sub_cfg].isin(value_array))]

    logger.info('Number of Loan Pass Filter:' + str(len(df.index)))
    df.rename(columns={'id':'loanId'}, inplace=True)
    df['requestedAmount'] = invest_amount
    df['portfolioId'] = portfolio_id
    #print(df)
    return df.loc[:, ['loanId','requestedAmount','portfolioId']].to_dict('records') #loan_list is a list of dict [{"loanId":22222,"requestedAmount":55.0,"portfolioId":44444}]

 

#__init__ main

#logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(abs_dir, 'lcbot.log'))
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info('-------------------------------------------------------')#bot start mark in log file

#get avalable fund
total_cash = checkAvailableCash()

#check if we have enough cash
if(total_cash > invest_amount):

    #get all listed loan 
    loan_list = getLoadList()

    #filter loan that meet requirement
    filtered_loan_list = loanFilter(loan_list,config['LoanCriteria'])
    
    #order loan
    order_result = submitLoanOrder(filtered_loan_list)
    
else:
    logger.info('insufficient funds')

