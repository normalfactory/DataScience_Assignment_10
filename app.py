#-- Flask App with Mission to Mars
#  This Flask website is for the UCSD Data Science course that is to scrape data
#  from online resources and display within this site.

# Scott McEachern
# April 23, 2019


#-- Dependencies
from flask import Flask
import scrape_mars


#-- Initialize App
app = Flask(__name__)

print("Completed initialization of app")


#-- Routes

#- Route: Home
@app.route("/")
def homeRoute():
    print("Request received for Home route")


    return "Hello World!"


#- Route: Scrape
@app.route('/scrape')
def scrapeRoute():
    print("Request received for scrape route")

    #-- Get Scrape Data
    theTest = scrape_mars.scrape()


    #-- Store Data within MongoDB


    return theTest['news_p']


#-- Start Application
if __name__ == "__main__":
    app.run(debug=True)