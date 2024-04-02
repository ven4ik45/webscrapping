import bs4
import requests
import json
from fake_headers import Headers


def get_headers():
    return Headers(os='win', browser='chrome').generate()


url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
response = requests.get(url, headers=get_headers())
url_data = response.text
url_soup = bs4.BeautifulSoup(url_data, features='lxml')
vac_list = url_soup.find('main', class_='vacancy-serp-content')
vacancies = vac_list.find_all('div', class_='serp-item serp-item_link')

parsed_vacancies = []
for vac in vacancies:
    title_vacancy = vac.find('span', 'data-qa' == 'serp-item__title').text
    name_company = vac.find('a', class_='bloko-link bloko-link_kind-tertiary').find('span').text.replace(u'\xa0', ' ')
    info = vac.find('div', class_='vacancy-serp-item__info')
    city = vac.find(attrs={'class': ['bloko-text'], 'data-qa': 'vacancy-serp__vacancy-address'}).text
    salary = vac.find('span', class_='bloko-header-section-2')
    salary_text = ''
    if salary is not None:
        salary_text = salary.text.replace(u'\u202f', ' ')
    link = vac.find('a', class_='bloko-link')['href']

    parsed_vacancies.append(
        {
            'название вакансии': title_vacancy,
            'имя компании': name_company,
            'город': city,
            'вилка зп': salary_text,
            'ссылка': link
         }
    )

sorted_vacancies = []
for vacancy in parsed_vacancies:
    url_vac = vacancy['ссылка']
    s_response = requests.get(url_vac, headers=get_headers())

    s_resp_data = s_response.text
    s_soup = bs4.BeautifulSoup(s_resp_data, features='lxml')
    vacancy_description_list = s_soup.find_all(class_='bloko-column bloko-column_xs-4 bloko-column_s-8 '
                                                      'bloko-column_m-12 bloko-column_l-10')
    desc = ''
    for i in vacancy_description_list:
        description_vacancy = i.find(class_='vacancy-description')
        if description_vacancy is not None:
            desc = description_vacancy.text
    description = s_soup.find(attrs={'class': ['g-user-content'], 'data-qa': 'vacancy-description'})
    words = ['Django', 'Flask']
    for word in words:
        if word.lower() in desc.lower():
            sorted_vacancies.append(vacancy)

with open('vacancies.json', 'w') as f:
    json.dump(sorted_vacancies, f, indent=4, sort_keys=True, ensure_ascii=False)
