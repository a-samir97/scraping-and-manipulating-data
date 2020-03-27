import requests, numpy, pandas, bs4, datetime
from split_data import split_text

# step 1

request = requests.get('https://www.spaceweatherlive.com/en/solar-activity/top-50-solar-flares')

bs_object = bs4.BeautifulSoup(request.text,features='lxml')

content = str(bs_object.find('table'))

data_content = pandas.read_html(content)[0]

data_content.columns  = [ 'rank', 'x_classification', 'date', 'region','start_time', 'max_time', 'end_time', 'movie']


# step 2

data_content = data_content.iloc[:, :-1]

for index, row in data_content.iterrows():
    
    date = data_content['date'][index].split('/')
    
    start_time = data_content['start_time'][index].split(':')
    max_time = data_content['max_time'][index].split(':')
    end_time = data_content['end_time'][index].split(':')

    new_start_time = datetime.time(hour=int(start_time[0]), minute=int(start_time[1]))
    new_max_time = datetime.time(hour=int(max_time[0]), minute=int(max_time[1]))
    new_end_time = datetime.time(hour=int(end_time[0]), minute=int(end_time[1]))

    new_date = datetime.date(year=int(date[0]),month=int(date[1]),day=int(date[2]))

    data_content['start_time'][index] = datetime.datetime.combine(new_date, new_start_time)
    data_content['max_time'][index] = datetime.datetime.combine(new_date, new_max_time)
    data_content['end_time'][index] = datetime.datetime.combine(new_date, new_end_time)    

del data_content['date']

# step 3 

request = requests.get('https://cdaw.gsfc.nasa.gov/CME_list/radio/waves_type2.html')

bs_object = bs4.BeautifulSoup(request.text,features='lxml')

content = str(bs_object.find('pre'))

data_split_list = content.split('\n')

content_data = []

for i in range(12,len(data_split_list)-2):
    content_data.append(split_text(data_split_list[i]))

nasa_data_frame = pandas.DataFrame(content_data)

nasa_data_frame.columns = ['start_date','start_time','end_date','end_time','start_frequency',
                            'end_frequency','flare_location','flare_region','importance',
                            'cme_date','cme_time','cpa','width','spd','plots']
                            
# print(nasa_data_frame)
# nasa_data_frame.to_csv('nasa2.csv')

# step 4
nasa_data_frame['start_frequency'] = nasa_data_frame['start_frequency'].replace(r'[?]+', "NaN", regex=True)
nasa_data_frame['end_frequency'] = nasa_data_frame['end_frequency'].replace(r'[?]+', "NaN", regex=True)
nasa_data_frame['flare_location'] = nasa_data_frame['flare_location'].replace(r'[-]+', "NaN", regex=True)

nasa_data_frame['flare_region'] = nasa_data_frame['flare_region'].replace(r'[a-zA-Z]+', "NaN", regex=True)
nasa_data_frame['flare_region'] = nasa_data_frame['flare_region'].replace(r'[-]+', "NaN", regex=True)

nasa_data_frame['importance'] = nasa_data_frame['importance'].replace(r'[-]+', "NaN", regex=True)

nasa_data_frame['cme_date'] = nasa_data_frame['cme_date'].replace(r'--/--', "NaN", regex=True)

nasa_data_frame['cme_time'] = nasa_data_frame['cme_time'].replace(r'--:--', "NaN", regex=True)

nasa_data_frame['cpa'] = nasa_data_frame['cpa'].replace(r'[-]+', "NaN", regex=True)
nasa_data_frame['width'] = nasa_data_frame['width'].replace(r'[-]+', "NaN", regex=True)
nasa_data_frame['spd'] = nasa_data_frame['spd'].replace(r'[-]+', "NaN", regex=True)

nasa_data_frame['width_lower_bound'] = [True if '>' in i else False for i in nasa_data_frame['width']]
nasa_data_frame['width'] = [i if '>' not in i else i[1:] for i in nasa_data_frame['width']]

start_date_list = [x.split('/') for x in nasa_data_frame['start_date']]
start_time_list = [x.split(':') for x in nasa_data_frame['start_time']]
start_date_time_list = [datetime.datetime.combine(
                datetime.date(year=int(start_date_list[x][0]),
                            month=int(start_date_list[x][1]),
                            day=int(start_date_list[x][2])),
                
                datetime.time(
                            hour=int(start_time_list[x][0]),
                            minute=int(start_time_list[x][1]))) 
                for x in range(len(start_date_list))]

nasa_data_frame['start_datetime'] = start_date_time_list

end_date_list = [x.split('/') for x in nasa_data_frame['end_date']]
end_time_list = [x.split(':') for x in nasa_data_frame['end_time']]

end_date_time_list = [datetime.datetime.combine(
                datetime.date(year=int(start_date_list[x][0]),
                            month=int(end_date_list[x][0]),
                            day=int(end_date_list[x][1])),
                
                datetime.time(
                            hour=int(end_time_list[x][0]) if end_time_list[x][0] != '24' else 0,
                            minute=int(end_time_list[x][1]))) 
                for x in range(len(end_time_list))]

nasa_data_frame['end_datetime'] = end_date_time_list

cme_date_list = [x.split('/') for x in nasa_data_frame['cme_date']]
cme_time_list = [x.split(':') for x in nasa_data_frame['cme_time']]

cme_date_time_list = []

for x in range(len(cme_date_list)):

    if 'NaN' not in cme_date_list[x] and x != len(cme_date_list)-1:
        cme_date_time_list.append(
                            datetime.datetime.combine(
                            datetime.date(year=int(start_date_list[x][0]),
                            month=int(cme_date_list[x][0]),
                            day=int(cme_date_list[x][1])),
                
                            datetime.time(
                            hour=int(cme_time_list[x][0]),
                            minute=int(cme_time_list[x][1])))
                        )
    else:
        cme_date_time_list.append('NaN')


nasa_data_frame['cme_datetime'] = cme_date_time_list

del nasa_data_frame['start_date']
del nasa_data_frame['end_date']
del nasa_data_frame['start_time']
del nasa_data_frame['end_time']
del nasa_data_frame['cme_date']
del nasa_data_frame['cme_time']

nasa_data_frame['is_halo'] = [True if x == 'Halo' else False for x in nasa_data_frame['cpa']]
nasa_data_frame['cpa'] = [x if x != 'Halo' else 'NaN' for x in nasa_data_frame['cpa']]

nasa_data_frame.to_csv('radwan.csv')