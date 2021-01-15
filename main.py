from datetime import datetime, timedelta
from pprint import pprint
import pandas as pd

from sodapy import Socrata


def parse_time_str(time_str):
    if time_str[:2] != '24':
        return pd.to_datetime(time_str)
    time_str = '00' + time_str[2:]
    return pd.to_datetime(time_str) + timedelta(days=1)


now = pd.to_datetime(datetime.now())
current_day_order = now.isoweekday()
client = Socrata("data.sfgov.org")
time_str = now.strftime('%H:%M')
where_query = "start24<='{}' and end24 >= '{}'".format(time_str, time_str)
results = client.get("jjew-r69b", select='applicant,location,start24,end24,dayofweekstr',
                     dayorder=current_day_order,
                     where=where_query, order='applicant')
client.close()
results_df = pd.DataFrame.from_records(results)
print(results_df)
# results_df['start24'] = results_df.start24.apply(parse_time_str)
# results_df['end24'] = results_df.end24.apply(parse_time_str)
# # pprint(results_df['start24'].dt.time)
# # pprint(results_df['end24'].dt.time)
#
# time_filter_1 = results_df['start24'] <= now
# time_filter_2 = now <= results_df['end24']
# time_filter = time_filter_1 & time_filter_2
# day_filter = results_df['dayorder'] == now.isoweekday()
# date_time_filter = time_filter  # & day_filter
# filtered_result = results_df.loc[date_time_filter]
#
# final_result = filtered_result.sort_values('applicant')
print(results_df)
