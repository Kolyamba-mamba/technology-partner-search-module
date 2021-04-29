import stanza
import os
import re
import uuid
from typing import List
from models.patent import Patent
from models.sao import Sao
from dbActions.getTables import get_count_table_rows, get_entities, get_cursor
from helpers.dbHelper import create_connection
from dbActions.insertTables import insert_sao
import psycopg2


def rem(text: str):
    sub_regex = re.sub(r"\([\w\W][^\)\(]+\)", "", text)
    return sub_regex


def text_splitter(text: str):
    sentence_separators_regex = re.compile(r'[.|!|?|...|\n|;]')
    sentences = sentence_separators_regex.split(text)
    return sentences


def sentence_splitter(sentence: str):
    words_separators_regex = re.compile(r'[\s|:|,|;|]')
    words = words_separators_regex.split(sentence)
    return words


def split_description(text: str):
    titles = ["SUMMARY OF THE INVENTION", "SUMMARY", "DETAILED DESCRIPTION", "BRIEF SUMMARY OF THE INVENTION",
              "DETAILED DESCRIPTION OF THE INVENTION", "TECHNICAL FIELD", "FIELD OF THE INVENTION",
              "SUMMARY AND OBJECTS OF THE INVENTION", "BRIEF SUMMARY"]
    result = []
    splitter = re.compile(r'([^a-z0-9.]{2,}\n)')
    splitted_text = splitter.split(text)
    for i, t in enumerate(splitted_text):
        if t.strip().isupper() and t.strip() in titles and len(splitted_text) > i:
            result.append(splitted_text[i+1])
    return " ".join(result)


# Метод поиска предложений с запрещенными словами
def find_forbidden_sentences(sentences: List[str]):
    forbidden_sentences = []
    forbidden_words = ['comprise', 'comprises', 'comprised', 'comprising', 'include', 'includes', 'including',
                       'included', 'consist', 'consists', 'consisted', 'consisting', 'have', 'has', 'had',
                       'having', 'connect', 'connects', 'connected', 'connecting', 'fig', 'figs', 'contain',
                       'contains', 'contained', 'containing']
    for sentence in sentences:
        if len(sentence) > 0:
            words = sentence_splitter(sentence)
            for word in words:
                if word.lower() in forbidden_words or word.isnumeric():
                    forbidden_sentences.append(sentence)
                    break
    return forbidden_sentences


# Метод обрезающий строку после ключевых слов
def find_trim_sentence(sentences: List[str]):
    is_cropped = False
    trim_sentences = []
    trim_sentence = ""
    words_of_cut_part = ['which', 'where', 'wherein']
    for sentence in sentences:
        if len(sentence) > 0:
            words = sentence.split()
            for i, word in enumerate(words):
                if word in words_of_cut_part:
                    trim_sentence = ' '.join(words[:i])
                    is_cropped = True
                    break
                elif word == 'and':
                    if i > 0:
                        if words[i-1][-1] == ',':
                            trim_sentence = ' '.join(words[:i])
                            is_cropped = True
                            break
                elif word == 'such':
                    if i < len(words)-1:
                        if words[i+1] == 'as':
                            trim_sentence = ' '.join(words[:i])
                            is_cropped = True
                            break

            if is_cropped:
                trim_sentences.append(trim_sentence)
            else:
                trim_sentences.append(sentence)
            is_cropped = False
    return trim_sentences


def get_sentences(text: str):
    sentences = text_splitter(text)
    forbidden_sentences = find_forbidden_sentences(sentences)
    for sentence in forbidden_sentences:
        sentences.remove(sentence)
    trim_sentence = find_trim_sentence(sentences)
    return trim_sentence


def get_sao(words, patent_id):
    object_deprel = ['nmod', 'obj', 'obl']

    object_id = None
    subject_id = None

    action_text = None

    subject = None
    action = None
    obj = None

    for i, word in enumerate(words):
        if word.deprel == 'root' and word.upos == 'VERB':
            if i > 1 and words[i-1].deprel == 'aux':
                action_text = words[i-1].text + " "
                id_start = words[i-1].id
            if action_text:
                action_text += word.text
                id_end = word.id
            else:
                action_text = word.text
                id_start = word.id
                id_end = word.id
            action = (id_start, id_end, action_text)
        elif word.deprel in object_deprel and not object_id:
            object_id = word.id
        elif word.deprel == 'nsubj' and not subject_id:
            subject_id = word.id

    if action and object_id and subject_id:
        if object_id < action[0]:
            obj = ' '.join(str(word.text) for word in words[:action[0]-1])
        elif subject_id < action[0]:
            subject = ' '.join(str(word.text) for word in words[:action[0]-1])
        if object_id > action[1]:
            obj = ' '.join(str(word.text) for word in words[action[1]:])
        elif subject_id > action[1]:
            subject = ' '.join(str(word.text) for word in words[action[1]:])

    if action and obj and subject:
        return Sao(str(uuid.uuid4()), subject, action[2], obj, patent_id)

    return None


# Функция для извлечения sao
def process_sao(text: str, patent_id: str, is_description: bool):
    if is_description:
        text = split_description(text)
    text = rem(text)
    sentences = get_sentences(text)
    nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse')
    con = create_connection("diplom", "postgres", "postgres", "localhost", "5432")
    for sentence in sentences:
        doc = nlp(sentence)
        if doc.sentences:
            sao = get_sao(doc.sentences[0].words, patent_id)
        if sao:
            try:
                insert_sao(con, sao)
            except psycopg2.errors.UniqueViolation as e:
                print(e)
    con.close()


def main():
    stanza.download('en')
    con = create_connection("diplom", "postgres", "postgres", "localhost", "5432")
    patents = get_entities(con, "patents")
    for patent_tuple in patents:
        patent = Patent(*patent_tuple)
        if patent.abstract_path:
            if os.path.isfile(patent.abstract_path):
                with open(str(patent.abstract_path), 'r', encoding='utf8') as f:
                    lines = f.read()
                    process_sao(lines, patent.id, False)
        if patent.description_path:
            if os.path.isfile(patent.description_path):
                with open(str(patent.description_path), 'r', encoding='utf8') as f:
                    lines = f.read()
                    process_sao(lines, patent.id, True)
    con.close()


if __name__ == '__main__':
    main()
