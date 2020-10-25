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
client = Socrata("data.sfgov.org", None)

results = client.get("jjew-r69b", limit=20000)

results_df = pd.DataFrame.from_records(results)
results_df['start24'] = results_df.start24.apply(parse_time_str)
results_df['end24'] = results_df.end24.apply(parse_time_str)
# pprint(results_df['start24'].dt.time)
# pprint(results_df['end24'].dt.time)

time_filter_1 = results_df['start24'] <= now
time_filter_2 = now <= results_df['end24']
time_filter = time_filter_1 & time_filter_2
day_filter = results_df['dayorder'] == now.isoweekday()
date_time_filter = day_filter & time_filter
print(results_df.loc[date_time_filter])
