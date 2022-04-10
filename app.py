from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd

import bs4
from bs4 import BeautifulSoup
import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)
api = Api(app)

class Results(Resource):
    def get(self):
        data = scrape_results()  # scrape results
        return {'data': data.to_json()}, 200  # return data as JSON object and 200 OK
    
api.add_resource(Results, '/results')  # add endpoint

TOKENS = {'89b638c0524d4d688b56ff77add5f79c':'Tom',
          'bc2862f420844334a08e36b47119df75':'Sammy',
          'baef0dbf8c8f4d978ef962ea9a0277f3':'Chris'}

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
s=Service(ChromeDriverManager().install())

def scrape_results():
    master=[]
    for z in TOKENS.keys():
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options, service=s)
        driver.implicitly_wait(100)
        driver.get("https://www.17lands.com/user_history/{}".format(z))
        sleep(10)
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
            data.insert(3,data[2][-1]) #adds losses after record
            data[2]=data[2][0] #converts record into wins
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
            data.append(TOKENS[z])
            master.append(data)
        driver.close()
    df = pd.DataFrame(master, columns = ['Date','Set','Wins','Losses','Format','Start Rank', 'End Rank', 'Colors', 'Links', 'Pilot'])
    df['Draft'] = [df['Links'][x]['Draft'] if 'Draft' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Pool'] = [df['Links'][x]['Pool'] if 'Pool' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Details'] = [df['Links'][x]['Details'] if 'Details' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 1'] = [df['Links'][x]['Deck 1'] if 'Deck 1' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 2'] = [df['Links'][x]['Deck 2'] if 'Deck 2' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 3'] = [df['Links'][x]['Deck 3'] if 'Deck 3' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 4'] = [df['Links'][x]['Deck 4'] if 'Deck 4' in df['Links'][x].keys() else None for x in range(len(df))]
    df['Deck 5'] = [df['Links'][x]['Deck 5'] if 'Deck 5' in df['Links'][x].keys() else None for x in range(len(df))]
    df.drop(columns=['Links'], inplace=True)
    return df

if __name__ == '__main__':
    app.run()  # run the Flask app