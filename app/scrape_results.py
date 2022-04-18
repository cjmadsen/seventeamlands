
from time import sleep
from app import utils
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_results(tokens):
    resp_list = []
    master = []
    for z in tokens.keys():
        driver = utils.create_driver()
        try:
            driver.get("https://www.17lands.com/user_history/{}".format(z))
            resp = {'status_code': 200, 'msg': f"Success for {tokens[z]}"}
            sleep(1)
            html = driver.execute_script("return document.getElementsByTagName('tbody')[0].innerHTML")
            soup = BeautifulSoup(html, "html.parser")
            for x in range(len(soup.find_all('tr'))):
                tr= soup.find_all('tr')[x] #tr is the tag the deliniates distinct drafts
                td=tr.find_all('td') #td gives us the individual parts. because td has type Resultset, we can't find_all('a') and have to use regex
                data = [x.string for x in td] #if one of the elements has multiple tags or no obvious string, it returns None
                if 'PremierDraft' not in data:
                    continue
                if len(data) != 9:
                    continue
                data=list(filter(None, data)) #remove Nones from the list
                #data.pop(3) #removes Format
                data.insert(3,int(data[2][-1])) #adds losses after record
                data[2]=int(data[2][0]) #converts record into wins
                if len(data) != 7:
                    continue
                try:
                    data.append(re.search(pattern='title="(.*?)"', string=str(td[3])).group(1)) #finds colors and appends it to the list
                except:
                    continue
                links = re.findall(pattern='<a href="(.*?)</a>', string=str(td[-1])) #finds each link string
                links = ['https://www.17lands.com/'+links[x] for x in range(len(links))] #completes the link
                links = [links[x].split('>') for x in range(len(links))] #splits the link from the description
                for x in range(len(links)):
                            links[x]= [links[x][1], links[x][0]] #inverts the order of the description and link to prep for being a dictionary
                links_dict = dict(links) #turns list of lists into dictionary with descriptions as keys and links as values
                data.append(links_dict) #adds the dictionary to the list
                data.append(tokens[z])
                master.append(data)
        except Exception as e:
            resp = {'status_code': 400, 'msg': f"FAIL for {tokens[token]}", 'error': str(e)}
        resp_list.append(resp)
        driver.close()
        df_ops(master)
    return resp_list

def df_ops(master):
    df = pd.DataFrame(master, columns = ['Date','Set','Wins','Losses','Format','Start Rank', 'End Rank', 'Colors', 'Links', 'Pilot'])
    df['Draft'] = [df['Links'][x]['Draft'][:-1] if 'Draft' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Pool'] = [df['Links'][x]['Pool'][:-1] if 'Pool' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Details'] = [df['Links'][x]['Details'][:-1] if 'Details' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 1'] = [df['Links'][x]['Deck 1'][:-1] if 'Deck 1' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 2'] = [df['Links'][x]['Deck 2'][:-1] if 'Deck 2' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 3'] = [df['Links'][x]['Deck 3'][:-1] if 'Deck 3' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 4'] = [df['Links'][x]['Deck 4'][:-1] if 'Deck 4' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 5'] = [df['Links'][x]['Deck 5'][:-1] if 'Deck 5' in df['Links'][x].keys() else None for x in range(len(df))]
    df.drop(columns=['Links'], inplace=True)
    df = df[df['Set'] == 'NEO'].copy()
    utils.google_sheets_upload(df)