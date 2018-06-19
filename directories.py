from datetime import datetime
from os import listdir
from os.path import isfile, join, isdir
from pprint import pprint
import os
import re
import credentials

def day_list(path):
    day_list = [path+name for name in listdir(path) if isdir(path) and name != ".DS_Store"  and name != "._.DS_Store"]
    return day_list

def month_list(path):
    day_list = [path+name for name in listdir(path) if isdir(path) and name != ".DS_Store"  and name != "._.DS_Store"]
    event_list = []
    for day in day_list:
        event_list = event_list + [day+"/"+name for name in listdir(day) if isdir(day) and name != ".DS_Store"  and name != "._.DS_Store"]
    return event_list

def year_list(path):
    event_list = []
    month_list = [path+name for name in listdir(path) if isdir(path) and name != ".DS_Store"  and name != "._.DS_Store"]
    for month in month_list:
        day_list = [month+"/"+name for name in listdir(month) if isdir(month) and name != ".DS_Store"  and name != "._.DS_Store"]
        for day in day_list:
            event_list = event_list + [day+"/"+name for name in listdir(day) if isdir(day) and name != ".DS_Store"  and name != "._.DS_Store"]
    return event_list

def generate_file_list():

    timestamp = datetime.now()
    current_day = str(timestamp.strftime('%Y/%m/%d'))

    year_2018 = year_list(credentials.year_2018)
    year_2017 = year_list(credentials.year_2017)
    final_list = year_2018 + year_2017

    title_dict = {}
    for item in final_list:
        if current_day in item:
            pass
        else:
            split_item = item.split('/')
            title = split_item[4]+"/"+split_item[5]+"/"+split_item[6]+" - "+split_item[7]
            title_dict[item] = title

    return title_dict
