import pandas as pd
import requests
import re
from datetime import date, timedelta

def get_color_pair_data(expansion, endpoint=None, start=None, end=None):
    if endpoint is None:
        endpoint = f"https://www.17lands.com/color_ratings/data?expansion={expansion.upper()}&event_type=PremierDraft"
        if start is not None:
            endpoint += f"&start_date={start}"
        if end is not None:
            endpoint += f"&end_date={end}"
        endpoint+= f"&combine_splash=false"
    color_json = requests.get(endpoint).json()
    color_df = pd.DataFrame(color_json).set_index("color_name")
    color_df['win_rate'] = [color_df['wins'][x]/color_df['games'][x] for x in range(len(color_df))]
    color_df['meta_share'] = [color_df['games'][x]/color_df['games'][-1] for x in range(len(color_df))]
    color_df = color_df.drop(['is_summary'], axis=1)
    return color_df

def get_format_history(set,release_date):
    get_color_pair_data(set,start=release_date)

#worksheet = sht1.worksheet('Team Performance')
#worksheet.update('J1:N61', [dataframe.columns.values.tolist()] + dataframe.values.tolist())
def get_metagame(set):
    present = get_color_pair_data(set, start = date.today()-timedelta(days=10))
    past = get_color_pair_data(set,start = date.today()-timedelta(days=20), end = date.today()-timedelta(days=10))
    present['win_rate_delta'] = [present['win_rate'][x]-past['win_rate'][x] for x in range(len(present))]
    present['meta_share_delta'] = [present['meta_share'][x]-past['meta_share'][x] for x in range(len(present))]
    present = present[['wins', 'games', 'win_rate','win_rate_delta', 'meta_share','meta_share_delta']]
    return present

#worksheet = sht1.worksheet('Metagame Breakdown')
#worksheet.update('J1:N61', [dataframe.columns.values.tolist()] + dataframe.values.tolist())

get_format_history(set = 'NEO',release_date ='2022-03-10')

get_metagame('NEO')