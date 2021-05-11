import argparse
import os


def parse_args(args):
    parser = argparse.ArgumentParser(description='Скачиватель патентов')
    parser.add_argument('-startDownloader', type=bool, dest='startDownloader',
                        default=False, help='Запускать ли скачватель патентов')
    parser.add_argument('-startUnpacker', type=bool, dest='startUnpacker',
                        default=False, help='Запускать ли распаковщик патентов')
    parser.add_argument('-path', type=str, dest='path',
                        default='C:/Users/mrkol/Documents/patents/',
                        help='Место сохранения')
    parser.add_argument('-saveUrl', type=bool, dest='saveUrl',
                        default=False, help='Сохранять ли ссылки на файлы патентов')
    parser.add_argument('-urlsPath', type=str, dest='urlsPath', help='Путь к файлу с ссылками')
    parser.add_argument('-parsePatent', type=bool, dest='parsePatent', default=False, help='Запуск парсера патентов')
    parser.add_argument('-selectSao', type=bool, dest='selectSao', default=False, help='Запуск извлечения структур SAO')
    parser.add_argument('-createSaoLog', type=bool, dest='createSaoLog', default=False,
                        help='Сохранение логов при извлечении SAO')
    parser.add_argument('-createW2VModel', type=bool, dest='cerateW2VModel', default=False,
                        help='Создание модели Word2Vec')
    return parser.parse_args(args)


def validate_args(args):
    if not args.saveUrl:
        if args.urlsPath is None or not os.path.isfile(args.urlsPath):
            print('Файла с ссылками не существует')
            return False
        else:
            return True
    if args.saveUrl:
        if args.urlsPath is not None:
            print('Вы не можете указывать путь к файлу с сылками, так как этот файл будет создан скриптом ')
            return False
        else:
            return True
    if args.startUnpacker:
        if os.path.isfile(args.path):
            return True
        else:
            return False
    else:
        return True
