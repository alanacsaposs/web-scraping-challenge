
# Dependencies
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pandas as pd
from collections import OrderedDict

def init_browser(): 
    # Replace the path with your actual path to the chromedriver
    # Mac Users (Me)
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

    # Windows Users
    # executable_path = {'executable_path': '/Users/cantu/Desktop/Mission-to-Mars'}
    # return Browser('chrome', **executable_path, headless=False)


# Scrape for News
def scrape(): 

    # Initialize browser 
    browser = init_browser()

    # Dictionary to hold ALL of the mars data
    mars_data = {}

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'

    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')

    #Find title and body elements
    results = soup.find('div', class_='slide')

    ####### ARTICLE_TITLE
    # Identify and return title of article
    article_title = results.find('div', class_='content_title').text
    ####### ARTICLE_BODY
    # Identify and return body preview of article
    article_body = results.find('div', class_='rollover_description_inner').text

    #Add ARTICLE_TITLE and ARTICLE_BODY to dictionary
    mars_data['news_title'] = article_title
    mars_data['news_paragraph'] = article_body

    # Scrape for Featured Image 
    # https://splinter.readthedocs.io/en/latest/drivers/chrome.html
    #get_ipython().system('which chromedriver')

    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)

    # Featured Image url
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup_html = BeautifulSoup(html, 'html.parser')

    results = soup_html.find('div', class_='carousel_items')

    # Parse footer for href
    footer = results.footer
    img = footer.find('a', class_='button fancybox')
    img_href = img.get('data-fancybox-href')

    # Add href to front url matter to give full url
    ####### FEATURED_IMAGE_URL
    featured_image_url = 'https://www.jpl.nasa.gov' + img_href

    # Add FEATURED_IMAGE_URL to dictionary
    mars_data['featured_image'] = featured_image_url

    # Scrape for Weather
    # Visit url
    url_weather = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url_weather)

    # Grab newest tweet
    html_weather = browser.html
    soup_weather = BeautifulSoup(html_weather, "html.parser")
    ####### MARS_WEATHER
    mars_weather = soup_weather.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text

    # Add MARS_WEATHER to dictionary
    mars_data['weather'] = mars_weather

    # Scrape for Facts
    # Visit Facts url
    url_facts = "https://space-facts.com/mars/"
    browser.visit(url_facts)

    # Read into table using Pandas
    facts_table = pd.read_html(url_facts)
    facts_table_df = facts_table[0]
        

    # Convert table in html
    ####### TABLE_HTML
    table_html = facts_table_df.to_html(index=False)

    # Add TABLE_HTML to dictionary
    mars_data['facts_table'] = table_html

    # Scrape for Hemispheres (hem)
    # Visit url
    url_hem = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url_hem)

    html_hem = browser.html
    soup_hem = BeautifulSoup(html_hem, "html.parser")
    description = soup_hem.find("div", class_="collapsible results")

    # Build List for all Links
    hem_links = []
    img_links = description.find_all('a', class_='itemLink product-item')

    for link in img_links:
        # Use Beautiful Soup's find() method to navigate and retrieve attributes
        href = link['href']
        link_to_click = 'https://astrogeology.usgs.gov' + href
        hem_links.append(link_to_click)

    # Drop Duplicate urls from List
    hem_links = list(OrderedDict.fromkeys(hem_links))

    # Create list to hold dictionaries of title and img url
    ####### HEM_IMAGE_URLS (list)
    hem_image_urls = []
    # Loop through each Link
    for href in hem_links:
        try: 
            browser.visit(href)
       
            html_hem_img = browser.html
            # Parse HTML with Beautiful Soup
            soup_hem_img = BeautifulSoup(html_hem_img, 'html.parser')
            # Retrieve all elements that contain image info
            img_info = soup_hem_img.find('section', class_='block metadata')
    
            title = img_info.find('h2', class_= 'title').text
            img_a_href = img_info.find('a')
            img_url = img_a_href.get('href')
            hem_image_urls.append({"title" : title, "img_url" : img_url})
        
            # Tab back to previous page for next link
            browser.back()
        except: print('Failed Attempt')
        
    #Add HEM_IMAGE_URLS to dictionary
    mars_data["hemisphere_imgs"] = hem_image_urls
    return(mars_data)

    browser.quit()


