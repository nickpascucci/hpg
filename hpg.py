#! /usr/bin/env python2.7
# -*- mode: python; fill-column: 80; -*-

"""A simple password generator.

Uses a seed password and an identifier to generate a password. This allows it to
generate unique passwords and recover them easily.
"""

import argparse
import getpass
import hashlib
import os
import os.path
import string
import sys
import subprocess

__author__ = "Nick Pascucci (npascut1@gmail.com)"

HELP_TEXT = ("Usage: hpg [-l<password length>] [-e<excluded chars>] " 
             "[-a] [-c] [-n] <identifier>")
CONFIG_DIR = os.path.expanduser("~/.hpg")
KEYS_FILE = CONFIG_DIR + "/keys"

parser = argparse.ArgumentParser(description="A simple password generator.")
parser.add_argument("-l", "--length", help="password length",
                    default=12, dest="length")
parser.add_argument("-e", "--excluded-chars", help="exclude characters",
                    default="", dest="excluded_chars")
parser.add_argument("-a", "--alphanumeric", help="use only [a-zA-Z0-9]",
                    action="store_true", default=False, dest="alpha")
parser.add_argument("-c", "--copy", help="copy to X clipboard",
                    action="store_true", default=False, dest="copy")
parser.add_argument("-n", "--no-save", help="don't save key",
                    action="store_false", default=True, dest="save")
parser.add_argument("-p", "--print-keys", help="show saved keys",
                    action="store_true", default=False, dest="print_keys")
parser.add_argument("-s", "--search", help="search stored keys",
                    dest="search", nargs="+")
parser.add_argument("key", help="key to use as password base", nargs="*")

options = parser.parse_args()

def main():
    if not options.key and not options.print_keys and not options.search:
        parser.print_help()
        exit(0)

    if options.print_keys:
        print_keys()
        exit(0)

    if options.search:
        search(options.search)
        exit(0)

    if options.alpha:
        available_chars = set(string.ascii_letters + string.digits)
    else:
        available_chars = set(string.printable)
    available_chars -= set(string.whitespace + options.excluded_chars)

    # Check arguments.
    if options.copy and not check_for_xsel():
        print ("xsel is not in your PATH. You must install it "
               "before passwords can be copied to the clipboard.")
        exit(1)

    save_key(options.key[0], options.save, get_options(options))

    # Get salt from user without echoing.
    password = getpass.getpass("Salt: ")
    pw_hash = hashlib.sha512(password).digest()
    generated_pass = hashlib.sha512(pw_hash + options.key[0]).digest()

    # Now, we need to extract a printable password from the hash.
    printable_pass = ""
    position = 0
    while len(printable_pass) < options.length:
        # Skip excluded characters. May cause the password to loop.
        while (generated_pass[position] not in available_chars):
            position = (position + 1) % len(generated_pass)
        # When the next printable character is encountered, add it.
        printable_pass += generated_pass[position]
        position += 1

    if options.copy:
        print "Password copied to X clipboard."
        save_to_clipboard(printable_pass)
    else:
        print printable_pass

def save_key(key, prompt=True, options=""):
    # Check to see that the config dir exists, creating it if needed
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

    # Create the keyfile if needed
    if not os.path.isfile(KEYS_FILE):
        open(KEYS_FILE, "w").close()

    key_in_file = False
    with open(KEYS_FILE, "r") as keyfile:
        for line in keyfile:
            if line.strip().split()[0] == key:
                key_in_file = True

    if not key_in_file and prompt:
        confirmation = raw_input("Store this key? [y/N] ")
        if confirmation.lower() == "y":
            keyfile = open(KEYS_FILE, "a")
            keyfile.write("%s %s\n" % (key, options))

def print_keys():
    with open(KEYS_FILE, "r") as keyfile:
        for line in keyfile:
           print line,

def search(terms):
    with open(KEYS_FILE, "r") as keyfile:
        for line in keyfile:
           for term in terms:
               if term in line:
                   print line,

def get_options(options):
    string = "["
    if options.alpha:
        string += "alpha "
    if options.excluded_chars:
        string += "exclude: [" + options.excluded_chars + "] "
    return string + "]"

def check_for_xsel():
    which_proc = subprocess.Popen(['which', 'xsel'], 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    which_proc.wait()
    return (which_proc.returncode == 0)

def save_to_clipboard(password):
    xsel_proc = subprocess.Popen(['xsel', '-pi'], stdin=subprocess.PIPE)
    xsel_proc.communicate(password)

if __name__ == "__main__":
    main()
