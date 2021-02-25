from bs4 import BeautifulSoup as BS
from models.patent import Patent


def splitter(text: str):
    splitter = '<?xml version="1.0" encoding="UTF-8"?>'
    splitted = text.split(splitter)
    splitted = list(filter(lambda x: x != '', splitted))
    return splitted


def parse_XML(splitted_xml):
    patents = []
    for number, text in enumerate(splitted_xml):
        soup = BS(text, 'lxml')
        app_ref_tmp = soup.find("application-reference")
        if app_ref_tmp:
            application_reference = {'doc_number': app_ref_tmp.find("doc-number").text,
                                     'country': app_ref_tmp.find("country").text,
                                     'date': app_ref_tmp.find("date").text}
        else:
            application_reference = None

        pub_ref_tmp = soup.find("publication-reference")
        if pub_ref_tmp:
            publication_reference = {'doc-number': pub_ref_tmp.find("doc-number").text,
                                     'country': pub_ref_tmp.find("country").text,
                                     'date': pub_ref_tmp.find("date").text}
        else:
            publication_reference = None

        abstract_tmp = soup.find("abstract")
        if abstract_tmp:
            abstract = abstract_tmp.text

        description_tmp = soup.find("description")
        if description_tmp:
            description = description_tmp.text

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

        patents.append(Patent(application_reference, publication_reference, str(classification_type),
                              str(main_classification), abstract, description, claims))

    return patents


def main():
    file = 'C:/Users/mrkol/Documents/patents/unpack/ipg100105.xml'
    with open(file) as f:
        xml = f.read()
    splitted_xml = splitter(xml)
    patents = parse_XML(splitted_xml)
    for p in patents:
        print(p.description)


if __name__ == '__main__':
    main()
