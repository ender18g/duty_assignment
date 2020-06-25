import csv
from datetime import date, timedelta
import clipboard
import random
from time import time
import argparse
from math import floor
from tabulate import tabulate
import copy
from sheets import pull_sheet
import re

def make_cal_link(output_list):
    #http://www.google.com/calendar/event?action=TEMPLATE&dates=20200325T20200326&text=E%26W%20Duty&location=&details=Take%20from%20Mike%20Byrge%0A%0AGive%20to%20Blake%20Smith
    one_day = timedelta(days=1)
    for i in range(len(output_list)):
        if output_list[i].get('full_date')=='Supernumerary':
            continue
        start_day=output_list[i].get('date').strftime("%Y%m%d")
        end_day= (output_list[i].get('date')+one_day).strftime("%Y%m%d")
        if i== 0:
            prior_email='unknown'
        else:
            prior_email=output_list[i-1].get("Email")
        if i==len(output_list)-1:
            next_email = 'unknown'
        else:
            next_email=output_list[i+1].get("Email")
        link = (
            f"https://calendar.google.com/calendar/r/eventedit?"
            f"dates={start_day}/{end_day}&text=E%26W+Duty&location&"
            f"details=Take+from+{prior_email}%0A%0AGive+to+{next_email}"
            f"&sf=true"
        )
        link = f'=HYPERLINK("{link}","Calendar - {output_list[i].get("Duty Officer")}")'
        output_list[i].update({'link':link})
    return output_list


def make_points(best_dict,personnel_bids):
    name_points = [];
    for n in personnel_bids:
        temp_list = [n['Duty Officer'],0]
        for v in best_dict.values():
            if v['Duty Officer']== temp_list[0]:
                temp_list[1]+=1
        name_points.append(temp_list)
    print('\n\n POINTS \n\n')
    #print(tabulate(name_points,headers=['Name','Points']))
    for n in name_points:
        print(f"{n[0]}:{n[1]}")


    
    



def make_int(s):
    if type(s)==str:
        s.strip()
    return int(s) if s else 0

def make_watchbill(best_dict,supernumerary,best_leftover,max_score,iter_num,start_time):
    year = (date.today()+timedelta(days=30)).year
    output_list=[]
    for k,v in best_dict.items():
        m = re.search(r'(\d+)/(\d+)\s',k)
        month,day = [int(m.group(1)),int(m.group(2))]
        date_obj = date(year,month,day)
        best_dict[k].update({'date':date_obj})
        best_dict[k].update({'full_date':date_obj.strftime("%a, %b %d")})
    
    for s in range(len(supernumerary)):
        supernumerary[s].update({'full_date':"Supernumerary " + str(s+1),'bid':'Y','date':date(2050,12,s+1)})
        best_dict.update({'super'+str(s):supernumerary[s]})

    ## Output list is a list of dicts
    ## the dicts include full_date Duty Officer Rank|Rate Email Dept assigned bid link

    output_list = [v for v in best_dict.values()]
    output_list.sort(key=lambda x: x.get('date',0))

    output_list = make_cal_link(output_list)



    clip_output = "Date\tName\tRank\tEmail\tDept\t\tAssignments\tBid\tCalendar\n"
    print_output = "Date\tName\tRank\tEmail\tDept\t\tAssignments\tBid\n"
    for v in output_list:
        clip_output = clip_output + f"\'{v['full_date']}\t\'{v['Duty Officer']}\t{v['Rank|Rate']}\t{v['Email']}\t{v['Dept']}\t\t{v['assigned']}\t{v['bid']}\t{v['link']}\n"
        print_output = print_output + f"\'{v['full_date']}\t\'{v['Duty Officer']}\t{v['Rank|Rate']}\t{v['Email']}\t{v['Dept']}\t\t{v['assigned']}\t{v['bid']}\n"
    for line in best_leftover:
        clip_output += "\t\t\t\t\t\t\t" + line.get('Duty Officer','-') + "\n"
        print_output += "\t\t\t\t\t\t\t" + line.get('Duty Officer','-') + "\n"
    # print(output)
    # print('\n')
    print('\n\n')
    print(tabulate([my_row.split('\t') for my_row in print_output.splitlines()],headers='firstrow',
    tablefmt='github'))
    print(f"Max Score: {max_score} iterations: {iter_num} time: {floor(time()-start_time)} sec")
    clipboard.copy(clip_output)


