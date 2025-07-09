#!/usr/bin/env python3

"""
    Tenta 'crackar' um ficheiro de palavras passe com uma estrutura identica ao 'etc/shadow'. Apresentam-se aqui duas formas
    de ler parâmetros da linha de comandos:
    1. Utilizando o móduloi argparse (presente na biblioteca padrão)
    2.Utilizando o módulo  docopt (disponível no PyPI)

    More to come.
"""
import os
from docopt import docopt
import sys

DEFAULT_PWD_FILE = '/etc/shadow'

def main():
    """
        Pycracker entry point. Reads command line arguments and using the docopt library and calls the appropriate functions
    """
    doc = f"""
    Pycracker is a password cracker written in Python3. Using a password dictionary, 
    it searches for user with passwords in that dictionary

    Usage:
        {sys.argv[0]} <dictionary> [<passwords>] [-u USER] [-v]

    Options:
        -h, --help              Show help
        <passwords>             /etc/shadow-like file [default: {DEFAULT_PWD_FILE}]
        <dictionary>            Password dictionary
        -u USER, --user=USER    Search password for this USER only
        -v, --verbose           Increase verbosity level
    """

    args = docopt(doc)
    print(args)

if __name__ == '__main__':
    main()