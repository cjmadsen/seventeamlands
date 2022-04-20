import pandas as pd
import requests
import re
from datetime import date, timedelta
from app import utils

def get_card_rating_data(expansion, endpoint=None, start=None, end=None, colors=None):
    if endpoint is None:
        endpoint = f"https://www.17lands.com/card_ratings/data?expansion={expansion.upper()}&format=PremierDraft"
        if start is not None:
            endpoint += f"&start_date={start}"
        if end is not None:
            endpoint += f"&end_date={end}"
        if colors is not None:
            endpoint += f"&colors={colors}"
    try:
        card_resp = requests.get(endpoint)
    except Exception as e:
        raise Exception(f"Exception at cards stats request: {e}")
    card_json = card_resp.json()
    if "status" in card_json:
        raise Exception(f"Endpoint for card stats not available: {card_json['detail']}")
    card_df = pd.DataFrame(card_json).fillna(0.0)
    card_df["name"] = card_df["name"].str.lower()
    numerical_cols = card_df.columns[card_df.dtypes != object]
    numerical_cols = numerical_cols.insert(0, "name")
    return card_df[numerical_cols]

def card_stats(deck_set, release_date=None):
    orig = get_card_rating_data(deck_set, start = date.today()-timedelta(days=10))
    master = orig.drop(["name"], axis=1)
    master=master.applymap(lambda x:x*100 if x <1 else x)
    d10 = master.copy(deep=True)
    orig_d20 = get_card_rating_data(deck_set,start = date.today()-timedelta(days=20), end = date.today()-timedelta(days=10))
    d20 = orig_d20.drop(["name"], axis=1)
    d20 = d20.applymap(lambda x:x*100 if x <1 else x)

    for col in d10.columns:
            d10.rename(columns={col:col+'_10'},inplace=True)
    d10 = d10[['avg_seen_10','avg_pick_10','win_rate_10','ever_drawn_win_rate_10','drawn_improvement_win_rate_10']]
    comparison10 = d10.join(d20[['avg_seen','avg_pick','win_rate','ever_drawn_win_rate','drawn_improvement_win_rate']], how='inner')
    comparison10['avg_seen_delta'] = [comparison10['avg_seen'][x] - comparison10['avg_seen_10'][x] for x in range(len(comparison10))]
    comparison10['avg_pick_delta'] = [comparison10['avg_pick'][x] - comparison10['avg_pick_10'][x] for x in range(len(comparison10))]
    comparison10['win_rate_delta'] = [comparison10['win_rate'][x] - comparison10['win_rate_10'][x] for x in range(len(comparison10))]
    comparison10['ever_drawn_win_rate_delta'] = [comparison10['ever_drawn_win_rate'][x] - comparison10['ever_drawn_win_rate_10'][x] for x in range(len(comparison10))]
    comparison10['drawn_improvement_win_rate_delta'] = [comparison10['drawn_improvement_win_rate'][x] - comparison10['drawn_improvement_win_rate_10'][x] for x in range(len(comparison10))]
    master = master.join(comparison10[['avg_seen_delta','avg_pick_delta','win_rate_delta','ever_drawn_win_rate_delta','drawn_improvement_win_rate_delta']], how='inner')
    colors = ['WU', 'WR', 'WG','WB', 'UR', 'UG', 'UB', 'RG','BR', 'BG']
    orig_base = get_card_rating_data(deck_set, start = date.today()-timedelta(days=10))
    base = orig_base.drop(["name"], axis=1)

    for x in colors:
        orig_pair = get_card_rating_data(deck_set, start = date.today()-timedelta(days=10), colors = x)
        pair = orig_pair.drop(["name"], axis=1)
        for col in pair.columns:
            pair.rename(columns={col:col+'_'+x},inplace=True)
        base = base.join(pair,how='inner')

    base = base[base.columns.drop(list(base.filter(regex='sideboard')))]
    base=base.applymap(lambda x:x*100 if x <1 else x)
    metrics = ['win_rate','ever_drawn_win_rate', 'drawn_improvement_win_rate']
    for z in metrics:
        metric_columns = [col for col in base.columns if z in col[0:len(z)]]
        metric_df = base[metric_columns].copy()
        md={}

        for x in metric_df.index:
            md[x]=[]
            for y in metric_df.columns[1:]:
                md[x].append((y[-2:], round(metric_df.loc[x][y],1)))

        for x in md.keys():
            string=''
            md[x].sort(key=lambda tup:tup[1], reverse=True)
            md[x] = [value for value in md[x]]# if value[1] > 0]
            for y in range(len(md[x])):
                str1,str2,str3 = md[x][y][0],str(md[x][y][1]),', '
                newstr = f'{str1} {str2}{str3}'
                string+=newstr
            string=string[:-2]
            md[x] = string
        final_df= pd.DataFrame.from_dict(md,orient='index', columns =[z +'_pairs'])
        master = master.join(final_df,how='inner')
    master['open_or_draw'] = ['Open' if master['opening_hand_win_rate'][x] > master['drawn_win_rate'][x] else 'Draw' for x in range(len(master))]
    master['open_improvement_win_rate'] = [master['opening_hand_win_rate'][x] - master['drawn_win_rate'][x] for x in range(len(master))]
    master['pick_percentage'] = [100*master['pick_count'][x]/master['seen_count'][x] for x in range(len(master))]
    master = master[['avg_seen','avg_seen_delta','avg_pick','avg_pick_delta','pick_percentage',
                'ever_drawn_win_rate','ever_drawn_win_rate_delta','ever_drawn_win_rate_pairs',
                'drawn_improvement_win_rate','drawn_improvement_win_rate_delta','drawn_improvement_win_rate_pairs',
                'win_rate','win_rate_delta','win_rate_pairs',
                'opening_hand_win_rate','open_improvement_win_rate','open_or_draw','never_drawn_win_rate']]
    master.insert(0, "name", orig["name"].tolist())
    utils.google_sheets_upload(master, 'Card Stats')
    yield master
#worksheet = sht1.worksheet('Card Stats')