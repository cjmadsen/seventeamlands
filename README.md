# Flask on Heroku

This project is intended to help you tie together some important concepts and
technologies from the 12-day course, including Git, Flask, JSON, Pandas,
Requests, Heroku, and Bokeh for visualization.

The repository contains a basic template for a Flask configuration that will
work on Heroku.

A [finished example](https://lemurian.herokuapp.com) that demonstrates some basic functionality.

## Step 1: Setup and deploy
- Git clone the existing template repository.
- `Procfile`, `requirements.txt`, `conda-requirements.txt`, and `runtime.txt`
  contain some default settings.
- There is some boilerplate HTML in `templates/`
- Create Heroku application with `heroku create <app_name>` or leave blank to
  auto-generate a name.
- Deploy to Heroku: `git push heroku master`
- You should be able to see your site at `https://<app_name>.herokuapp.com`
- A useful reference is the Heroku [quickstart guide](https://devcenter.heroku.com/articles/getting-started-with-python).

## Step 2: Get data from API and put it in pandas
- Use the `requests` library to grab some data from a public API. This will
  often be in JSON format, in which case `simplejson` will be useful.
- Build in some interactivity by having the user submit a form which determines which data is requested.
- Create a `pandas` dataframe with the data.

## Step 3: Use Bokeh to plot pandas data
- Create a Bokeh plot from the dataframe.
- Consult the Bokeh [documentation](http://bokeh.pydata.org/en/latest/docs/user_guide/embed.html)
  and [examples](https://github.com/bokeh/bokeh/tree/master/examples/embed).
- Make the plot visible on your website through embedded HTML or other methods - this is where Flask comes in to manage the interactivity and display the desired content.
- Some good references for Flask: [This article](https://realpython.com/blog/python/python-web-applications-with-flask-part-i/), especially the links in "Starting off", and [this tutorial](https://github.com/bev-a-tron/MyFlaskTutorial).


# Update: 12/04/22

1. The code was refactored a bit for readbility.
- There is a subfolder now called app which contains the majority of the files necessary
- `run.py` is now the file used to enter the app and run so the environment variable FLASK_APP needs to be set to 'run.py'
- Procfile was updated to include logging and capturing print statments. This means when you deploy the site, you can run `heroku logs` to show you the output of any print statements
- The app/static folder contains the google_creds.json structure which is needed to authorize the upload to google sheets. The library used for this is `gspread` located in `utils.py > google_sheets_upload`.
- Tokens.json in app/static is where you would add more tokens used to scrape the url.
- Inside __init__.py is the contructor used to define the app and the routes located in views.py
- `scrape_results` contains all of your business logic for scraping all the tokens in a loop and your dataframe operations
- `utils` contains methods to create the driver object based on if you are in production or development. `get_tokens` returns all the tokens in the tokens.json file.
- `views` is where you define your app's urls and endpoints. The first app.route here is the base url going to the index.html page which contains a button to start the script. The endpoint `/results` is defined here which was previously defined as a resource class (nothing wrong with this, just a preference for defining more endpoints and html pages).

2. Previously when the `/results` was hit, it would have to wait for a response after all the scraping was done and this would cause a timeout on heroku. Currently, it will start a thread in the background to do the scraping and then return a response before the thread is finished so there is no timeout.

3. In order to upload the dataframe to google sheets, some information needs to be saved as environment variables in heroku.

Here is a list of those variable in caps which can be found on heroku under Settings > Reveal config vars
```
{
  "type": "service_account",
  "project_id": PROJECT_ID,
  "private_key_id": PRIVATE_KEY_ID,
  "private_key": PRIVATE_KEY,
  "client_email": CLIENT_EMAIL,
  "client_id": CLIENT_ID,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": CERT_URL
}
```

`SPREADSHEET_KEY` is the spreadsheet key of your google sheet found in the url of the sheet betwee d/ and /edit

Also remember to share the google sheet with hte client email stored as a variable.

## Update 18/04/22

- Added the endpoint /metagame_card_stats
- It contains two parameters:
  - set
  - release_date (optional)
- The set is the deck name and release date is in the format YYYY-MM-DD

eg. /metagame_card_stats?set=neo&release_date=2022-03-10

This endpoint runs the get_metagame, get_format_history and the card_stats methods.

