"""
Utilities
"""

import re

def calc_calperday(activity,bmr):
    '''
    Calculate the amount of calories a person of certain
    activity level would lose.

    Ref: https://www.freedieting.com/calorie-needs

    :param activity: activity level from sendentary to very active
    :param bmr: person's BMR
    :return: calories lost per day
    '''
    activity_factor = {"sedentary":1.2,
                       "light":1.45,
                       "active":1.7,
                       "very":1.9}
    return bmr*activity_factor[str(activity)]
    

def calc_bmr(gender,age,weight,feet,inches):
    '''
    Calculate BMR using Mifflin-St Jeor Equation:
    For men:BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(y) + 5
    For women:BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(y) - 161

    Ref: https://www.calculator.net/

    :param gender: female (F) or male (M)
    :param age: in years
    :param weight: person's weight in pounds
    :param feet: person's height, only feet part
    :param inches: person's height, only inches part
    :return: person's BMR
    '''
    weight = float(weight)*0.453592 # pounds to kg
    height = float(feet)*30.48 + float(inches)*2.54 #feet/inches to m

    bmr = 0
    if gender == 'F':
        bmr = 10*weight + 6.25*height - 5*float(age) - 161
    elif gender == 'M':
        bmr = 10*weight + 6.25*height - 5*float(age) + 5
    else:
        print("Don't know gender: ",gender)

    return bmr


def calc_bmi(weight,feet,inches):
    '''
    Calculate BMI as:
    weight[kg]/(height[m]^2)

    :param weight: person's weight in pounds
    :param feet: person's height, only feet part
    :param inches: person's height, only inches part
    :return: person's BMI
    '''

    weight = float(weight)*0.453592 # pounds to kg
    height = float(feet)*0.3048 + float(inches)*0.0254 #feet/inches to m
    return weight/height**2

# ------------------------------------------------------------------------------
#       DATA CLEANING
# ------------------------------------------------------------------------------
