from bs4 import BeautifulSoup as BS
import uuid
import multiprocessing
import time
import os
import sys
from modules.models.parsedPatent import ParsedPatent
from modules.models.patent import Patent
from modules.helpers.dbHelper import create_connection, create_tables
from modules.dbActions.insertTables import insert_patent


def save_to_file(path: str, patent_title: str, ext: str, data: str):
    if not os.path.isdir(path):
        os.makedirs(path)
    filePath = path + "/" + patent_title + ext
    try:
        with open(filePath, 'w', encoding="utf-8") as file:
            file.write(data.strip())
    except EnvironmentError:
        print("Ошибка при записи в файл:" + filePath)
    return filePath


def get_text_field(parent_name, field_name: str):
    field = parent_name.find(field_name)
    try:
        if field:
            text_field = field.text.strip()
            return text_field
        else:
            return None
    except AttributeError:
        print("Ошибка при обращении к полю" + field_name)
        return None


def splitter(text: str):
    splitter = '<?xml version="1.0" encoding="UTF-8"?>'
    splitted = text.split(splitter)
    splitted = list(filter(lambda x: x != '', splitted))
    return splitted


def parse_XML(text):
    patent_reference = ''
    try:
        soup = BS(text, 'lxml')
        app_ref_tmp = soup.find("application-reference")
        if app_ref_tmp:
            application_reference = {'doc_number': get_text_field(app_ref_tmp, "doc-number"),
                                     'country': get_text_field(app_ref_tmp, "country"),
                                     'date': get_text_field(app_ref_tmp, "date")}
        else:
            application_reference = None

        pub_ref_tmp = soup.find("publication-reference")
        if pub_ref_tmp:
            publication_reference = {'doc-number': get_text_field(pub_ref_tmp, "doc-number"),
                                     'country': get_text_field(pub_ref_tmp, "country"),
                                     'date': get_text_field(pub_ref_tmp, "date"),
                                     'kind': get_text_field(pub_ref_tmp, "kind")}
            patent_reference = publication_reference["country"] + publication_reference["doc-number"] \
                               + publication_reference["kind"]
        else:
            publication_reference = None

        invention_title = soup.find("invention-title")
        if invention_title:
            title = invention_title.text.strip()
        else:
            title = None

        inventors = []
        applicants = soup.find("applicants")
        if applicants:
            for content in applicants.contents:
                if content != '\n':
                    inventor = {'first-name': get_text_field(content, "first-name"),
                                'last-name': get_text_field(content, "last-name")}
                    inventors.append(inventor)

        assignee_tmp = soup.find("assignee")
        assignee = None
        if assignee_tmp:
            assignee = get_text_field(assignee_tmp, "orgname")

        abstract_tmp = soup.find("abstract")
        if abstract_tmp:
            abstract = abstract_tmp.text
        else:
            abstract = None

        description_tmp = soup.find("description")
        if description_tmp:
            description = description_tmp.text
        else:
            description = None

        claims = [x.text for x in soup.findAll("claim-text")]

        classification_type = None
        main_classification = None
        # только ipc
        for classification in ("classification-ipc", "classification-ipcr", "classification-locarno"):
            tag = soup.find(classification)
            if tag:
                classification_type = classification
                if classification == "classification-ipcr":
                    section_tag = tag.find("section")
                    class_tag = tag.find("class")
                    subclass_tag = tag.find("subclass")

                    if section_tag and class_tag and subclass_tag:
                        patent_section = section_tag.text.strip()
                        patent_class = class_tag.text.strip()
                        patent_subclass = subclass_tag.text.strip()

                        main_classification = f"{patent_section} {patent_class} {patent_subclass}"
                        break
                    else:
                        continue
                else:
                    main_classification_tag = tag.find("main-classification")
                    if main_classification_tag:
                        main_classification = main_classification_tag.text.strip()
                        break
                    else:
                        continue

        return ParsedPatent(application_reference, publication_reference, str(classification_type),
                            str(main_classification), title, inventors, abstract, description, claims, assignee)

    except Exception:
        print("Ошибка при парсинге патента " + patent_reference)
        return None


def save_patent(patent: ParsedPatent, path: str):
    result = {}
    filename = patent.publication_reference["country"] + patent.publication_reference["doc-number"] \
               + patent.publication_reference["kind"]

    result['abstractPath'] = None
    result['descriptionPath'] = None
    result['claimsPath'] = None
    if patent.abstract:
        abstract_path = save_to_file(path + '/abstract', filename,
                                     '.txt', patent.abstract)
        result['abstractPath'] = abstract_path
    if patent.description:
        description_path = save_to_file(path + '/description', filename,
                                        '.txt', patent.description)
        result['descriptionPath'] = description_path
    if patent.claims:
        claims_path = save_to_file(path + '/claims', filename,
                                   '.txt', '\n'.join(patent.claims))
        result['claimsPath'] = claims_path
    return result


def map_patent(parsed_patent: ParsedPatent, paths):
    patent_reference = parsed_patent.publication_reference["country"] + parsed_patent.publication_reference[
        "doc-number"] \
                       + parsed_patent.publication_reference["kind"]
    if parsed_patent.inventors and len(parsed_patent.inventors) > 0:
        inventors = ','.join(str(e['first-name']) + " " + str(e['last-name']) for e in parsed_patent.inventors)
    else:
        inventors = ""
    return Patent(str(uuid.uuid4()), patent_reference, parsed_patent.main_classification_type,
                  parsed_patent.main_classification, parsed_patent.title, inventors, paths['abstractPath'],
                  paths['descriptionPath'], paths['claimsPath'], parsed_patent.assignee)


# Функция для обработки файлов
def process_files(files, path):
    con = create_connection("diplom", "postgres", "postgres", "localhost", "5432")
    for file in files:
        start_time = time.time()
        with open(file) as f:
            xml = f.read()
        splitted_xml = splitter(xml)
        print(len(splitted_xml))
        iter = 0
        while iter < len(splitted_xml):
            parsed_patent = parse_XML(splitted_xml[iter])
            if not parsed_patent:
                continue
            save_files = save_patent(parsed_patent, path)
            patent = map_patent(parsed_patent, save_files)
            insert_patent(con, patent)
            iter += 1
        end_time = time.time()
        print(f"Finished processing {file}, time: {end_time-start_time}")
    con.close()


def main():
    total_time_start = time.time()
    parallel_processes_count = multiprocessing.cpu_count() - 2
    path = 'C:/Users/mrkol/Documents'
    files = os.listdir(path + '/patents/unpack')
    names = list(map(lambda x: path + '/patents/unpack/' + x, files))
    filenames_list = []
    i = 0

    con = create_connection("diplom", "postgres", "postgres", "localhost", "5432")
    create_tables(con)
    con.close()

    # Проверка существования
    while i < len(names):
        if os.path.isdir(names[i]):
            names += list(map(lambda x: f"{names[i]}/{x}", os.listdir(names[i])))
        i += 1

    filenames = [name for name in names if os.path.isfile(name)]

    for i in range(parallel_processes_count):
        start = i * len(filenames) / parallel_processes_count
        end = (i + 1) * len(filenames) / parallel_processes_count
        if i == parallel_processes_count:
            end = len(filenames)
        start = int(start)
        end = int(end)
        if len(filenames[start:end]) > 0:
            filenames_list.append(filenames[start:end])

    filenames_list = filenames_list

    processes = []

    for sublist in filenames_list:
        p = multiprocessing.Process(target=process_files, args=(sublist, path))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    total_time_end = time.time()

    print(f"\nDone in {total_time_end - total_time_start}")


if __name__ == '__main__':
    main()
