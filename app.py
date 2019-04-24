#-- Flask App with Mission to Mars
#  This Flask website is for the UCSD Data Science course that is to scrape data
#  from online resources and display within this site.
#
#  Assumption that able to connect to local instance of MongoDB on port 27017 and creates the following:
#       Database: marsMissionDB
#       Collection: scrapeInfo
#
# Scott McEachern
# April 23, 2019


#-- Dependencies
from flask import Flask, render_template
import scrape_mars

import pymongo
import datetime


#-- Constants
docCreateDate = 'createdate'


#-- Initialize MongoDB

#- Connect to database
conString = 'mongodb://localhost:27017'

client = pymongo.MongoClient(conString)


#- Reference Collection
missionDb = client['marsMissionDB']

scrapeCollection = missionDb['scrapeinfo']

print('Completed connecting MongoDB and referencing collection')



#-- Initialize App
app = Flask(__name__)

print("Completed initialization of app")


#-- Routes

#- Route: Home
@app.route("/")
def homeRoute():
    print("=> Request: Home")


    #-- Get Mars Data from database
    marsDocs = getScrapeInfo()


    #-- Update Table for Bootstrap
    marsDocs['marsFactsHtml'] = marsDocs['marsFactsHtml'].replace('class="dataframe"', 'class="table table-sm table-striped"')


    return render_template('index.html', dict=marsDocs)


#- Route: Scrape
@app.route('/scrape')
def scrapeRoute():
    print("=> Request: scrape")

    #-- Get Scrape Data
    scrapeResult = scrape_mars.scrape()


    #-- Store Data within MongoDB
    insertIntoMongoDB(scrapeResult)


    return "Completed scraping of Mars information"



#-- Work with MongoDB

def insertIntoMongoDB(scrapeResult):
    ''' Inserts the scraping results dictionary into MongoDB; updates the dictionary to include the current date in UTC

    Accepts : scrapeResult (dictionary) contains metadata from the scraping

    Returns : none
    '''

    #- Add Create Date
    scrapeResult[docCreateDate] = datetime.datetime.utcnow()

    #- Insert Document
    scrapeCollection.insert_one(scrapeResult)

    print("Completed saving document into the scrapeinfo collection in MongoDB")



def getScrapeInfo():
    ''' Gets the latest scrape information from the MongoDB; if no item found then does the scrape

    Accepts : none

    Returns : (dictionary) contains the metadata from the scraping
    '''

    #- Get Latest Scrape Information
    hasMarsInfo = False
    scrapeInfo = None

    marsDocs = scrapeCollection.find().sort(docCreateDate, -1)

    for doc in marsDocs:
        scrapeInfo = doc
        hasMarsInfo = True

        print("MongoDB contained scrape information")
        break


    #- Check for Scrape Information
    if (hasMarsInfo == False):

        print("MongoDB did not contain scrape information")

        # Get Scrape Information
        scrapeInfo = scrape_mars.scrape()

        # Store in Mongo DB
        insertIntoMongoDB(scrapeInfo)


    return scrapeInfo


#-- Start Application
if __name__ == "__main__":
    app.run(debug=True)