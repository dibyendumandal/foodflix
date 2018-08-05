"""
Utilities
"""

import re

def calc_bmi(weight,feet,inches):
    '''
    Calculate BMI given a weight and height

    :param weight: person's weight in pounds
    :param feet: person's height, only feet part
    :param inches: person's height, only inches part
    :returns person's BMI
    '''

    weight = float(weight)*0.453592 # pounds to kg
    height = float(feet)*0.3048 + float(inches)*0.0254 #feet/inches to m
    return weight/height**2

# ------------------------------------------------------------------------------
#       DATA CLEANING
# ------------------------------------------------------------------------------
