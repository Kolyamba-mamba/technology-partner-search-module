import stanza
import os
import sys
from gensim.models import Word2Vec
from modules.helpers.dbHelper import create_connection
from modules.dbActions.getTables import get_entities_by_condition
from modules.models.sao import Sao


# объединение списков
def merge_list(lst1, lst2):
    for i in lst2:
        if i not in lst1:
            lst1.append(i)
    return lst1


# объединение списков
def merge_list_and_count_weight(lst1, lst2):
    for i in lst2:
        if i not in lst1:
            lst1.append(i)
        else:
            index = lst1.index(i)
            if index >= 0:
                lst1[index] = (lst1[index][0] + i[0], lst1[index][1])
    return lst1


# получение элементов с уникальным родителем
def get_sao_with_unique_parent(lst):
    result = []
    item_in_list = False
    for l in lst:
        for res in result:
            input_sao = Sao(*l[1])
            result_sao = Sao(*res[1])
            if input_sao.patent_id == result_sao.patent_id:
                item_in_list = True
                break
        if not item_in_list:
            result.append(l)
        item_in_list = False
    return result


# ищем совпадения с синонимами объекта
def find_synonym_match(model, connection, el, type):
    counter = 0
    sao_with_object = []
    try:
        synonyms = model.wv.most_similar(positive=str(el))
    except:
        print("синоним не найден")
        return sao_with_object
    while counter < len(synonyms) and counter < 8 and synonyms[counter][1] > 0.6:
        counter += 1
        saos = get_entities_by_condition(connection, 'sao', f'''lower({type}) like '%{synonyms[counter][0].lower()}%' ''')
        if len(saos) > 0:
            saos_with_weight = list(map(lambda x: (synonyms[counter][1], x), saos))
            sao_with_object = merge_list(sao_with_object, saos_with_weight)
    return sao_with_object


# получение action и object из запроса
def get_ao(query):
    object_deprel = ['nmod', 'obj', 'obl']
    action = []
    obj = []
    nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse')
    doc = nlp(query)
    if doc.sentences:
        for word in doc.sentences[0].words:
            if word.upos == 'VERB':
                action.append(word.text)
            elif word.deprel in object_deprel:
                obj.append(word.text)
    return action, obj


# Функция поиска совпадающих с запросом sao
def find_match(connection, query):
    # stanza.download('en')
    model = Word2Vec.load('C:\\Users\\mrkol\\OneDrive\\Рабочий стол\\Univers\\Диплом\\technology-partner-search-module\\modules\\analyzer\\myModel.model')
    sao_with_action = []
    sao_with_object = []
    action, obj = get_ao(query)
    for a in action:
        saos = get_entities_by_condition(connection, 'sao', f'''lower(action) = '{a.lower()}' ''')
        if len(saos) > 0:
            saos_with_weight = list(map(lambda x: (1, x), saos))
            sao_with_action = merge_list(sao_with_action, saos_with_weight)
        synonym_sao = find_synonym_match(model, connection, a, 'action')
        sao_with_action = merge_list(sao_with_action, synonym_sao)
    for o in obj:
            saos = get_entities_by_condition(connection, 'sao', f'''lower(object) like '%{o.lower()}%' ''')
            if len(saos) > 0:
                saos_with_weight = list(map(lambda x: (1, x), saos))
                sao_with_object = merge_list(sao_with_object, saos_with_weight)
            synonym_sao = find_synonym_match(model, connection, o, 'object')
            sao_with_action = merge_list(sao_with_action, synonym_sao)
    match_list = merge_list_and_count_weight(sao_with_action, sao_with_object)
    match_list.sort(key=lambda x: (x[0]), reverse=True)
    result = get_sao_with_unique_parent(match_list)
    return result


def get_patents(query):
    results = []
    connection = create_connection("diplom", "postgres", "postgres", "localhost", "5432")
    # save_text_db_to_txt(connection)
    # create_w2v_model('C:/Users/mrkol/Documents/myLog/dataset1.txt')
    matches = find_match(connection, query)
    for match in matches:
        patent = get_entities_by_condition(connection, "patents", f"id = '{match[1][4]}'")[0]
        result = (patent[0], patent[5], patent[4], patent[1], match[1][2] + " " + match[1][3], match[1][1], patent[9])
        results.append(result)
    return results



# model = Word2Vec.load('myModel.model')
# query = input()
get_patents("reducing capacity")# get_patents("reducing capacity")