#! /usr/bin/env python2.7
# -*- mode: python; fill-column: 80; -*-

# hpg - The Hash Password Generator.
# Copyright (C) 2014  Nick Pascucci

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

"""A simple password generator.

Uses a seed password and an identifier to generate a password. This allows it to
generate unique passwords and recover them easily."""

import argparse
import getpass
import hashlib
import json
import os
import os.path
import platform
import string
import sys
import subprocess

__author__ = "Nick Pascucci (npascut1@gmail.com)"

CONFIG_DIR = os.path.expanduser("~/.hpg")
KEYS_FILE = CONFIG_DIR + "/keys.json"
DEFAULT_LENGTH = 12

parser = argparse.ArgumentParser(description="A simple password generator.")
# Generator options
parser.add_argument("-l", "--length", help="password length",
                    default=DEFAULT_LENGTH, dest="length", type=int)
parser.add_argument("-e", "--exclude-chars", help="characters to exclude",
                    default="", dest="excluded_chars")
parser.add_argument("-i", "--include-chars", help="characters to include",
                    default="", dest="included_chars")
parser.add_argument("-a", "--alphanumeric", help="use only [a-zA-Z0-9]",
                    action="store_true", default=False, dest="alpha")

# Operations
parser.add_argument("-c", "--copy", help="copy to clipboard",
                    action="store_true", default=False, dest="copy")
parser.add_argument("-n", "--no-save", help="don't save key",
                    action="store_true", default=False, dest="skip_save")
parser.add_argument("-p", "--print-keys", help="show saved keys",
                    action="store_true", default=False, dest="print_keys")
parser.add_argument("-s", "--search", help="search stored keys",
                    dest="search", nargs="+")

parser.add_argument("key", help="key to use as password base")

def main():
  options = parser.parse_args()
  if not options.key and not options.print_keys and not options.search:
        parser.print_help()
        exit(0)

  ensure_config()
  config = load_config(KEYS_FILE)
  keys = config["keys"]

  if options.print_keys:
      print_keys(keys)
      exit(0)

  if options.search:
      search(options.search, keys)
      exit(0)

  # Check arguments.
  if options.copy and not check_for_xsel():
      print ("xsel is not in your PATH. You must install it "
             "before passwords can be copied to the clipboard.")
      exit(1)

  saved_config = find_config(options.key, keys)
  use_saved_config = False
  if saved_config:
    use_saved_config = prompt("Use saved settings for this key?",
                              default=True)

  printable_pass = ""
  if use_saved_config:
    printable_pass = generate_password(saved_config.get("name").encode("ascii"),
                                       saved_config.get("alphanumeric", False),
                                       saved_config.get("length", DEFAULT_LENGTH),
                                       saved_config.get("included_chars", ""),
                                       saved_config.get("excluded_chars", ""))
  else:
    printable_pass = generate_password(options.key,
                                       options.alpha,
                                       options.length,
                                       options.included_chars,
                                       options.excluded_chars)

  if options.copy:
      print "Password copied to clipboard."
      save_to_clipboard(printable_pass)
  else:
      print printable_pass
  if not options.skip_save and not use_saved_config:
    update_keys(options.key, keys, options)

def generate_password(key, restrict_to_alpha, length,
                      included_chars="", excluded_chars=""):
  # Basic character sets
  if restrict_to_alpha:
    available_chars = set(string.ascii_letters + string.digits)
  else:
    available_chars = set(string.printable)

  # Add in user-specified characters
  available_chars |= set(included_chars)

  # Remove non-printables and user-specified exclusions
  available_chars -= set(string.whitespace + excluded_chars)

  # Get salt from user without echoing.
  password = getpass.getpass("Salt: ")
  pw_hash = hashlib.sha512(password).digest()
  generated_pass = hashlib.sha512(pw_hash + key).digest()

  # Now, we need to extract a printable password from the hash.
  printable_pass = ""
  position = 0
  while len(printable_pass) < length:
    position = (position + 1) % len(generated_pass)
    # Skip excluded characters. May cause the password to repeat.
    if generated_pass[position] in available_chars:
      printable_pass += generated_pass[position]
  return printable_pass

def print_keys(keys):
  for key in keys:
    print key["name"],

def search(terms, keys):
  for key in keys:
    for term in terms:
      if term in key["name"]:
        print key["name"],

def ensure_config():
  # Check to see that the config dir exists, creating it if needed
  if not os.path.isdir(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)

  # Create the key file if needed
  if not os.path.isfile(KEYS_FILE):
    open(KEYS_FILE, "w").close()

def find_config(key, keys):
  for extant_key in keys:
    if extant_key["name"] == key:
      return extant_key

def update_keys(new_key, keys=[], options=""):
    extant_key = find_config(new_key, keys)

    save_key = False
    if not extant_key:
      save_key = prompt("Store this key?")
    else:
      save_key = prompt("Update this key?")

    if save_key:
      keys = [k for k in keys if k["name"] != new_key]
      keys.append(make_config_entry(new_key, options))
      with open(KEYS_FILE, "w") as keyfile:
        config = {"keys": keys}
        json.dump(config, keyfile)

def make_config_entry(key, options):
  entry = {"name": key, "length": options.length}
  if options.alpha:
    entry["alphanumeric"] = True
  if options.included_chars:
    entry["include"] = options.included_chars
  if options.excluded_chars:
    entry["exclude"] = options.excluded_chars
  return entry

def load_config(keyfile):
  with open(keyfile, "r") as f:
    return json.load(f)

def check_for_xsel():
    if platform.system() == "Linux":
        which_proc = subprocess.Popen(['which', 'xsel'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        which_proc.wait()
        return (which_proc.returncode == 0)
    return True

def save_to_clipboard(password):
    if platform.system() == "Linux":
        xsel_proc = subprocess.Popen(['xsel', '-pi'], stdin=subprocess.PIPE)
        xsel_proc.communicate(password)
    elif platform.system() == "Darwin":
        pbcopy_proc = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        pbcopy_proc.communicate(password)
    else:
        print "Copy to clipboard is not supported on this platform."

def prompt(text, default=False):
  if default:
    confirmation = raw_input(text + " [Y/n] ")
    return confirmation.lower() != "n"
  else:
    confirmation = raw_input(text + " [y/N] ")
    return confirmation.lower() == "y"

if __name__ == "__main__":
    main()
