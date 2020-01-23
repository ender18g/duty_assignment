import csv
from datetime import date, timedelta
import clipboard
import random
from time import time
import argparse
from math import floor

parser = argparse.ArgumentParser(description='takes input.csv file and turns it into an optimized watchbill')
parser.add_argument(
    '--time',
    default=1,
    help='time argument will define length of run in minutes'
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

    output = "Date;Name;Rank;Email;Dept;;;Bid\n"
    for v in output_list:
        output = output + f"{v['full_date']};{v['Duty Officer']};{v['Rank|Rate']};{v['Email']};{v['Dept']};;;{v['bid']}\n"
    print(output)
    print('\n')
    for line in best_leftover:
        output += ";;;;;;;" + line.get('Duty Officer','-') + "\n"
    print('\n')
    print(f"Max Score: {max_score} iterations: {iter_num} time: {floor(time()-start_time)} sec")
    clipboard.copy(output)



start_time = time()

year = (date.today()+timedelta(days=30)).year
runtime_length = 60 * int(args.time)


with open('inputs.csv') as f:
    reader = csv.DictReader(f)
    personnel_bids = [r for r in reader if "," in r['Duty Officer']]

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
    if time()-start_time>=runtime_length:
        print("---------DONE-----------")
        break
    i+=1
    temp_score = 0
    temp_bill = {}
    temp_personnel = personnel_bids[:]
    #shuffle the list
    random.shuffle(date_list)
    #random.shuffle(temp_personnel)
    #print(temp_personnel[0]['Duty Officer'])
    for num,day in enumerate(date_list):
        if (calendar_length-num)*2+temp_score<=max_score:
            break
        temp_personnel.sort(key=lambda x: x[day],reverse=True)
        for n in range(len(temp_personnel)):
            if temp_personnel[n].get('assigned',0)<max_assignments:
                if temp_personnel[n].get(day,1)!=1:
                    temp_bill[day]=temp_personnel[n].copy()
                    bid_value = temp_personnel[n].get(day)
                    temp_score=temp_score + bid_value
                    #temp_personnel[n]['assigned']+=1
                    temp_personnel.remove(temp_personnel[n])
                    temp_bill[day]['bid']=bid_value
                    break

    if temp_score>max_score:
        if None in temp_bill or len(temp_bill)!=len(date_list):
            pass
        else:
            #print(f"new MAX!!  {temp_score}")
            max_score=temp_score
            best_dict=temp_bill.copy()
            best_leftover = temp_personnel.copy()
            iter_num = i
            make_watchbill()
