#importing packages
from dataclasses import dataclass,field
import json
import csv
from datetime import datetime 
from bs4 import BeautifulSoup
import requests

#dataclass for holiday types 
@dataclass
class Calendar:
    #initial variables
    name: str
    date: datetime.date
    #getter methods
    def get_name(self):
        return self.name
    def get_date(self):
        return self.date
    def str_get_date(self):
        return str(self.date.year)+"-"+str(self.date.month)+"-"+str(self.date.day)
    #string magic method
    def __str__(self):
        s=str(self.date.year)+"-"+str(self.date.month)+"-"+str(self.date.day)
        hol=f'{self.name} ({s})'
        return hol

#decorated method
def remover(decorated_fn):
    def inner_fn(*args,**kwargs):
        fn_result=decorated_fn(*args,**kwargs)
        print(f'{fn_result} has been removed from holiday calendar')
    return inner_fn

#wikipedia website to scrape
response=requests.get('https://en.wikipedia.org/wiki/Public_holidays_in_the_United_States')

#saving tables from site into lists
soup=BeautifulSoup(response.text,'html.parser')
table_classes={'class':['wikitable sortable','wikitable']}
tables=soup.findAll('table',attrs=table_classes)

#initial list of holidays from sources
holidays=[]
holidays_other=[]

#scraping for holidays in first wikipedia table
for row in tables[0].find_all_next('tr'):
    cells=row.find_all_next('td')
    try:
        if cells[1] is not None and cells[2] is not None:
            single={}
            single['Date']=cells[1].find('span').text
            single['Name']=cells[2].find('a').text
            holidays.append(single)
    except:
        pass

#scraping for holidays in second wikipedia table
for row in tables[1].find_all_next('tr'):
    cells=row.find_all_next('td')
    try:
        if cells[0] is not None and cells[1] is not None:
            single={}
            single['Date']=cells[0].text
            single['Name']=cells[1].find('a').text
            holidays_other.append(single)
    except:
        pass

#cleaning first wikipedia table
for h in holidays:
    empty={}
    if h==empty:
        holidays.remove({})
holidays=holidays[:10]
holidays.remove({'Date': 'November 22', 'Name': 'Thanksgiving'})
holidays.remove({'Date': 'December 25', 'Name': 'Christmas'})
holidays.remove({'Date': 'May 8', 'Name': "Mother's Day"})
holidays.remove({'Date': 'June 15', 'Name': "Father's Day"})


#cleaning second wikipedia table
other=filter(lambda x: x['Date'].find('\n')==-1 and x['Date']!='Outline'and x['Date'].find('floating')==-1 and x['Date'].find('depends')==-1 and x['Date'].find('-')==-1 and x['Date'].find('DC')==-1 and x['Name']!='Kwanzaa' and x['Name']!='Rosa Parks Day' and x['Name']!='Black History Month' and x['Date']!='October',holidays_other)
other=list(other)
other[15]['Date']='April 22' 

#combining information from two tables
for i in other:
    if i not in holidays:
        holidays.append(i)

#change format of dates and converting dates to datetime
for h in holidays:
    year21=str(h['Date'])+' '+'2021'
    d21=datetime.strptime(year21,"%B %d %Y")
    h['Date']=d21.date()
#adding dates for an additional year (2022)
for h in holidays[0:54]:
    year22=str(h['Date'])
    new=year22.replace('2021','2022')
    d22=datetime.strptime(new,"%Y-%m-%d")
    holidays.append({'Date':d22.date(),'Name':h['Name']})

#retrieving data from json
file=open('holidays.json')
extra=json.load(file)
for e in extra['holidays']:
    edate=datetime.strptime(e['date'],"%Y-%m-%d")
    edate2=datetime.strptime(e['date'].replace('2021','2022'),"%Y-%m-%d")
    holidays.append({'Date':edate.date(),'Name':e['name']})
    holidays.append({'Date':edate2.date(),'Name':e['name']})

#creating list of Calendar Objects
holiday_collection=[]
for i in holidays:
    holiday_collection.append(Calendar(i['Name'],i['Date']))

#method for option 1-Add a Holiday
def option_one():
    #asks for a holiday name
    name=input('Please enter a holiday name: ')
    hdate=input(f'Please enter the date for {name} in the following format (YYYY-MM-DD)')
    hdate_boo=True
    #checks if date is in the valid format
    while hdate_boo:
        try:
            hdate=datetime.strptime(hdate,"%Y-%m-%d")
            hdate_boo=False
        except:
            hdate=input('Please try again with the correct format: ')
    #adds to master list
    holiday_collection.append(Calendar(name,hdate.date()))
    print(f'{holiday_collection[-1]} has been added.')

#method for option 2-Remove a Holiday
@remover
def option_two():
    #asks for a holiday name
    names=list(map(lambda x: x.get_name(),holiday_collection))
    h_name=input('Please enter the name of the holiday you would like to delete: ')
    #checks if holiday is valid
    ind=-1
    h_boo=True
    while h_boo:            
        try:
            ind=names.index(h_name)
            h_boo=False
        except:
            h_name=input('Holiday name not found. Please try again. ')
    #returns name to decorator to display message and item is removed
    name=holiday_collection[ind]
    holiday_collection.pop(ind)
    return name

#Save Holiday Lists: in JSON and CSV
def option_three():
    #asking user for confirmation
    ans=input('Are you sure you want to save? y or n: ').lower()
    while ans!='y' and ans!='n':
        ans=input('Please enter y or n: ').lower()
    if ans=='n':
        print('Holiday List Calendar Save Canceled')
    if ans=='y':
        #asking user for type of file
        file_type=input('Enter option number for how you would like the file saved: 1.JSON, 2.CSV: ')
        while file_type!='1' and file_type!='2':
            file_type=input('Please enter 1 or 2: ')
        #if 1 write to JSON file
        if file_type=='1':
            holiday_dict={}
            for h in holiday_collection:
                holiday_dict[h['Date']]=h['Name']
            with open('holiday_calendar.json','w') as outfile:
                json.dump(holiday_dict,outfile)
            outfile.close()
            print('Your changes have been saved.')
        #if 2 write to CSV file
        if file_type=='2':
            holiday_list=list()
            for h in holiday_collection:
                holiday_list.append(str(h))
            with open('holiday_calendar.csv','w') as outfile:
                write=csv.writer(outfile)
                write.writerow(['Holidays'])
                write.writerows([holiday_list])
            outfile.close()
            print('Your changes have been saved.')

#View Holiday Lists
def option_four():
    #ask user for year
    hyear=input('Which year would you like to search for?')
    hyear_boo=True
    while hyear_boo:
        try:
            hyear=datetime.strptime(hyear,"%Y")
            hyear_boo=False
        except:
            hyear=input('Please input a year: ')
    hyear_list_len=len(list(filter(lambda x: x.get_date().year==hyear.year,holiday_collection)))
    while hyear_list_len==0:
        hyear=input('No Holidays in that Year. Please enter another year. ')
        hhyear_boo=True
        while hhyear_boo:
            try:
                hyear=datetime.strptime(hyear,"%Y")
                hhyear_boo=False
            except:
                hyear=input('Please input a year: ')
        hyear_list_len=len(list(filter(lambda x: x.get_date().year==hyear.year,holiday_collection)))
    #filter holiday collection to show holidays in that year
    hyear_list=list(filter(lambda x: x.get_date().year==hyear.year,holiday_collection))
    #ask user for what week or blank for current week
    hweek=input('Which week would you like to search in?(1-52 or leave blank for current week): ')
    hweek_boo=True
    if hweek=='':
        hweek_boo=False
    while hweek_boo:
        try:
            hweek=int(hweek)
            hweek_boo=False
        except:
            hweek=input('Please enter a number: ')
            if hweek=='':
                hweek_boo=False
    if hweek=="":
        pass
    else:
        while hweek<1 or hweek>52:
            hweek=input('Please enter a number between 1-52: ')
            hhweek_boo=True
            while hhweek_boo:
                try:
                    hweek=int(hweek)
                    hhweek_boo=False
                except:
                    hweek=input('Please enter a number: ')
                    if hweek=='':
                        hhweek_boo=False
    #if current week get next 10 days plus current day
    if hweek=='':
        w_list=[]
        for i in range(0,11):
            ndate=datetime.today()+timedelta(days=i)
            w_list.append(datetime.strptime(str(ndate.date()),"%Y-%m-%d").date())
        week_list=list(filter(lambda x: x.get_date() in w_list,holiday_collection))
        ans=input('Would you like to see the weather for in Milwaukee on those holidays? (y or n) ')
        #ask user if they want to see weather
        while ans!='y' and ans!='n':
            ans=input('Please enter y or n: ')
        #if no print out holidays without weather
        if ans=='n':
            for w in week_list:
                print(w)
        #if yes retrive weather for milwaukee for those days
        if ans=='y':
            for w in week_list:
                wdate=w.str_get_date()
                api_url=f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Milwaukee/{wdate}?unitGroup=us&key=Y9HLRVMQCHNG52XCQG7L28F26'
                response=requests.get(api_url)
                wdict=response.json()
                weather=str(w)+" "+wdict['days'][0]['conditions']
                print(weather)
    #print out list of holidays for filtered week and year
    else:
        week_list=list(filter(lambda x: int(x.get_date().strftime("%V"))==(hweek),hyear_list))
        for w in week_list:
            print(w)

#Search for Holidays by Date
def option_five():
    hdate=input(f'Please enter the date you would like to search for in the following format (YYYY-MM-DD)')
    hdate_boo=True
    #checks if date is in the valid format
    while hdate_boo:
        try:
            hdate=datetime.strptime(hdate,"%Y-%m-%d")
            hdate_boo=False
        except:
            hdate=input('Please try again with the correct format: ')
    #filters out list for that date
    flist=list(filter(lambda x:x.get_date()==hdate.date(),holiday_collection))
    for f in flist:
        print(f)

#Exit
def option_six():
    #checks if user wants to exit and informs data will be deleted
    print('Are you sure you want to exit? All data will be deleted.')
    quit=str(input('Please enter y or n: '))
    #checks if input is yes or no
    while quit!='y' and quit!='n':
        quit=input('Please enter y or n: ')
    #deletes calendar if yes and returns False to exit Holiday Manager
    if quit=='y':
        holiday_collection=list()
        print('Holidays in Calendar have been deleted')
        return False
    #returns True to stay in Holiday Manager
    else: 
        return True

print('Welcome to Holiday Manager')
#code that interacts with user
menu=True
#goes tournament tracker until user wants to exit (menu is False)
while menu==True:
    #prints menu options
    print(f'There are {len(holiday_collection)} holidays stored in the system.')
    print("Menu Options","\n1. Add a Holiday","\n2. Remove a Holiday","\n3. Save Holiday List",
          "\n4. View Holidays","\n5. Search for Holidays By Date","\n6. Exit")
    #gets option input from user
    option=input('What would you like to do? Please enter a number: ')
    opt_boo=True
    #checks if option input is a number
    while opt_boo:
        try:
            option=int(option)
            opt_boo=False
        except:
            option=input('Please enter a number: ')
    #checks if option is in range
    while option<1 or option>6:
        option=input('Invalid option. Please try again: ')
        op_boo=True
        #checks if option is a number
        while op_boo:
            try:
                option=int(option)
                op_boo=False
            except:
                option=input('Please enter a number: ')
    #calls corresponding method based on option selected; if user wants to exit menu will stop displaying 
    if option==1:
        option_one()
    if option==2:
        option_two()
    if option==3:
        option_three()
    if option==4:
        option_four()
    if option==5:
        option_five()
    if option==6:
        menu=option_six()

else:
    print('Thanks for using Holiday Manager!')