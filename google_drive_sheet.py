# -*- coding: utf-8 -*-

import os
import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import var
import var_price
import errors_type

#Название Гугл-таблицы
google_json = var_price.gs_json #имя json-файла от GoogleAPI
PRICE_TITLE = var_price.file_title
CREDENTIALS_FILE = os.path.join(os.getcwd(), google_json)

SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive.file'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(credentials)

#Search for sheet. Поиск по листу: здесь по 7-значному артикулу
def find_by_sheet(value_for_search):
    sheet_title = var_price.sheet_1_title  # Имя Лист excel с которым работаем
    sheet = client.open(PRICE_TITLE).worksheet(sheet_title)
    try:
        amount_re = re.compile(value_for_search)
        cell = sheet.find(amount_re)

        #Берем значения со всей строки по найденной ячейке
        row_by_cell = sheet.row_values(cell.row)
        #Преобразуем результат в читабельный вид
        # value_from_row = '\nНазвание: ' + row_by_cell[1] + '\nАртикул: ' + row_by_cell[2] + '\nЦена: ' + row_by_cell[3]
        value_from_row = [row_by_cell[1], row_by_cell[2],  row_by_cell[3]]
    except gspread.exceptions.CellNotFound:
        #Текст ошибки, если ячейка не наййдена
        value_from_row = errors_type.G01

    return value_from_row

#Get value from range. Получение значений из диапазона ячеек.
def get_all_ranks():
    sheet_title = var_price.sheet_0_title   #Имя Лист excel с которым работаем
    sheet_rank = client.open(PRICE_TITLE).worksheet(sheet_title)   #Подключаемся к нашей Гугл-таблице
    rank_count = sheet_rank.acell('A2').value   #Берем число МАХ кол-ва строк - сидит в ячейке А2
    cell_max = int(rank_count) + 1
    range_rank_id = 'B2:B' + str(cell_max)  #Формируем диапазоны для выборки
    range_rank_title = 'C2:C' + str(cell_max)
    list_id = sheet_rank.range(range_rank_id)   #Массивы данных из выборки
    list_title = sheet_rank.range(range_rank_title)
    list_ranks = []
    for y in range(len(list_id)):
        value_1 = list_id[y].value
        value_2 = list_title[y].value
        list_ranks.append({
            'id': value_1,
            'title': value_2
        })
    return list_ranks

def get_cell_value(cell_id):
    sheet_title = var_price.sheet_0_title
    sheet_rank = client.open(PRICE_TITLE).worksheet(sheet_title)
    cell_value = str(sheet_rank.acell(cell_id).value)
    return cell_value
