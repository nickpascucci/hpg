#! /usr/bin/env python2.7
# -*- mode: python; fill-column: 80; -*-

"""A simple password generator.

Uses a seed password and an identifier to generate a password. This allows it to
generate unique passwords and recover them easily.
"""

import getpass
import hashlib
import os
import os.path
import string
import sys

__author__ = "Nick Pascucci (npascut1@gmail.com)"

HELP_TEXT = ("Usage: hpg <identifier> [-l<password length>]" 
             " [-e<excluded chars>]")
CONFIG_DIR = os.path.expanduser("~/.hpg")
KEYS_FILE = CONFIG_DIR + "/keys"

def main():
    UNGOOD_CHARS = string.whitespace
    NUM_CHARS = 12

    # Check arguments.
    if len(sys.argv) < 2:
        print HELP_TEXT
        exit(1)
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg.startswith("-l"):
                try:
                    NUM_CHARS = int(arg[2:])
                    print "Password length:", NUM_CHARS
                except:
                    print HELP_TEXT
            elif arg.startswith("-e"):
                print "Excluding", arg[2:]
                UNGOOD_CHARS += arg[2:]
            else:
                print "Unrecognized option %s. Ignoring." % arg

    identifier = sys.argv[1]
    
    store_key(identifier)

    # Get password from user without echoing.
    password = getpass.getpass("Password: ")
    # Hash their password; this is our seed.
    pw_hash = hashlib.sha512(password).digest()
    generated_pass = hashlib.sha512(pw_hash + identifier).digest()

    # Now, we need to extract a printable password from the hash.
    printable_pass = ""
    position = 0
    while len(printable_pass) < NUM_CHARS: # and position < len(generated_pass):
        # Skip non-printable characters.
        while (generated_pass[position] not in string.printable
               or generated_pass[position] in UNGOOD_CHARS):
            position += 1
        # When the next printable character is encountered, add it.
        printable_pass += generated_pass[position]
        position += 1

    print printable_pass

def store_key(identifier):
    # Check to see that the config dir exists, creating it if needed
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

    # Create the keyfile if needed
    if not os.path.isfile(KEYS_FILE):
        open(KEYS_FILE, "w").close()

    key_in_file = False
    with open(KEYS_FILE, "r") as keyfile:
        for line in keyfile:
            if line.strip() == identifier:
                key_in_file = True

    if not key_in_file:
        confirmation = raw_input("Store this key? [y/N] ")
        if confirmation.lower() == "y":
            keyfile = open(KEYS_FILE, "a")
            keyfile.write(identifier + "\n")

if __name__ == "__main__":
    main()