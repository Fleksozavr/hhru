import os
import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv


HH_TITLE = "HeadHunter Moscow"
SJ_TITLE = "SuperJob Moscow"


def get_vacancies_hh(language, page=0):
    area = 1
    url = 'https://api.hh.ru/vacancies'
    params = {'text': language, 'area': area, 'page': page}

    response = requests.get(url, params=params)
    return response.json()


def get_stat_hh():
    vacancies_by_language = {}
    languages = [
        "Python", "Java", "Javascript", "Ruby",
        "PHP", "C++", "C#", "C", "Go",
        "Shell"
    ]
    for language in languages:
        vacancies_processed = 0
        salary_by_vacancies = []
        for page in count(0):
            vacancies = get_vacancies_hh(language, page=page)
            if vacancies and page >= vacancies["pages"] - 1:
                break
            for vacancy in vacancies['items']:
                salary = vacancy.get('salary')
                if salary and salary['currency'] == 'RUR':
                    predicted_salary = predict_rub_salary(
                        vacancy['salary'].get('from'),
                        vacancy['salary'].get('to'))
                    if predicted_salary:
                        salary_by_vacancies_hh.append(predicted_salary)
        total_vacancies = vacancies['found']
        average_salary = None
        if salary_by_vacancies_hh:
            average_salary = int(
                sum(salary_by_vacancies_hh) / len(salary_by_vacancies_hh))

        vacancies_by_language[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': len(salary_by_vacancies_hh),
            'average_salary': average_salary
        }
    return vacancies_by_language


def predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        expected_salary = int((salary_to + salary_from) / 2)
    elif salary_to:
        expected_salary = int(salary_to * 1.2)
    elif salary_from:
        expected_salary = int(salary_from * 0.8)
    else:
        expected_salary = None
    return expected_salary


def get_vacancies_sj(key, language="Python", page=0):
    period_in_days = 30
    catalogue_count = 48
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {"X-Api-App-Id": key}

    params = {
        "town": "Moscow",
        "period": period_in_days,
        "catalogues": catalogue_count,
        "keyword": language,
        "page": page
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_statistic_vacancies_sj(sj_token):
    vacancies_by_language = {}
    languages = [
        "Python", "Java", "Javascript", "Ruby",
        "PHP", "C++", "C#", "C", "Go",
        "Shell"
    ]
    for language in languages:
        salary_by_vacancies = []
        for page in count(0, 1):
            vacancies = get_vacancies_sj(language, page=page)
            if not vacancies['objects']:
                break
    
            for vacancy in vacancies['objects']:
                predicted_salary = predict_rub_salary(vacancy["payment_from"],
                                                      vacancy["payment_to"])
                if predicted_salary:
                    salary_by_vacancies_sj.append(predicted_salary)
        total_vacancies = vacancies['total']
        average_salary = None
        if salary_by_vacancies_sj:
            average_salary = int(
                sum(salary_by_vacancies_sj) / len(salary_by_vacancies_sj))
    
        vacancies_by_language[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': len(salary_by_vacancies_sj),
            'average_salary': average_salary
        }
    
    return vacancies_by_language


def create_table(title, statistics):
    table_contents = [[
        "Язык программирования", "Вакансий найдено", "Вакансий обработано",
        "Средняя зарплата"
    ]]
    for language, vacancies in statistics.items():
        table_contents.append([
            language, vacancies["vacancies_found"],
            vacancies["vacancies_processed"], vacancies["average_salary"]
        ])
    table = AsciiTable(table_contents, title)
    return table.table


def main():
    load_dotenv()

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print('Ошибка при получении ответа:', err)

    sj_token = os.getenv('SJ_TOKEN')
    hh_table = create_table(HH_TITLE, get_stat_hh())

    superjob_table = create_table(SJ_TITLE,
                                  get_statistic_vacancies_sj(sj_token))
    print(f"{superjob_table}\n{hh_table}")


if __name__ == "__main__":
    main()
