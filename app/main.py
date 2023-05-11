import requests
from bs4 import BeautifulSoup
import time
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pushover import PushoverClient

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


@app.get('/find')
def notify(db: Session = Depends(database.get_db)):
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
            client = PushoverClient(f"{settings.user_key}", api_token=f"{settings.api_token}")
            # client.send_message(
            # message=f"Быстрее подай заявку \n название вакансии: {new_vacancy.name} \n начинается: {new_vacancy.start}",
            # title=f"Новая Вакансия!!!",
            # url=f"{new_vacancy.link}",
            # url_title=">>> Нажми сюда для перехода на сайт <<<"
            # )

            client.send_message(
            f"Быстрее подай заявку \n название вакансии: {new_vacancy.name} \n начинается: {new_vacancy.start} \n {new_vacancy.link}",
            title="Новая Вакансия!!!",
            priority=1,
            sound="siren",
            retry=30,
            expire=300
            )

    return {"message": "Website scraped successfully!"}

 
@app.get("/")
def root():
    return {"message": "HEllO WORLD CI/CD here"}
