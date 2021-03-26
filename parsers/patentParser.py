from bs4 import BeautifulSoup as BS
import os
from models.parsedPatent import ParsedPatent
from models.patent import Patent


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
                           str(main_classification), title, inventors, abstract, description, claims)

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
    patent_reference = parsed_patent.publication_reference["country"] + parsed_patent.publication_reference["doc-number"] \
                       + parsed_patent.publication_reference["kind"]
    if parsed_patent.inventors and len(parsed_patent.inventors) > 0:
        inventors = ','.join(str(e['first-name']) + " " + str(e['last-name']) for e in parsed_patent.inventors)
    else:
        inventors = ""
    return Patent(patent_reference, parsed_patent.main_classification_type,
                        parsed_patent.main_classification, parsed_patent.title, inventors, paths['abstractPath'],
                        paths['descriptionPath'], paths['claimsPath'])


def main():
    file = 'C:/Users/mrkol/Documents/patents/unpack/ipg100105.xml'
    path = 'C:/Users/mrkol/Documents'
    with open(file) as f:
        xml = f.read()
    splitted_xml = splitter(xml)
    print(len(splitted_xml))
    iter = 0
    while iter < len(splitted_xml):
        parsed_patent = parse_XML(splitted_xml[iter])
        save_files = save_patent(parsed_patent, path)
        patent = map_patent(parsed_patent, save_files)
        iter += 1
    print(patent.title)


if __name__ == '__main__':
    main()
