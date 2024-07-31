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

#ChromeDriverManager().install()

def crawl_links(url) -> set:
    def run_driver():
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        #chrome_options.add_argument("--headless")  
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url) #https://divar.ir/s/tehran/rent-apartment?sort=sort_date # https://divar.ir/s/tehran/rent-apartment/tehran-zanjan?sort=sort_date
        time.sleep(10)
        return driver
    
    def get_cases(driver: webdriver.Chrome):
        def scroll(driver):
            driver.execute_script("window.scrollBy(0, 500);")
        
        def height(driver):
            return driver.execute_script("return document.body.scrollHeight")
        
        def check_for_error(driver):
            driver.find_element(By.XPATH("/html/body/div/div[1]/div/main/div/div[2]/div/button")).click()
            time.sleep(20)
            driver.find_element(By.XPATH("/html/body/div/div[1]/div/main/div/div[2]/div/button"))
        cases = set()  
        initial_height = height(driver)
        j = 0
        i = 1
        height_check = 0
        pbar = tqdm(j+1)
        while True:
            html = driver.page_source
            soup = BeautifulSoup(html, features="html.parser")
            caselist = soup.find_all("div", attrs= {"class": "post-list__widget-col-a3fe3"})
            for case in caselist:
                #print(case)
                cases.add(case)

            scroll(driver)
            i += 1
            j += 1
            pbar.update(1)
            time.sleep(5)

            current_height = height(driver)
            if current_height == initial_height:
                if i % 15 == 0:
                    #try:
                        check_for_error(driver)
                        print("reload button appeared")
                        break
                    #except: 
                    #    time.sleep(5)
                    #    current_height = height(driver)
                    #    if current_height == initial_height:
                    #        print("height didnt change")
                    #        height_check += 1
                    #        if height_check == 3:
                    #            break        
                    #    else:
                    #        initial_height = current_height
                    #        i = 1
                               
            else:    
                initial_height = current_height
                i = 1
            
        driver.quit()
        
        return cases
    
    #try:
    driver = run_driver()
    return get_cases(driver)
    #except:
    #    return crawl_links(url)

def get_data(cases) -> pd.DataFrame:
    
    def get_values(case):
        def get_url(case):
            #print()
            #print("https://divar.ir" + case.a.get("href"))
            return "https://divar.ir" + case.a.get("href")
        
        def get_soup(url):
            time.sleep(3)
            return BeautifulSoup(session.get(url, timeout= 20).text, features="html.parser")
            
        def get_title(soup):
            return soup.find("div", attrs= {"class": "kt-page-title__title kt-page-title__title--responsive-sized"}).text
        
        def get_zone(soup):
            return soup.find("div", attrs= {"class": "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized"}).text
        
        def get_description(soup):
            return soup.find("p", attrs= {"class": "kt-description-row__text kt-description-row__text--primary"}).text
        
        def get_area_year_rooms(soup):
            area_built_rooms = soup.find_all("tr", attrs= {"class": "kt-group-row__data-row"})
            area = area_built_rooms[0].find_all('td')[0].text
            built = area_built_rooms[0].find_all('td')[1].text
            rooms = area_built_rooms[0].find_all('td')[2].text
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
        #try:
        url = get_url(case)
        #except:
        #    return 0
        try:
            soup = get_soup(url)
            title = get_title(soup)
        except:
            time.sleep(20)
            try:
                soup = get_soup(url)
                title = get_title(soup)
            except:
                return 0
        zone = get_zone(soup)
        description = get_description(soup)
        area, built, rooms = get_area_year_rooms(soup)
        rent_pre_dict = get_rent_costs(soup)
        level = get_level(soup)
        elevator, parking, warehouse = get_elev_park_ware(soup)
        return title, description, zone, area, built, rooms, rent_pre_dict, level, elevator, parking, warehouse, url
    
    df = pd.DataFrame(columns = ["title", "description", "zone", "area", "year", "number of rooms", "pish1", "rent1", "pish2", "rent2", "level", "elevator", "parking", "warehouse", "url"])
    for case in tqdm(cases):
        #time.sleep(2)
        try:
            title, description, zone, area, built, rooms, rent_pre_dict, level, elevator, parking, warehouse, url = get_values(case)
            df.loc[len(df)] = {
                "title": title,\
                "description": description,\
                "area": area,\
                "zone": zone,\
                "year": built,\
                "number of rooms": rooms,\
                "pish1": rent_pre_dict["pish1"],\
                "rent1": rent_pre_dict["rent1"],\
                "pish2": rent_pre_dict["pish2"],\
                "rent2": rent_pre_dict["rent2"],\
                "level": level,\
                "elevator": elevator,\
                "parking": parking,\
                "warehouse": warehouse,\
                "url": url
                }
        except:
            pass
    return df

def clean_data(df):
    persian_to_western = {
                        "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
                        "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
                        }
    free = ["مجانی", "اجاره رایگان", "توافقی"]
    no_rooms = "بدون اتاق"
    for i in df.index:
        if df.loc[i, "year"][0] == 'ق':
            df.loc[i, "year"] = 1365
        try:
            df.loc[i, "zone"] = df.loc[i, "zone"].split("،")[1].strip()
        except:
            df.loc[i, "zone"] = df.loc[i, "zone"].split(" در ")[1].strip()
        for column in ["area", "year", "number of rooms", "pish1", "rent1", "pish2", "rent2"]:
            try:
                df.loc[i, column] = df.loc[i, column].replace("٬", "")
                for persian, western in persian_to_western.items():
                    df.loc[i, column] = df.loc[i, column].replace(persian, western)
                splitted = df.loc[i, column].split(" ")
                if len(splitted) > 1:
                    if splitted[1] == "تومان":
                        df.loc[i, column] = float(splitted[0])
                    elif splitted[1] == "میلیون":
                        df.loc[i, column] = float(splitted[0]) * 1000000
                    elif splitted[1] == "هزار":
                        df.loc[i, column] = float(splitted[0]) * 1000
                    elif splitted[1] == "میلیارد":
                        df.loc[i, column] = float(splitted[0]) * 1000000000
                if df.loc[i, column] in free:
                    df.loc[i, column] = 0
                if df.loc[i, column] == no_rooms:
                    df.loc[i, column] = 0    
            except:
                pass
        try:
            df.loc[i, "level"] = int(df.loc[i, "level"][0])
        except:
            df.loc[i, "level"] = 0
    return df

#clean_data(get_data(crawl_links())).to_excel("cases2.xlsx")