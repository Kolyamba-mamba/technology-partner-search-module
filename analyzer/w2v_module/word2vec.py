import nltk
import os
import re
from nltk.corpus import stopwords
from gensim.models import Word2Vec


def prepare_dataset(dataset):
    stop_words = stopwords.words('english')
    # Очистка
    print("Привеодим к нижнему регистру")
    processed_article = dataset.lower()
    print("Удаляем все кроме слов")
    processed_article = re.sub(r'[^a-zA-Z\.]', ' ', processed_article)
    processed_article = processed_article.replace('fig', ' ')
    print("Удаляем лишние пробелы")
    processed_article = re.sub(r'\s+', ' ', processed_article)


    # Подготовка данных
    print("Разбиваем на предложения")
    all_sentences = nltk.sent_tokenize(processed_article)

    print("Разбиваем на слова")
    all_words = [nltk.word_tokenize(sent) for sent in all_sentences]

    # Удаление стоп слов
    print("Удаляем стоп слова")
    for i in range(len(all_words)):
        all_words[i] = [w for w in all_words[i] if w not in stop_words]

    return all_words


def create_w2v_model(path):
    # nltk.download('punkt')
    # nltk.download('stopwords')
    if os.path.isfile(path):
        with open(str(path), 'r', encoding='utf8') as f:
            dataset = f.read()
            words = prepare_dataset(dataset)
            print("Обучение модели")
            model = Word2Vec(words,  vector_size=50,  window=5,  min_count=2,  workers=6,  epochs=5)
            print("Сохранение модели")
            model.save('myModel.model')

