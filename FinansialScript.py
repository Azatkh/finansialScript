import requests
from pprint import pprint
from bs4 import BeautifulSoup
import operator

class Company():

    def __init__(self, name, points, p, ev, s, e, p_e, p_s, p_b, ev_ebitda, rent_ebitda, debt_ebitda, branch):
        self.branch = branch    #отрасль
        self.name = name        #имя
        self.points = points    #Набранные очки
        self.p = p              #капитализация
        self.ev = ev            #стоимость компании
        self.s = s              #выручка
        self.e = e              #прибыль
        self.p_e = p_e
        self.p_s = p_s
        self.p_b = p_b
        self.ev_ebitda = ev_ebitda
        self.rent_ebitda = rent_ebitda
        self.debt_ebitda = debt_ebitda

def transformation(val):
    if val == '' or val == ' ':
        return 0.0
    else:
        if val[-1] == '%':
            return float(val.split('%')[0])
        else:
            return float( val.replace(' ', '') )

def get_sectors_companies(id):
    url = 'https://smart-lab.ru/q/shares_fundamental2/?sector_id%5B%5D=' + id
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    r = requests.get(url, headers);
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find_all('table', class_='simple-little-table little trades-table')
    sector_companies = list()
    if len(table) != 0:
        sector_table = table[0].contents
        for i in range(2, len(sector_table)):
            if sector_table[i] != '\n':
                sector_companies.append(sector_table[i].contents[3].text)
    return sector_companies

def get_all_companies():

    url = 'https://smart-lab.ru/q/shares_fundamental/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.text, 'lxml')
    tables = soup.find_all('table', class_='simple-little-table little trades-table') #получаем таблицы
    table_all_company = tables[0].contents
    company_arr = list()
    for i in range(3, len(table_all_company)):
        if table_all_company[i] != '\n':
            table1 = table_all_company[i].contents
            company_name = table1[3].a.text
            p = transformation(table1[9].text)
            ev = transformation(table1[11].text)
            s = transformation(table1[13].text)
            e = transformation(table1[15].text)
            p_e = transformation(table1[23].text)
            p_s = transformation(table1[25].text)
            p_b = transformation(table1[27].text)
            ev_ebitda = transformation(table1[29].text)
            rent_ebitda = transformation(table1[31].text)
            debt_ebitda = transformation(table1[33].text)
            points = 0
            #отсеивание компаний с непонятными данными
            if p != 0.0 and ev != 0.0 and s != 0.0 and e != 0.0 and p_e != 0.0 and p_s != 0.0 and p_b != 0.0 and ev_ebitda != 0.0 and rent_ebitda != 0.0 and debt_ebitda != 0.0:
                company = Company(company_name, points, p, ev, s, e, p_e, p_s, p_b, ev_ebitda, rent_ebitda, debt_ebitda, '')
                company_arr.append(company)

    sectors = soup.find( id = "sector_id" )
    sectors_arr = dict()
    for i in sectors:
        if i != '\n':
            sectors_arr[i['value']] = i.text

    for key, value in sectors_arr.items():                  #key - номер в форме на сайте, value - название сектора
        company_for_sector = get_sectors_companies(key)
        if len(company_for_sector) > 0:
            for i in company_arr:
                for j in company_for_sector:
                    if i.name == j:
                        i.branch += value
                        break


    return company_arr

def comparison(coampanies): #на вход принимает массив с объектами
    comparison_arr = list()
    for i in coampanies:
        #оценка p/e
        if i.p_e < 0.0:
            i.points += 0.0
        elif 0.0 < i.p_e <= 1.0:
            i.points += 1.0
        else:
            i.points += 1/i.p_e

        #оценка p/s
        if 0.0 < i.p_s < 1.0:
            i.points += 1.0
        elif 1.0 <= i.p_s < 2.0:
            i.points += 0.5
        else:
            i.points += 1/i.p_s

        #оценка p/b
        if i.p_b < 0:
            i.points += 0.0
        elif 0.0 < i.p_b <= 1.0:
            i.points += 1.0
        else:
            i.points += 1/i.p_b

        #оценка ev_ebitda
        if i.ev_ebitda < 0:
            i.points += 0.0
        else:
            i.points += 1/i.ev_ebitda

        #оценка rent_ebitda
        if i.rent_ebitda < 0.0:
            i.points += 0.0
        else:
            i.points += i.rent_ebitda/100

        #оценка debt_ebitda
        if i.debt_ebitda < 0.0 or i.debt_ebitda > 4.0:
            i.points += 0.0
        elif  0.0 < i.debt_ebitda < 2.0:
            i.points += 1
        elif 2.0 < i.debt_ebitda < 4.0:
            i.points += 0.5

if __name__ == "__main__":

    comp = get_all_companies()
    comparison(comp)
    sectors = set()
    for i in comp:
        sectors.add(i.branch)   #набираем имена всех существующих секторов
    text_for_write = ''
    for i in sectors:
        text_for_write += "\n SECTOR: {}----------------------------------\n\n".format(i)  #добавляем в файл имя сектора
        buff_dict = dict()  # промежуточный словарь для хранения компаний одного сектора
        for j in comp:
            if j.branch == i:
                buff_dict[j.name] = j.points    #сформировали словарь ключ значение для компаний одного сектора

        dict_for_write = sorted(buff_dict.items(), key = operator.itemgetter(1), reverse=True) #массив для отсортированных компаний по набранным баллам
        for k in dict_for_write:
            text_for_write += "---{} - {}\n".format(k[0], k[1])

    with open('rezult.txt', 'w') as f:
        f.write(text_for_write)