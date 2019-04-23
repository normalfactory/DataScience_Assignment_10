#- Scrape Mars Data
# Functionality to scrape different websites about Mars.
#
# Scott McEachern
# April 23, 2019


#-- Dependences
import requests
from splinter import Browser
from bs4 import BeautifulSoup

import time
import urllib.parse
import pandas as pd


def scrape():
    ''' Scrapes the data about Mars from different websites
    
    Accepts : nothing

    Returns: dictionary with the following keys:
                'news_title' (string) latest news title from NASA
                'news_p' (string) latest news from NASA, summary paragraph 
                'featured_image_url' (string) URL to the featured image of Mars
                'mars_weather' (string) metadata on latest weather on Mars
                'marsFactsHtml' (string) facts on Mars that is formated in HTML table
                'hemisphere_image_urls' (list) information on the different hemispheres
                        'title' (string) name of the hemisphere
                        'img_url' (string) URL to image of the hemisphere

    '''

    print('Start scrape processing')


    #-- Initialize Browser
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    print('Completed initialization of browser')


    #-- 1 - NASA Mars News
    print("--> 1")
    print("NASA Mars News: Start scraping")

    nasaMarsNewsUrl = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'

    browser.visit(nasaMarsNewsUrl)

    print("NASA Mars News: Completed load of site")


    #- Delay 
    # It was found that the first time the script is run, the async content is not dowloaded and the delay is 
    # to ensure that the content can be downloaded before attempting to search for content on page
    time.sleep(5)

    print("NASA Mars News: Delay for download is completed")


    #- Parse Page
    nasaMarsNewsSoup = BeautifulSoup(browser.html, 'html.parser')


    #- Get Content
    newsList = nasaMarsNewsSoup.find_all('li', class_='slide')


    #- Get First News
    news_title = ''
    news_p = ''

    if (len(newsList) > 1):
        news_title = newsList[0].find('div', class_='content_title').text
        
        news_p = newsList[0].find('div', class_='article_teaser_body').text


    print('NASA Mars News: Completed scrape for the Mars news')


    #-- 2 - JPL Mars Space Images
    print("--> 2")
    print("JPL Mars Images: Start scraping")

    marsSpaceImagesUrl = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(marsSpaceImagesUrl)


    #- Navigate to Featured Image
    browser.click_link_by_partial_text('FULL IMAGE')

    print("JPL Mars Images: Completed navigation to featured image")


    #- Wait
    # To ensure success in navigating to metadata page; wait for 2 seconds
    time.sleep(2)


    #- Navigate to Metadata
    browser.click_link_by_partial_text('more info')

    print("JPL Mars Images: Completed navigation to metadata page")


    #-- Parse Page
    spaceImageSoup = BeautifulSoup(browser.html, 'html.parser')


    #-- Get URL to Feature Image
    #- Get List of Image Details
    imageMetadataList = spaceImageSoup.find_all('div', class_='download_tiff')


    #- Get JPG
    featured_image_url = ''

    for imageMetadata in imageMetadataList:
        
        if ('Full-Res JPG' in imageMetadata.text):
                    
            #- Create URL
            baseUrl = "https:"
            featured_image_url = urllib.parse.urljoin(baseUrl, imageMetadata.find('a')['href'])
            
            break

    print('JPL Mars Images: Completed scraping')


    #--> 3 - Mars Weather
    print('--> 3')
    print('Mars Weather: Started scraping')

    marsWeatherUrl = 'https://twitter.com/marswxreport?lang=en'

    browser.visit(marsWeatherUrl)

    print('Mars Weather: Completed navigation to site')


    #- Parse Page
    weatherSoup = BeautifulSoup(browser.html, 'html.parser')


    #-- Get Latest Weather
    #- Get Div with List of weather reports
    weatherStreamDivs = weatherSoup.find_all('div', class_='stream')


    #- Get List of Weather Reports
    weatherReportsList = weatherStreamDivs[0].find_all('li')


    #- Get Latest Weather
    latestWeatherDiv = weatherReportsList[0].find('div', class_='js-tweet-text-container')


    #- Get Weather
    # Paragraphy contains twitter image text, remove that
    weatherRemove = latestWeatherDiv.find('a').text

    weatherAll = latestWeatherDiv.find('p').text

    mars_weather = weatherAll.replace(weatherRemove, '')

    print('Mars Weather: Completed scraping')


    #-- 4 - Mars Facts
    print('--> 4')
    print('Mars Facts: Started scraping')

    marsFactsUrl = 'https://space-facts.com/mars/'

    marsFactsTables = pd.read_html(marsFactsUrl)

    marsFacts_df = marsFactsTables[0]


    #- Rename Columns
    marsFacts_df.columns = ['Fact', 'Info']


    #- Create HTML Table
    marsFactsHtml = marsFacts_df.to_html(index=False)


    #- Cleanup HTML
    marsFactsHtml = marsFactsHtml.replace('\n', '')

    print('Mars Facts: Completed scraping')


    #-- 5 - Mars Hemispheres
    print('--> 5')
    print('Mars Hemispheres: Started scraping')

    marsHemispheresUrl = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(marsHemispheresUrl)

    print('Mars Hemispheres: Completed navigation to page')


    #-- Get Names of buttons
    #- Parse Page
    hemisphereSoup = BeautifulSoup(browser.html, 'html.parser')

    #- Div of Hemispheres
    divHemispheres = hemisphereSoup.find_all('div', class_='description')

    #- Loop Through divs and get name of hyperlink
    hyperlinkTitles = []

    for divHemisphere in divHemispheres:
        hyperlinkTitles.append(divHemisphere.find('h3').text)

    print('Mars Hemispheres: Completed getting list of button names')


    #-- Get Hemisphere Metadata
    hemisphere_image_urls = []

    for hyperlinkTitle in hyperlinkTitles:
        
        #- Navigate to page
        browser.click_link_by_partial_text(hyperlinkTitle)
        
        print(f'Mars Hemispheres: Completed navigation to details page: {hyperlinkTitle}')
        
        
        #- Parse Page
        hemisphereDetailSoup = BeautifulSoup(browser.html, 'html.parser')
        
        
        #- Get Div with Metadata
        downloadDiv = hemisphereDetailSoup.find('div', class_='downloads')
        
        
        #- Get Image URL
        hemisphereImageUrl = downloadDiv.find('a')['href']
        
        #- Add Dictionary to list
        hemisphere_image_urls.append(
        {
            'title': hyperlinkTitle.replace(' Enhanced', ''),
            'img_url': hemisphereImageUrl
        })
        
        
        print(f'Mars Hemispheres: Success getting image URL: {hemisphereImageUrl}')
        
        
        #- Return to source page
        browser.visit(marsHemispheresUrl)

    print('Mars Hemispheres: Completed scraping')


    #-- Prepare Results
    print("--> Completed")
    print("Completed with the scraping of the data")

    results = {
        'news_title' : news_title,
        'news_p': news_p,
        'featured_image_url': featured_image_url,
        'mars_weather': mars_weather,
        'marsFactsHtml': marsFactsHtml,
        'hemisphere_image_urls': hemisphere_image_urls
    }

    return results
