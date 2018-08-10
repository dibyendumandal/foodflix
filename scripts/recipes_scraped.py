# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 00:28:36 2018

@author: sudha
"""

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd


records = []

# run for: 
# 76500  : 76999
# 254000 : 255000
# 255000 : 256000
# 256000 : 257000
# 257000 : 258000

for i in range(220000, 240000,1):
    url = 'https://www.allrecipes.com/recipe/' + str(i)
    print(url)

    r = requests.get(url)
    if (r.status_code == 200):
        soup = BeautifulSoup(r.content, 'html.parser') 
        recipe_info = soup.find('section', attrs={'class':'recipe-ingredients'})
        href_tags = soup.find(href=True)
        recipe_id = (href_tags['href']).split('/')[4]
        recipe_name = (href_tags['href']).split('/')[5]
        recipe_url = href_tags['href']
        ingred = soup.find_all(class_="recipe-ingred_txt added")
        ingredients = []
        for result in ingred:
            ingredients.append(result.text)
        if (soup.find('span', attrs={'class':'ready-in-time'})):
            cook_time = (soup.find('span', attrs={'class':'ready-in-time'})).text
        else:
            cook_time = ''

        if ((soup.find('span', attrs={'class':'calorie-count'}))):
            calorie_count = (soup.find('span', attrs={'class':'calorie-count'})).text
        else:
            calorie_count = ''

        review_count = (soup.find('span', attrs={'class': 'review-count'})).text
        rating_text = (soup.find('div', attrs={'class':'rating-stars'}))
        overall_rating = re.findall("\d*\.*\d+", str(rating_text))[0]

        r1 = [recipe_id, recipe_name, recipe_url, ingredients, cook_time, calorie_count, review_count, str(overall_rating)]
        records.append(r1)

    time.sleep(1)
    
#print(records)  

df = pd.DataFrame(records, columns=['recipe_id', 'recipe_name', 'recipe_url', 'ingredients', 
                                    'cook_time', 'calorie_count', 'review_count', 'overall_rating'])
df.to_csv('recipe_info.csv', index=False, encoding='utf-8') 
  
#df = pd.DataFrame(records, columns=['recipe_id', 'recipe_name', 'ingredients', 
#                                    'cook_time', 'calorie_count', 'review_count'])  
#df.to_csv('recipe_info.csv', index=False, encoding='utf-8') 

# include rating
# include url
# include picture



#df = pd.DataFrame(records, columns=['recipe_id', 'recipe_name', 'ingredients_list', 'cooking_time', 'calorie_count', 'total_reviews'])  
#df['date'] = pd.to_datetime(df['date'])  
#df.to_csv('trump_lies.csv', index=False, encoding='utf-8') 

#match = re.search(r'inch\W+', r2)