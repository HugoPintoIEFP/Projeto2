#!/usr/bin/env python3
"""
Vamos agora fazer um programa para detectar ficheiros idênticos, isto é, ficheiros cujo conteúdo é igual.
Através da linha de comandos, o seu programa recebe um caminho para uma directoria e no final deve exibir
uma listagem com todos os ficheiros duplicados dentro dessa directoria,
inclusive dentro das sub-directorias.

Rafael Oliveira e Hugo Pinto, 2025
"""

import re
import sys
from docopt import docopt
import os
import hashlib
# -----------------------------------------------------------------------------------------
def main():
    doc = f'''
Returns all duplciate files in the given folder.

Usage:
    {sys.argv[0]} [-c] [-n] [-e] [-r PATTERN] [DIR_PATH]

Options:
    DIR_PATH                        Start directory [defalt: .]
    -c, --contents                  Search files with the same binary content
    -n, --name                      Search files with the same name
    -e, --extension                 Search files with the same extension
    -r PATTERN, --regex==PATTERN    Search files using a regular expression
'''
    args = docopt(doc)
    #print(args)
    dir_path = '.' if args['DIR_PATH'] is None else args['DIR_PATH']

    if args['--contents']:
        print("_______________BY CONTENTS_____________________")
        show_groups(group_files_by_contents(dir_path))
        print("-----------------------------------------------------")

        print()
    
    if args['--name']:
        print("_______________BY NAME_____________________")
        show_groups(group_files_by_name(dir_path))
        print("-----------------------------------------------------")

        print()
    
    if args['--extension']:
        print("________________BY EXTENSION__________________")
        show_groups(group_files_by_extension(dir_path))
        print("-----------------------------------------------------")

        print()

    if args['--regex']:
        print("________________BY REGEX__________________")
        regex = args['--regex']
        show_groups({regex:group_files_by_regex(dir_path, regex)})
        print("-----------------------------------------------------")
        print()





# Funções.
# -----------------------------------------------------------------------------------------
def show_groups(duplicates: dict):
    for filename, paths in duplicates.items():
        if len(paths) > 1:
            print(filename)
            for path in paths:
                print(f'   {path}')
            print()
# -----------------------------------------------------------------------------------------
def group_files_by_name(dir_path) -> dict[str, list[str]]:
    groups={}
    for curr_dir, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename not in groups:
                groups[filename] = []
            groups[filename].append(os.path.join(curr_dir, filename))
    return groups
# -----------------------------------------------------------------------------------------
def group_files_by_extension(dir_path) -> dict[str, list[str]]:
    groups={}
    for curr_dir, _, filenames in os.walk(dir_path):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext not in groups:
                groups[ext] = []
            groups[ext].append(os.path.join(curr_dir, filename))
    return groups
# -----------------------------------------------------------------------------------------
def group_files_by_regex(dir_path, regex: str) -> list[str]:
    found_filenames=[]
    for curr_dir, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if re.search(regex, filename):
                found_filenames.append(os.path.join(curr_dir, filename))
    return found_filenames
# -----------------------------------------------------------------------------------------
def group_files_by_contents(dir_path: str) -> dict[str, list[str]]:
    groups={}
    for curr_dir, _, filenames in os.walk(dir_path):
        for filename in filenames:
            filepath = os.path.join(curr_dir, filename)
            hash = hashlib.file_digest(open(filepath, 'rb'), 'md5').hexdigest()
            if hash not in groups:
                groups[hash] = []
            groups[hash].append(os.path.join(curr_dir, filename))
    return groups
# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
# -----------------------------------------------------------------------------------------