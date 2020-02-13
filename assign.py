import csv
from datetime import date, timedelta
import clipboard
import random
from time import time
import argparse
from math import floor
from tabulate import tabulate
import copy

parser = argparse.ArgumentParser(description='takes input.csv file and turns it into an optimized watchbill')
parser.add_argument(
    '--time',
    default=1,
    help='time argument will define length of run in minutes --time=2'
)
args = parser.parse_args()


def make_int(s):
    s.strip()
    return int(s) if s else 0

def make_watchbill():
    output_list=[]
    for k,v in best_dict.items():
        month = int(k.split("/")[0])
        day = int(k.split("/")[1])
        date_obj = date(year,month,day)
        best_dict[k].update({'date':date_obj})
        best_dict[k].update({'full_date':date_obj.strftime("%a, %b %d")})

    supernumerary.update({'full_date':"Supernumerary",'bid':'Y','date':date(2050,12,1)})
    best_dict.update({'super':supernumerary})

    output_list = [v for v in best_dict.values()]
    output_list.sort(key=lambda x: x.get('date',0))

    output = "Date\tName\tRank\tEmail\tDept\t\tAssignments\tBid\n"
    for v in output_list:
        output = output + f"\'{v['full_date']}\'\t\'{v['Duty Officer']}\'\t{v['Rank|Rate']}\t{v['Email']}\t{v['Dept']}\t\t{v['assigned']}\t{v['bid']}\n"
    for line in best_leftover:
        output += "\t\t\t\t\t\t\t" + line.get('Duty Officer','-') + "\n"
    # print(output)
    # print('\n')
    print('\n\n')
    print(tabulate([my_row.split('\t') for my_row in output.splitlines()],headers='firstrow',
    tablefmt='github'))
    print(f"Max Score: {max_score} iterations: {iter_num} time: {floor(time()-start_time)} sec")
    clipboard.copy(output)



start_time = time()

year = (date.today()+timedelta(days=30)).year
runtime_length = 60 * int(args.time)


with open('inputs.csv') as f:
    reader = csv.DictReader(f)
    personnel_bids = [r for r in reader if "," in r['Duty Officer']]
    #Personnel_bids is the CSV - It's a list of dicts {name,2/1,2/2,supernumerary}

for line in personnel_bids:
    if line.get('Supernumerary (Y|N)')=='30':
        supernumerary=line

#Filter and make a list of all of the dates
date_list = [k for k in personnel_bids[0].keys() if "/" in k]
#create a dictionary of dates
#date_dict = {k:None for k in date_list}

print("\n\n\n\n\n\n")
for i in personnel_bids:
    i['assigned']=make_int(i.get('assigned',0))
    for k,v in i.items():
        if "/" in k:
            i[k]=make_int(i.get(k,0))
###################### try to optimize the duty scheduling ###############

max_score = 0
best_dict = {}
max_assignments=1
i=0
calendar_length = len(date_list)

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
        temp_personnel.sort(key=lambda x: x[day],reverse=True)
        #sort personnel by number of assignments from 0 to 2
        temp_personnel.sort(key=lambda x: x['assigned'],reverse=False)
        #iterate through all personnel
        for n in range(len(temp_personnel)):
            #if this person hasn't reached the max number of assignments
            if temp_personnel[n]['assigned']<max_assignments:
                #if this person did not give this day a 1 (do not assign)
                if temp_personnel[n].get(day,1)!=1:

                    bid_value = temp_personnel[n].get(day)
                    #add their bid value to our overall points
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
            make_watchbill()