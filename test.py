import csv
from datetime import date, timedelta
import clipboard
import random
from time import time
import argparse
from itertools import permutations
from math import factorial, floor

parser = argparse.ArgumentParser(description='takes input.csv file and turns it into an optimized watchbill')
parser.add_argument(
    '--iterations',
    default=15,
    help='provide an integer that will be the exponent of 2 (default: 13)'
)
args = parser.parse_args()


def make_int(s):
    s.strip()
    return int(s) if s else 0

def make_watchbill():
    for k in best_dict.keys():
            month = int(k.split("/")[0])
            day = int(k.split("/")[1])
            date_obj = date(year,month,day)
            best_dict[k].update({'full_date':date_obj.strftime("%a, %b %d")})

    supernumerary.update({'full_date':"Supernumerary",'bid':'Y'})
    best_dict.update({'super':supernumerary})


    output = "Date;Name;Rank;Email;Dept;;;Bid\n"
    for k,v in best_dict.items():
        output = output + f"{v['full_date']};{v['Duty Officer']};{v['Rank|Rate']};{v['Email']};{v['Dept']};;;{v['bid']}\n"
    print(output)
    print('\n')
    for line in best_leftover:
        output += ";;;;;;;" + line.get('Duty Officer','-') + "\n"
    print('\n')
    print(f"Max Score: {max_score} iterations: {iter_num} time: {time()-start_time} sec")
    clipboard.copy(output)



start_time = time()

year = (date.today()+timedelta(days=30)).year
iterations = 2**int(args.iterations)


with open('inputs.csv') as f:
    reader = csv.DictReader(f)
    personnel_bids = [r for r in reader if "," in r['Duty Officer']]

for line in personnel_bids:
    if line.get('Supernumerary (Y|N)')=='30':
        supernumerary=line

#Filter and make a list of all of the dates
date_list = [k for k in personnel_bids[0].keys() if "/" in k]
#create a dictionary of dates
date_dict = {k:None for k in date_list}

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
random.shuffle(personnel_bids)
total_perms = factorial(len(personnel_bids))
one_percent = floor(total_perms/100)
completion = 0
current_pos = 0

#for i in range(iterations):
for temp_pers in permutations(personnel_bids,len(personnel_bids)):
    current_pos +=1
    if current_pos%100000==0:
      print(f"************    {current_pos}%")
    temp_score = 0
    temp_bill = {}
    temp_personnel = list(temp_pers)
    #shuffle the list
    #random.shuffle(temp_personnel)
    #print(temp_personnel[0]['Duty Officer'])
    for day in date_dict.keys():
        for n in range(len(temp_personnel)):
            if temp_personnel[n].get(day,1)!=1:
                temp_bill[day]=temp_personnel[n].copy()
                bid_value = temp_personnel[n].get(day)
                temp_score=temp_score + bid_value
                #temp_personnel[n]['assigned']+=1
                temp_personnel.remove(temp_personnel[n])
                temp_bill[day]['bid']=bid_value
                break

    if temp_score>max_score:
        if None in best_dict or len(temp_bill)!=len(date_dict):
            pass
        else:
            #print(f"new MAX!!  {temp_score}")
            max_score=temp_score
            best_dict=temp_bill.copy()
            best_leftover = temp_personnel.copy()
            iter_num = current_pos
            make_watchbill()
