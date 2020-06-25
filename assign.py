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
from assign_functions import make_cal_link, make_int, make_points, make_watchbill

parser = argparse.ArgumentParser(description='takes input.csv file and turns it into an optimized watchbill')
parser.add_argument(
    '--time',
    default=1,
    help='time argument will define length of run in minutes --time=2'
)
args = parser.parse_args()


##Start of main program


start_time = time()

year = (date.today()+timedelta(days=30)).year
runtime_length = 60 * int(args.time)
supernumerary = []

# with open('inputs.csv') as f:
#     reader = csv.DictReader(f)
#     personnel_bids = [r for r in reader if "," in r['Duty Officer']]
#     #Personnel_bids is the CSV - It's a list of dicts {name,2/1,2/2,supernumerary}

ss_id = '1DIQeQAnnn6cUuRCi2i1XvBbAeJwdbsN4Ba2cbV1Gkgw'
tab_range = 'Inputs!A:AS'

sheets_array = pull_sheet(ss_id,tab_range)
personnel_bids=[]
sheets_columns = sheets_array[0]
for line in sheets_array:
    if line and "," in line[0]:
        personnel_bids.append(dict(zip(sheets_columns,line)))

for line in personnel_bids:
    if line.get('Supernumerary (Y|N)')=='30':
        supernumerary.append(line)

#Filter and make a list of all of the dates
date_list = [k for k in personnel_bids[0].keys() if "/" in k]
#create a dictionary of dates
#date_dict = {k:None for k in date_list}

print(date_list)

print("\n\n\n\n\n\n")
for i in personnel_bids:
    i['assigned']=make_int(i.get('Assigned',0))
    for k,v in i.items():
        if "/" in k:
            i[k]=make_int(i.get(k,0))



###################### try to optimize the duty scheduling ###############

max_score = 0
best_dict = {}
max_assignments=1
i=0
calendar_length = len(date_list)

TAD_bonus = 3;


while True:
    ### Turn off and break the loop if the runtime has been reached
    if time()-start_time>=runtime_length:
        print("---------DONE-----------")
        break
    i+=1  #counts the number of iterations
    temp_score = 0
    #starting a new try - clear out all of our temp bills
    temp_bill = {}
    temp_personnel = []
    temp_personnel = copy.deepcopy(personnel_bids)
    temp_personnel[:] = [d for d in temp_personnel if d.get('Qualified').lower()=='yes' or d.get('Qualified').lower()=='eom']
    # Remove people if not qualified:
 
    #shuffle the list
    random.shuffle(date_list)
    random.shuffle(temp_personnel)
    # print('##########################')
    # for p in temp_personnel:
    #  print(p['Duty Officer'] +"\t"+ str(p['assigned']))
    #print(temp_personnel[0]['Duty Officer'])
    for num,day in enumerate(date_list):
        #if you can't possibly make a BETTER score than already exists, STOP
        if (calendar_length-num)*2+temp_score<=max_score:
            break
        #Sort personnel by the bid value for that day 2 to 0
        temp_personnel.sort(key=lambda x: x.get(day,0)+ int(x.get('TAD',0))*TAD_bonus,reverse=True)
        #sort personnel by number of assignments from 0 to 2
        temp_personnel.sort(key=lambda x: x['assigned'],reverse=False)
        #iterate through all personnel
        for n in range(len(temp_personnel)):
            #if this person hasn't reached the max number of assignments
            if temp_personnel[n]['assigned']<max_assignments:
                #if this person did not give this day a 1 (do not assign)
                if temp_personnel[n].get(day,0)!=1:

                    bid_value = temp_personnel[n].get(day)
                    #add their bid value to our overall points
                    if bid_value:
                        temp_score=temp_score + bid_value
                    #mark this person as being assigned
                    temp_personnel[n]['assigned']+=1
                    #then assign this person to the day
                    temp_bill[day]=temp_personnel[n].copy()
                    #temp_personnel.remove(temp_personnel[n])
                    #remember their bid for tracking purposes
                    temp_bill[day]['bid']=bid_value
                    break #move on to the next day

    if temp_score>max_score:
        if None in temp_bill or len(temp_bill)!=len(date_list):
            pass
        else:
            #print(f"new MAX!!  {temp_score}")
            max_score=temp_score
            best_dict=temp_bill.copy()
            best_leftover = [p for p in temp_personnel if p['assigned']==0]
            iter_num = i
            make_watchbill(best_dict,supernumerary,best_leftover,max_score,iter_num,start_time)
            make_points(best_dict, personnel_bids)
