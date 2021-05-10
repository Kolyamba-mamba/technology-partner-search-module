from typing import List
import os
import sys
from modules.models.sao import Sao


def record_sao_log(patent_number: str, description_text: str, sentences: List[str], saos: List[Sao], filePath: str):
    try:
        with open(filePath, 'a', encoding="utf-8") as file:
            file.write(patent_number + '\n')
            file.write(description_text + '\n\n')
            file.write('Отобранные для извлечения SAO предложения:\n')
            for sentence in sentences:
                file.write(sentence + '\n')
            file.write('\nSAO:\n')
            for sao in saos:
                file.write('Subject: ' + sao.subject + '\n')
                file.write('Action: ' + sao.action + '\n')
                file.write('Object: ' + sao.object + '\n\n')
            file.write('\n')
    except EnvironmentError:
        print("Ошибка при записи в файл:" + filePath)
