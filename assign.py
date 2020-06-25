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

parser = argparse.ArgumentParser(description='takes input.csv file and turns it into an optimized watchbill')
parser.add_argument(
    '--time',
    default=1,
    help='time argument will define length of run in minutes --time=2'
)
args = parser.parse_args()


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


def make_points():
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

def make_watchbill():
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
            make_watchbill()
            make_points()
