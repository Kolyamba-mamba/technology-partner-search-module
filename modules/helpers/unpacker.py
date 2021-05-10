import os
from os import path
import zipfile


def unpacker(input_file, output_path):
    try:
        fantasy_zip = zipfile.ZipFile(input_file)
        fantasy_zip.extractall(output_path)
        fantasy_zip.close()
    except:
        print('Ошибка при распаковке архива')


def main(args):
    print('Запущен распаковыватель')
    files = os.listdir(args.path)
    files = list(filter(lambda x: path.splitext(path.basename(x))[1] == '.zip', files))
    for file in files:
        unpacker(args.path+file, args.path+'unpack/')
    print(f'''Распаковано {len(os.listdir(args.path+'unpack/'))} из {len(files)}''')
