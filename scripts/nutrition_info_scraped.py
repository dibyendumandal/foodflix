# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 00:28:36 2018

@author: sudha
"""

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd


nutrition = []

# run for: 
# 76500  : 76999
# 254000 : 255000
# 255000 : 256000
# 256000 : 257000
# 257000 : 258000

# to run for: 
# 220000 : 240000

for i in range(220000, 240000, 1):
    url = 'https://www.allrecipes.com/recipe/' + str(i)
    print(url)

    r = requests.get(url)
    if (r.status_code == 200):
        soup = BeautifulSoup(r.content, 'html.parser') 
        recipe_info = soup.find('section', attrs={'class':'recipe-ingredients'})
        href_tags = soup.find(href=True)
        recipe_id = (href_tags['href']).split('/')[4]
        recipe_url = href_tags['href']

        if (soup.find_all('span', attrs={'itemprop': 'calories'})):
            calories = (soup.find_all('span', attrs={'itemprop': 'calories'}))[0].text
        else:
            calories = ''

        if (soup.find_all('span', attrs={'itemprop': 'fatContent'})):
            fat = (soup.find_all('span', attrs={'itemprop': 'fatContent'}))[0].text
        else:
            fat = ''

        if (soup.find_all('span', attrs={'itemprop': 'carbohydrateContent'})):
            carb = (soup.find_all('span', attrs={'itemprop': 'carbohydrateContent'}))[0].text
        else:
            carb = ''

        if (soup.find_all('span', attrs={'itemprop': 'proteinContent'})):
            protein = (soup.find_all('span', attrs={'itemprop': 'proteinContent'}))[0].text
        else:
            protein = ''

        if (soup.find_all('span', attrs={'itemprop': 'cholesterolContent'})):
            cholesterol = (soup.find_all('span', attrs={'itemprop': 'cholesterolContent'}))[0].text
        else:
            cholesterol = ''

        if (soup.find_all('span', attrs={'itemprop': 'sodiumContent'})):
            sodium = (soup.find_all('span', attrs={'itemprop': 'sodiumContent'}))[0].text
        else:
            sodium = ''


        r1 = [recipe_id, recipe_url, calories, fat, carb, protein, cholesterol, sodium]
        nutrition.append(r1)

    time.sleep(1)
    
#print(nutrition)  

df = pd.DataFrame(nutrition, columns=['recipe_id', 'recipe_url', 'calories', 'fat', 'carb', 'protein', 
                                    'cholesterol', 'sodium'])
df.to_csv('nurtient_info.csv', index=False, encoding='utf-8') 
  