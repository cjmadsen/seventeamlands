import pandas as pd
import requests
import re
from datetime import date, timedelta
from app import utils

def get_color_pair_data(expansion, endpoint=None, start=None, end=None):
    if endpoint is None:
        endpoint = f"https://www.17lands.com/color_ratings/data?expansion={expansion.upper()}&event_type=PremierDraft"
        if start is not None:
            endpoint += f"&start_date={str(start)}"
            if end is None:
                end = date.today()
            endpoint += f"&end_date={str(end)}"
        endpoint+= f"&combine_splash=false"
    color_json = requests.get(endpoint).json()
    if 'status' in color_json:
        raise Exception(f"Endpoint for metagame not available: {color_json['detail']}")
    color_df = pd.DataFrame(color_json)
    color_df['win_rate'] = [color_df['wins'][x]/color_df['games'][x] for x in range(len(color_df))]
    color_df['meta_share'] = [color_df['games'][x]/color_df['games'].iloc[len(color_df.index) - 1]  for x in range(len(color_df))]
    color_df = color_df.drop(['is_summary'], axis=1)
    return color_df

def get_format_history(deck_set,release_date):
    tp = get_color_pair_data(deck_set,start=release_date)
    utils.google_sheets_upload(tp, 'Team Performance', sheet_range='K2')
    yield tp

#worksheet = sht1.worksheet('Team Performance')
#worksheet.update('J1:N61', [dataframe.columns.values.tolist()] + dataframe.values.tolist())
def get_metagame(deck_set):
    present = get_color_pair_data(deck_set, start = date.today()-timedelta(days=10))
    past = get_color_pair_data(deck_set,start = date.today()-timedelta(days=20), end = date.today()-timedelta(days=10))
    present['win_rate_delta'] = [present['win_rate'][x]-past['win_rate'][x] for x in range(len(present))]
    present['meta_share_delta'] = [present['meta_share'][x]-past['meta_share'][x] for x in range(len(present))]
    present = present[['color_name', 'wins', 'games', 'win_rate','win_rate_delta', 'meta_share','meta_share_delta']]
    utils.google_sheets_upload(present, 'Metagame Breakdown')
    yield present

#worksheet = sht1.worksheet('Metagame Breakdown')
#worksheet.update('J1:N61', [dataframe.columns.values.tolist()] + dataframe.values.tolist())

# get_format_history(deck_set='NEO',release_date ='2022-03-10')
