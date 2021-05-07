from dbActions.getTables import get_abstract_and_descr_path
from helpers.saoSelector import rem, split_description
import os


def save_text_db_to_txt(con, filename_base = 'C:/Users/mrkol/Documents/myLog/dataset.txt'):
    # Берем тексты патентов из БД
    paths = get_abstract_and_descr_path(con)
    # Сохраняем в файлы для обучения модели
    for i, el in enumerate(paths):
        try:
            with open(filename_base, 'a', encoding="utf-8") as file:
                if el[0]:
                    if os.path.isfile(el[0]):
                        with open(str(el[0]), 'r', encoding='utf8') as f:
                            file.write(f.read())
                if el[1]:
                    if os.path.isfile(el[1]):
                        with open(str(el[1]), 'r', encoding='utf8') as f:
                            file.write(f.read())
        except EnvironmentError:
            print("Ошибка при записи в файл:" + filename_base)
    return filename_base


def save_text_db_to_txt2(con, filename_base = 'C:/Users/mrkol/Documents/myLog/dataset.txt'):
    # Берем тексты патентов из БД
    paths = get_abstract_and_descr_path(con)
    # Сохраняем в файлы для обучения модели
    for i, el in enumerate(paths):
        try:
            with open(filename_base, 'a', encoding="utf-8") as file:
                if el[0]:
                    if os.path.isfile(el[0]):
                        with open(str(el[0]), 'r', encoding='utf8') as f:
                            text = f.read()
                            text = rem(text)
                            file.write(text)
                if el[1]:
                    if os.path.isfile(el[1]):
                        with open(str(el[1]), 'r', encoding='utf8') as f:
                            text = f.read()
                            text = split_description(text)
                            text = rem(text)
                            file.write(text)
        except EnvironmentError:
            print("Ошибка при записи в файл:" + filename_base)
    return filename_base