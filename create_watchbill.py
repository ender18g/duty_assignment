import csv
from datetime import date
import clipboard

year = 2019


with open('inputs.csv') as f:
    reader = csv.DictReader(f)
    data_list = [r for r in reader if "," or "EDPO" in r['Duty Officer']]

date_list = [k for k in data_list[0].keys() if "/" in k and "Rank" not in k]
date_dict = {k:None for k in date_list}

print("\n\n\n\n\n\n\n\n\n\n\n")

for line in data_list:
    for k,v in line.items():
        if k in date_dict.keys():
            if v in "30,31,32".split(","):
                date_dict[k] = line.copy()

for k in date_dict.keys():
    if "N" not in k:
        month = int(k.split("/")[0])
        day = int(k.split("/")[1])
        date_obj = date(year,month,day)
        date_dict[k].update({'full_date':date_obj.strftime("%a, %b %d")})
    else:
        date_dict[k].update({'full_date':"Supernumerary"})


output = "Date;Name;Rank;Email;Dept\n"
for k,v in date_dict.items():
    output = output + f"{v['full_date']};{v['Duty Officer']};{v['Rank/Rate']};{v['Email']};{v['Dept']}\n"

print(output)
clipboard.copy(output)