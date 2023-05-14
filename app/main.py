import requests
from bs4 import BeautifulSoup
import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import http.client, urllib
# 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


from .config import settings
from . import database, models, schemas


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/apply')
def apply_for_job(db: Session = Depends(database.get_db)):
    # URL of the website to scrape
    url = 'https://agropraktika.eu/vacancies?l=united-kingdom'
 
    # Make a GET to the website and parse the HTML using Beautiful Soup
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')

    # Find all the job vacancies on the page
    vacancies = soup.find_all('li', class_='border-b-2 p-8 sm:flex hover:bg-white')
    
    # Loop through the vacancies and check if we have already seen them
    for vacancy in vacancies:
        vacancy_div = vacancy.find('div', class_='lg:flex grow justify-between items-center')
        vacancy_name = vacancy.find('h4', class_='mb-2').text
        vacancy_link = vacancy_div.div.a['href']
        vacancy_start_date = vacancy.find('div', class_='italic text-gray-400').text

        found_vacancy = db.query(models.Vacancy).filter(models.Vacancy.name == vacancy_name, models.Vacancy.link == vacancy_link, models.Vacancy.start == vacancy_start_date).first()
        
        # If we haven't seen this vacancy before, add it to the list of seen vacancies and notify ourselves
        if not found_vacancy:
            new_vacancy = models.Vacancy(name=vacancy_name, link=vacancy_link, start=vacancy_start_date)
            db.add(new_vacancy)
            db.commit()
            db.refresh(new_vacancy)
            print(f"new vacancy found: {new_vacancy.name} ({new_vacancy.link})")


            # Automated apply for job
            # Create a new instance of the Chrome driver
            options = Options()
            options.binary_location = '/app/.apt/usr/bin/google-chrome-stable'
            driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=options)

            # Navigate to the Agropraktika website
            driver.get("https://agropraktika.eu/")

            # Find the login and password input fields and fill them in
            email_input = driver.find_element(By.NAME, "email")
            email_input.send_keys(settings.agro_email)

            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(settings.agro_password)


            # Submit the form by clicking the login button
            login_btn = driver.find_element(By.ID, "ugo1")
            login_btn.click()


            # Wait for the page to load after login and get the current URL
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.ID, "photo")))

            # Check if the current URL redirected to url
            if driver.current_url == "https://agropraktika.eu/user/profile":
                print("Login successful!")

                # Redirect to new vacancy's link
                driver.get(new_vacancy.link)

                # wait for the page load
                wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Подать заявку')]")))

                # tap to apply button
                apply_button = driver.find_element(By.XPATH, "//button[contains(text(),'Подать заявку')]")
                apply_button.click()
            else:
                print("Couldn't login")

            driver.quit()


            #  using pushover to send notification
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
            "token": f"{settings.api_token}",
            "user": f"{settings.user_key}",
            "message": f"Быстрее подай заявку \n название вакансии: {new_vacancy.name} \n начинается: {new_vacancy.start} \n ({new_vacancy.link})",
            "sound": "my-custom",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

     
    return {"message": "Website scraped successfully!"}



@app.get('/apply_local_pc')
def apply_for_job_using_local_pc(db: Session = Depends(database.get_db)):
    # URL of the website to scrape
    url = 'https://agropraktika.eu/vacancies?l=united-kingdom'
 
    # Make a GET to the website and parse the HTML using Beautiful Soup
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')

    # Find all the job vacancies on the page
    vacancies = soup.find_all('li', class_='border-b-2 p-8 sm:flex hover:bg-white')
    
    # Loop through the vacancies and check if we have already seen them
    for vacancy in vacancies:
        vacancy_div = vacancy.find('div', class_='lg:flex grow justify-between items-center')
        vacancy_name = vacancy.find('h4', class_='mb-2').text
        vacancy_link = vacancy_div.div.a['href']
        vacancy_start_date = vacancy.find('div', class_='italic text-gray-400').text

        found_vacancy = db.query(models.Vacancy).filter(models.Vacancy.name == vacancy_name, models.Vacancy.link == vacancy_link, models.Vacancy.start == vacancy_start_date).first()
        
        # If we haven't seen this vacancy before, add it to the list of seen vacancies and notify ourselves
        if not found_vacancy:
            new_vacancy = models.Vacancy(name=vacancy_name, link=vacancy_link, start=vacancy_start_date)
            db.add(new_vacancy)
            db.commit()
            db.refresh(new_vacancy)
            print(f"new vacancy found: {new_vacancy.name} ({new_vacancy.link})")


            # Automating click button for me using selenium.
            # Path to chromedriver executable
            chromedriver_path = "C:\Program Files\chromedriver\chromedriver_win32\chromedriver"

            # Create a new instance of the Chrome driver
            driver = webdriver.Chrome(executable_path=chromedriver_path) 

            # Navigate to the Agropraktika website
            driver.get("https://agropraktika.eu/")

            # Find the login and password input fields and fill them in
            email_input = driver.find_element(By.NAME, "email")
            email_input.send_keys(settings.agro_email)

            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(settings.agro_password)


            # Submit the form by clicking the login button
            login_btn = driver.find_element(By.ID, "ugo1")
            login_btn.click()


            # Wait for the page to load after login and get the current URL
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.ID, "photo")))

            # Check if the current URL redirected to url
            if driver.current_url == "https://agropraktika.eu/user/profile":
                print("Login successful!")

                # Redirect to new vacancy's link
                driver.get(new_vacancy.link)

                # wait for the page load
                wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Подать заявку')]")))

                # tap to apply button
                apply_button = driver.find_element(By.XPATH, "//button[contains(text(),'Подать заявку')]")
                apply_button.click()

            else:
                print("Login Error")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Error accured while trying to use automated script')

            driver.quit()


            #  using pushover to send notification
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
            "token": f"{settings.api_token}",
            "user": f"{settings.user_key}",
            "message": f"Быстрее подай заявку \n название вакансии: {new_vacancy.name} \n начинается: {new_vacancy.start} \n ({new_vacancy.link})",
            "sound": "my-custom",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

     
    return {"message": "Website scraped successfully!"}



@app.get('/find')
def notify(db: Session = Depends(database.get_db)):

     # TODO - for check only, delete if needed
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
    "token": f"{settings.api_token}",
    "user": f"{settings.user_key}",
    "message": f"Это просто проверка, Алибек Актай это просто проверка",
    "sound": "my-custom",
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()


    # URL of the website to scrape
    url = 'https://agropraktika.eu/vacancies?l=united-kingdom'
 
    # Make a GET to the website and parse the HTML using Beautiful Soup
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')

    # Find all the job vacancies on the page
    vacancies = soup.find_all('li', class_='border-b-2 p-8 sm:flex hover:bg-white')
    
    # Loop through the vacancies and check if we have already seen them
    for vacancy in vacancies:
        vacancy_div = vacancy.find('div', class_='lg:flex grow justify-between items-center')
        vacancy_name = vacancy.find('h4', class_='mb-2').text
        vacancy_link = vacancy_div.div.a['href']
        vacancy_start_date = vacancy.find('div', class_='italic text-gray-400').text

        found_vacancy = db.query(models.Vacancy).filter(models.Vacancy.name == vacancy_name, models.Vacancy.link == vacancy_link, models.Vacancy.start == vacancy_start_date).first()
        
        # If we haven't seen this vacancy before, add it to the list of seen vacancies and notify ourselves
        if not found_vacancy:
            new_vacancy = models.Vacancy(name=vacancy_name, link=vacancy_link, start=vacancy_start_date)
            db.add(new_vacancy)
            db.commit()
            db.refresh(new_vacancy)
            print(f"new vacancy found: {new_vacancy.name} ({new_vacancy.link})")


            #  using pushover to send notification
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
            "token": f"{settings.api_token}",
            "user": f"{settings.user_key}",
            "message": f"Быстрее подай заявку \n название вакансии: {new_vacancy.name} \n начинается: {new_vacancy.start} \n ({new_vacancy.link})",
            "sound": "my-custom",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

            
    return {"message": "Website scraped successfully!"}

 
@app.get("/")
def root():
    return {"message": "HEllO WORLD CI/CD here"}
