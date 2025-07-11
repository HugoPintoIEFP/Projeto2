#!/usr/bin/env python3

"""
    Tenta 'crackar' um ficheiro de palavras passe com uma estrutura identica ao 'etc/shadow'. Apresentam-se aqui duas formas
    de ler parâmetros da linha de comandos:
    1. Utilizando o móduloi argparse (presente na biblioteca padrão)
    2.Utilizando o módulo  docopt (disponível no PyPI)

    Rafael Oliveira e Hugo Pinto, 2025
"""
#import os
#import string
import sys
from enum import Enum
from typing import TextIO
from docopt import docopt
from textwrap import dedent
from passlib.hash import sha512_crypt #sha256_crypt, md5_crypt, sha1_crypt, bcrypt
from passlib.context import CryptContext


DEFAULT_PWD_FILE = '/etc/shadow'

PYCRACKER_CTX = CryptContext(schemes = [
    'sha256_crypt',
    'sha512_crypt',
    'md5_crypt',
    'sha1_crypt',
    'bcrypt'
])


AccountStatus = Enum('AccountStatus', ' VALID BLOCKED LOCKED INVALID ')

HASH_ID_NAMES = {
    '0' : 'No Hash',
    '1' : 'MD5',
    '2' : 'Blowfish',
    '3' : 'Blowfish (2a)',
    '4' : 'Blowfish (2b)',
    '5' : 'SHA-256',
    '6' : 'SHA-512',
}

def show_matches(
        pwd_filename: str, 
        dict_filename: str, 
        user: str | None = None, 
        verbose = False
):
    """
    Shows all decrypted passwords and users.
    """
    # print(f"{pwd_filename=} {dict_filename=} {user=} {verbose=}")
    matches = find_matches(pwd_filename, dict_filename, user, verbose)
    if verbose is False:
        if len(matches) == 0:
            print("[-] Não foram encontradas quaisquer palavras-passe")
        else:
            print("Foram encontradas as seguintes palavras-passe:")
            for user, (clear_text_pwd, method_name) in matches.items():
                print(f"[+] {user:<10}: {repr(clear_text_pwd):<20} ({method_name})")
    else:
        for user, (clear_text_pwd, method_name) in matches.items():
            print(f"[+] A tentar utilizador '{user}'")
            if clear_text_pwd == 'B':
                print("[-] ... ignorado. Conta bloqueada/inativa.(começa por *)")
            elif clear_text_pwd == 'L':
                print("[-] ... ignorado. Conta bloqueada.(começa por !)")
            elif clear_text_pwd == 'I':
                print("[-] ... ignorado. Conta sem palavra-passe.")
            else:
                print(f"[=] ... PALAVRA-PASSE DESCOBERTA ===> '{clear_text_pwd}'")

def find_matches(
        pwd_filename: str, 
        dict_filename: str, 
        user: str | None = None, 
        verbose = False
) -> dict[str,tuple[str, str]]:
    """
    Returns a dictionary where each entry maps a username to a decrypted password 
    and the hashing algorithm that was used to encrypt the password.
    """
    matches = {}
    if user != None:
        with open(dict_filename, 'r') as dict_file:
            with open(pwd_filename, 'rt') as pwd_file:
                for line in pwd_file:
                    curr_user, pwd_field = line.split(':')[:2]
                    if curr_user == user:
                        account_status = get_account_status(pwd_field)
                        if account_status is AccountStatus.VALID:
                            if clear_txt_pwd := find_pwd(pwd_field,dict_file):
                                matches[curr_user] = (clear_txt_pwd, method_name(pwd_field))
                                break
                        if verbose is True:
                            if account_status is AccountStatus.BLOCKED:
                                matches[curr_user] = ('B', "")
                            elif account_status is AccountStatus.LOCKED:
                                matches[curr_user] = ('L', "")
                            if account_status is AccountStatus.INVALID:
                                matches[curr_user] = ('I', "")
                            elif account_status is AccountStatus.VALID:
                                if clear_txt_pwd := find_pwd(pwd_field,dict_file):
                                    matches[curr_user] = (clear_txt_pwd, method_name(pwd_field))        
                    else:
                        continue
                    dict_file.seek(0)
    else:                
        with open(dict_filename, 'r') as dict_file:
            with open(pwd_filename, 'rt') as pwd_file:
                for line in pwd_file:
                    curr_user, pwd_field = line.split(':')[:2]
                    account_status = get_account_status(pwd_field)
                    if account_status is AccountStatus.VALID:
                        if clear_txt_pwd := find_pwd(pwd_field,dict_file):
                            matches[curr_user] = (clear_txt_pwd, method_name(pwd_field))
                    if verbose is True:
                        if account_status is AccountStatus.BLOCKED:
                            matches[curr_user] = ('B', "")
                        elif account_status is AccountStatus.LOCKED:
                            matches[curr_user] = ('L', "")
                        if account_status is AccountStatus.INVALID:
                            matches[curr_user] = ('I', "")
                        elif account_status is AccountStatus.VALID:
                            if clear_txt_pwd := find_pwd(pwd_field,dict_file):
                                matches[curr_user] = (clear_txt_pwd, method_name(pwd_field))
                    dict_file.seek(0)

                
    return matches

def get_account_status(pwd_field: str) -> AccountStatus:
    return (
        AccountStatus.BLOCKED if pwd_field in ('*') else
        AccountStatus.LOCKED if len(pwd_field) > 0 and pwd_field[0] == '!' else
        AccountStatus.INVALID if len(pwd_field) == 0 else
        AccountStatus.VALID
    )


def find_pwd(pwd_field: str, dict_file: TextIO) -> str | None:
    """
    Searches for a clear-text password in 'dict_file'
    that hashes to the same value as the hash in 'pwd_field'. Returns
    the clear-text password, if one is found, otherwise returns 'None'.
    
    'pwd_field' is the password field for a given user in a /etc/shadow-like file.
    Example:
        $6$m7.33qCr$joi9qE/ZYc ... etc ... Fk9BAnGWOi7NqU4/LWYUiP9kxZIoJ90KJRm.
    """
    for clear_text_pwd in dict_file:
        clear_text_pwd = clear_text_pwd.strip()
        if verify_password(clear_text_pwd,pwd_field):
            return clear_text_pwd
    return None


def verify_password(clear_text_pwd: str, pwd_field: str) -> bool:
    return PYCRACKER_CTX.verify(clear_text_pwd, pwd_field)


def method_name(pwd_field:str) -> str:
    method_id = parse_pwd_field(pwd_field)[0]
    return HASH_ID_NAMES[method_id]


def parse_pwd_field(pwd_field: str) -> tuple:
    """
    Analisa a informação sobre uma palavra-passe e devolve três campos:
    método, sal e palavra-passe encriptada.
    'pwd_field' must be at least something like '$METODO$SAL$HASH' or
    '$METODO$rounds=ROUNDS$SALT$HASH'
    """

    fields = pwd_field.split('$')
    valid_pwd = len(fields) in (4,5) and all(len(field) > 0 for field in fields[1])
    if not valid_pwd:
        raise ValueError('Invalid password field')

    if len(fields) == 5:
        del fields[2]
    return tuple(fields[1:])

#def encrypt_pwd_for_shadow(clear_text_pwd: str, salt_size = 8) -> str:
#    """
    #Generates a complete and suitable password field for '/etc/shadow'.
    #Hashing method is SHA-512. Returns a string.
#    """

#    SHA512_ROUNDS = 5000
#    salt_chars = string.ascii_letters + string.digits
#    salt = ''.join(random.choice(salt_chars) for _ in range(salt_size))
#    return sha512_crypt.using(salt = salt, rounds = SHA512_ROUNDS).hash(clear_text_pwd)

def main1():
    """
        Pycracker entry point. Reads command line arguments and using the docopt library and calls the appropriate functions
    """
    doc = dedent(f"""
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
    """)

    args = docopt(doc)
    pwd_file = args['<passwords>'] or DEFAULT_PWD_FILE
    show_matches(pwd_file,args['<dictionary>'], args['--user'], args['--verbose'])

def main2():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Password Cracker")
    parser.add_argument(
        'dictionary',
        help="Ficheiro com dicionário de palavras-passe",
        metavar='<dictionary>',
    )

    parser.add_argument(
        'passwords',
        help="A file similar to /etc/shadow",
        metavar="<passwords>",
        nargs='?',
        default= DEFAULT_PWD_FILE,
    )
    parser.add_argument(
        '-u', '--user',
        help="User. If none is passed, try all",
        required=False,
    )
    parser.add_argument(
        '-v','--verbose',
        help="Increase verbosity level.",
        action='store_true',
    )
    args = parser.parse_args()

    show_matches(args.passwords, args.dictionary, args.user, args.verbose)

if __name__ == '__main__':
    main1()