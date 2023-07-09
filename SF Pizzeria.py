# Importing the different libraries or packages needed for the project
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import os
import pymongo
from pymongo import MongoClient
import urllib.parse
import re
import http.client, urllib.parse
import json

def part_four_five():
    # (Ques 4)  Yellow Pages uses GET requests for its search.  Using plain Python or Java (no Selenium), write a program that
    # searches on yellowpages.com for the top 30 “Pizzeria” in San Francisco (no need to verify that the shop is actually
    # selling pizzas, just search for “Pizzeria”, top 30 shops according to YP's "Default" sorting).  Save each search result
    # page to disk, “sf_pizzeria_search_page.html”.

    url_int = "https://www.yellowpages.com"

    # Look for Pirzzeria in San Francisco. On checking information from payload, initalizing the below payload parameters
    search_terms = "pizzeria"
    geo_location_terms = "San+Francisco"  # Replaced space between San & Francisco with a plus symbol to parse it in the URL

    # Get the information using soup (concatenate urls and key value pairs)
    URL2 = url_int + "/search?search_terms=" + search_terms + "&geo_location_terms=" + geo_location_terms
    page2 = requests.get(URL2, headers=headers)
    soup2 = BeautifulSoup(page2.text, 'lxml')

    # Save file in local
    with open("sf_pizzeria_search_page.html", "w", encoding="utf-8") as file:
        file.write(page2.text)

    # (Ques 5) Using Python or Java, write code that opens the search result page saved in (4) and parses out all shop information:

    # (1 - search rank  2- name, 3- linked URL [this store’s YP URL], 4- star rating If It Exists, 5- number of reviews IIE,
    # 6- TripAdvisor rating IIE, 7- number of TA reviews IIE, 8- “$” signs IIE, 9- years in business IIE, 10- review IIE, and
    # 11- amenities IIE). Please be sure to skip all “Ad” results

    # So total 11 attributes

    # Open the file saves and reach a core element using soup which is without any ads
    with open("sf_pizzeria_search_page.html", "r", encoding="utf-8") as yp_page:
        content = yp_page.read()
        soup3 = BeautifulSoup(content, 'lxml')
        item = soup3.select("div.search-results.organic > div.result")

    # Create empty list for all info
    ranks = []
    name = []
    link_yp = []
    star = []
    reviews = []
    ta_star = []
    dollars = []
    years = []
    reviews_ft = []
    amenities = []
    properties2 = {}

    # Extract information given in the question for each of 30 restaurants
    for i in item:

        # Get ranks and the names
        rank0 = i.find('h2', class_='n')
        rank1 = rank0.text
        ranks.append(rank1)
        name.append(rank0.a.text)

        # Applying regex to extract only rank number from the string of ranks
        rank_num = [re.findall('\d+', string)[0] for string in ranks]

        # Get links of the restaurant URLs on YP
        link0 = i.find('a', {'class': 'business-name'})['href']
        link_yp.append(url_int + link0)

        # Get star rating and reviews count (if present)
        star0 = i.find('a', {'class': 'rating hasExtraRating'})

        star0_val = "None"  # Stars
        rev0_val = "None"  # Reviews

        if star0 is not None:
            star0_val = star0.find('div')['class'][1:3]  # Stars
            rev0_val = star0.find('span', {'class': 'count'}).text  # Reviews count
        star1 = []
        reviews1 = []
        star1.append(star0_val)
        # Apply regex on reviews to get rid of paranthesis
        reviews1.append([re.sub(r'\((.*?)\)', r'\1', rev0_val)])

        # Unlist the nested list items to fetch the ratings and then join 2nd and 3rd element of list if there exists any
        # such rating with 2 items
        for z in star1:
            if isinstance(z, list):
                star.append(''.join(z))
            else:
                star.append(z)

        # Unlist the reviews to get the nested list content in the main document
        for z in reviews1:
            if isinstance(z, list):
                reviews.extend(z)
            else:
                reviews.append(z)

        # Get trip advisor star rating and reviews count (if present)
        star1 = i.find("div", class_="ratings").attrs.get('data-tripadvisor')
        if star1 is not None:
            star1_val = star1
        else:
            star1_val = "None"
        ta_star.append(star1_val)  # Contains trip advisor star & ratings count

        # Dollars (if present)
        dollar0 = i.find('div', class_='price-range')
        dollar0_val = "None"
        if dollar0 is not None:
            dollar0_val = dollar0.text
        dollars.append(dollar0_val)

        # Years in Business (if present)
        years0 = i.find('div', class_='years-in-business')
        years0_val = "None"
        if years0 is not None:
            years0_val = years0.text

        years1 = []
        # Apply regex on year to get rid of texts
        years1.append([re.sub(r'(\d+)([A-Za-z\s]*)', r'\1', years0_val)])

        # Unlist the years to get the nested list content in the main document
        for z in years1:
            if isinstance(z, list):
                years.extend(z)
            else:
                years.append(z)

        # Reviews of restaurants (if present)
        rev0 = i.find('div', class_='snippet')
        rev0_val = "None"
        if rev0 is not None:
            rev0_val = rev0.text
        reviews_ft.append(rev0_val)

        # Amenities of restaurants (if present)
        am0 = i.find('div', class_='amenities-info')
        am0_val = "None"
        if am0 is not None:
            am0_val = am0.text
        amenities.append(am0_val)

    #print("ranks:", rank_num)
    #print("names:", name)
    #print("links:", link_yp)
    #print("stars:", star)
    #print("reviews:", reviews)
    #print("trip advisor star and counts:", ta_star)
    #print("dollars:", dollars)
    #print("time in business:", years)
    #print("reviews featured:", reviews_ft)
    #print("amenities:", amenities)

    # Put everything in a dictionary to write in mongo db
    properties2 = {"ranks": rank_num, "name": name, "links": link_yp, "star": star, "reviews": reviews,
                   "trip_adv_star": ta_star, "dollars": dollars, "year_in_business": years,
                   "featured_review": reviews_ft, "amenities": amenities}
    #print(properties2)
    return rank_num, name, link_yp, star, reviews, ta_star, dollars, years, reviews_ft, amenities


def part_six_seven_eight_nine():
    # (Ques 6) Copy your code from (5). Modify the code to create a MongoDB collection called “sf_pizzerias” that stores all
    # the extracted shop information, one document for each shop.

    rank_num, name, link_yp, star, reviews, ta_star, dollars, years, reviews_ft, amenities = part_four_five()

    # Select the database and collection that will hold pizzeria properties
    db = client["ddrproject"]
    col2 = db["sf_pizzerias"]

    # Store everything in dictionary and push all the values into mongodb
    for i in range(0, 30):
        document = {"ranks": rank_num[i], "name": name[i], "links": link_yp[i], "star": star[i], "reviews": reviews[i],
                    "trip_advisor": ta_star[i], "dollars": dollars[i], "year_in_business": years[i],
                    "featured_review": reviews_ft[i], "amenities": amenities[i]}
        col2.insert_one(document)

    # (Ques 7) Write code that reads all URLs stored in “sf_pizzerias” and download each shop page. Store the page to disk,
    # “sf_pizzerias_[SR].htm” (replace [SR] with the search rank)

    # Extract id, rank and links from mongodb
    show_col = {"_id": 1, "ranks": 1, "links": 1}

    mongo_rank = []
    mongo_link = []
    mongo_id = []

    # Get each of the columns from mongo and store it in list to loop through (ID, Ranks, Links)
    for each in col2.find({}, show_col):
        mongo_id.append(each["_id"])
        mongo_rank.append(each["ranks"])
        mongo_link.append(each["links"])

    # Download the pages from the list of links extracted from mongo
    for i in range(0, 30):
        page = mongo_link[i]
        response_content = requests.get(page)
        with open(f"sf_pizzerias_[{mongo_rank[i]}].html", "w", encoding="utf-8") as file:
            file.write(response_content.text)

    # (Ques 8) Write code that reads the 30 shop pages saved in (7) and parses each shop’s address, phone number, and website.
    # Create list to store these values
    phone = []
    address = []
    website = []

    # Loop through the pages to get the mentioned infos
    for i in range(0, 30):
        with open(f"sf_pizzerias_[{mongo_rank[i]}].html", "r", encoding="utf-8") as page:
            content = page.read()
            soup4 = BeautifulSoup(content, 'lxml')
            detail = soup4.select("section.inner-section")
            for j in detail:

                # Fetch phone numbers
                phone0 = j.find('a', {'class': 'phone dockable'})
                if phone0:
                    phone.append(phone0['href'].strip())
                else:
                    phone.append(None)

                # Fetch address
                add0 = j.find('span', {'class': 'address'})
                if add0:
                    address.append(add0.text.strip())
                else:
                    address.append(None)

                # Fetch website
                web0 = j.find('a', {'class': 'website-link'})
                if web0:
                    website.append(web0['href'])
                else:
                    website.append(None)

    # print(phone)
    # print(address)
    # print(website)


    # (Ques 9)  Sign up for a free account with https://positionstack.com/Links to an external site.  Copy your code from (8).
    # Modify the code to query each shop address’ geolocation (long, lat).  Update each shop document on the MongoDB collection
    # “sf_pizzerias” to contain the shop’s address, phone number, website, and geolocation

    access_key = "c37623cb6f23161902b2e7dbc4347210"
    conn = http.client.HTTPConnection('api.positionstack.com')
    json_obj = []

    # Got the below code from same website itself (https://positionstack.com/documentation), to establish connection in Python
    # Loop through address to feed address into the below code and get latitudes and longitudes

    for i in range(0, 30):
        # Apply regex on address to add space before San Francisco
        address[i] = re.sub(r'(San Francisco)', r' \1', address[i])

        params = urllib.parse.urlencode({'access_key': access_key, 'query': address[i]})
        conn.request('GET', '/v1/forward?{}'.format(params))
        res = conn.getresponse()
        data = res.read()
        data1 = data.decode('utf-8')
        json_obj.append(json.loads(data1))

    #print(json_obj)

    lat = []
    long = []
    geo = []

    # loop inside json object to get latitude and longtitude
    for i in range(0, 30):
        for loc in json_obj[0]['data']:
            lat.append(loc['latitude'])
            long.append(loc['longitude'])

    # Combine latitude and longitude into a single list called "geo"
    geo = list(zip(lat, long))

    # Create a dictionary and push data to mongo
    for i in range(0, 30):
        col2.update_one({"_id": mongo_id[i]}, {
            "$set": {"address": address[i], "phone": phone[i], "website": website[i], "geolocation": geo[i]}})


if __name__ == '__main__':


    part_four_five()

    part_six_seven_eight_nine()
