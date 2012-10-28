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
import subprocess

__author__ = "Nick Pascucci (npascut1@gmail.com)"

HELP_TEXT = ("Usage: hpg [-l<password length>] [-e<excluded chars>] " 
             "[-a] [-c] [-n]")
CONFIG_DIR = os.path.expanduser("~/.hpg")
KEYS_FILE = CONFIG_DIR + "/keys"

def main():
    BASE_CHARS = string.printable
    UNGOOD_CHARS = string.whitespace
    NUM_CHARS = 12
    copy_to_clipboard = False
    prompt_for_save = True

    # Check arguments.
    if len(sys.argv) < 2:
        print HELP_TEXT
        exit(1)
    if len(sys.argv) > 2:
        for arg in sys.argv[1:-1]:
            arg = arg.strip()
            if arg.startswith("-l"):
                try:
                    NUM_CHARS = int(arg[2:])
                    print "Password length:", NUM_CHARS
                except:
                    print HELP_TEXT
            elif arg.startswith("-e"):
                print "Excluding", arg[2:]
                UNGOOD_CHARS += arg[2:]
            elif arg == "-a":
                print "Using only alphanumeric characters."
                BASE_CHARS = string.letters + string.digits
            elif arg == "-c":
                if not check_for_xsel():
                    print ("xsel is not in your PATH. You must install it "
                           "before passwords can be copied to the clipboard.")
                    exit(1)
                copy_to_clipboard = True
            elif arg == "-n":
                prompt_for_save = False
            else:
                print "Unrecognized option %s. Ignoring." % arg

    identifier = sys.argv[-1]
    
    store_key(identifier, prompt_for_save)

    # Get password from user without echoing.
    password = getpass.getpass("Salt: ")
    # Hash their password; this is our seed.
    pw_hash = hashlib.sha512(password).digest()
    generated_pass = hashlib.sha512(pw_hash + identifier).digest()

    # Now, we need to extract a printable password from the hash.
    printable_pass = ""
    position = 0
    while len(printable_pass) < NUM_CHARS: # and position < len(generated_pass):
        # Skip non-printable characters.
        while (generated_pass[position] not in BASE_CHARS
               or generated_pass[position] in UNGOOD_CHARS):
            position += 1
        # When the next printable character is encountered, add it.
        printable_pass += generated_pass[position]
        position += 1

    if copy_to_clipboard:
        print "Password copied to X clipboard."
        save_to_clipboard(printable_pass)
    else:
        print printable_pass

def store_key(identifier, prompt=True, save=False):
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
        if prompt and not save:
            confirmation = raw_input("Store this key? [y/N] ")
            if confirmation.lower() == "y":
                save = True
        if save:
            keyfile = open(KEYS_FILE, "a")
            keyfile.write(identifier + "\n")

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

