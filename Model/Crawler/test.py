import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.remote_connection import LOGGER
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")
LOGGER.setLevel("ERROR")

def get_soup(url):
    return BeautifulSoup(session.get(url, timeout= 10).text, features="html.parser")
    
def get_title(soup):
    return soup.find("div", attrs= {"class": "kt-page-title__title kt-page-title__title--responsive-sized"}).text

def get_zone(soup):
    return soup.find("div", attrs= {"class": "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized"}).text

def get_description(soup):
    return soup.find("p", attrs= {"class": "kt-description-row__text kt-description-row__text--primary"}).text

def get_area_year_rooms(soup):
    area_built_rooms = soup.find_all("tr", attrs= {"class": "kt-group-row__data-row"})
    area = area_built_rooms[0].text
    built = area_built_rooms[1].text
    rooms = area_built_rooms[2].text
    return area, built, rooms

def get_rent_costs(soup):
    rent_pre = soup.find_all("div", attrs= {"class": "convert-slider__info kt-row"})
    if len(rent_pre) > 0:

        try:
            pish1 = rent_pre[0].find_all("div")[0].span.text
        except:
            pish1 = rent_pre[0].find_all("div")[0].text
        try:
            pish2 = rent_pre[0].find_all("div")[1].span.text
        except:
            pish2 = rent_pre[0].find_all("div")[1].text
        try:
            rent1 = rent_pre[1].find_all("div")[0].span.text
        except:
            rent1 = rent_pre[1].find_all("div")[0].text
        try:
            rent2 = rent_pre[1].find_all("div")[1].span.text
        except:
            rent2 = rent_pre[1].find_all("div")[1].text
        
        rent_pre = {"pish1": pish1, "rent1": rent1,\
                    "pish2": pish2, "rent2": rent2}
    else:
        rent_pre = soup.find_all("p", attrs= {"class": "kt-unexpandable-row__value"})
        rent_pre = {"pish1": rent_pre[0].text, "rent1": rent_pre[1].text,\
                    "pish2": np.nan, "rent2": np.nan}
    return rent_pre

def get_level(soup):
    for row in soup.find_all("div", attrs= {"class": "kt-base-row kt-base-row--large kt-unexpandable-row"}):
        if row.find("div", attrs= {"class": "kt-base-row__start kt-unexpandable-row__title-box"}).p.text == "طبقه":
            tabaghe = row.find("div", attrs= {"class": "kt-base-row__end kt-unexpandable-row__value-box"}).p.text
            break
    else:
        tabaghe = np.nan
    return tabaghe
def get_elev_park_ware(soup):
    epw = soup.find_all("tr", attrs= {"class": "kt-group-row__heading"})
    
    elevator = epw[-1].find_all('th')[0].get("class") == 'kt-group-row-item kt-group-row-item__header'
    parking = epw[-1].find_all('th')[1].get("class") == 'kt-group-row-item kt-group-row-item__header'
    warehouse = epw[-1].find_all('th')[2].get("class") == 'kt-group-row-item kt-group-row-item__header'
    return elevator, parking, warehouse

session = requests.Session()
url = "https://divar.ir/v/۸۵-متر-تک-واحدی-خ-ترکمنستان-زیتون/gZkKcC92"

soup = get_soup(url)
title = get_title(soup)

zone = get_zone(soup)
description = get_description(soup)
area, built, rooms = get_area_year_rooms(soup)
rent_pre_dict = get_rent_costs(soup)
level = get_level(soup)
elevator, parking, warehouse = get_elev_park_ware(soup)
print(title)
print(description)
print(area)
print(built)
print(rooms)
print(rent_pre_dict)
print(level)
print(elevator)
print(parking)
print(warehouse)
