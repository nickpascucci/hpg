[![Build Status](https://travis-ci.org/nickpascucci/hpg.svg?branch=master)](https://travis-ci.org/nickpascucci/hpg)

# hpg
## The Hash Password Generator

hpg is a simple script designed to accomplish a few simple goals.

1. You should never have to remember passwords again.
2. You should be able to use unique passwords in each place they're required.
3. Your passwords should be stored securely, or even better, *not stored at all*.

It works by hashing an identifier with a salt to produce passwords
that are unique and secure. You can use whatever salt you want for
each password, so you can use a single one and treat it as a 'master'
password or mix it up for greater security.

Each password is deterministically generated from the salt and the
identifier so they are easy to retrieve. Just run ```hpg``` again
using the same inputs and you'll get the same password back. Because
of this, hpg doesn't need to store your passwords. Identifiers can be
saved and searched if you want, or they can be discarded after use if
you're feeling paranoid.

## An Example

Say I wanted to generate a password for this new, awesome site called
newawesome.com. I like to use a standard format for my identifiers so
that it's easy to remember what they are later. In this case, I'll use
nick@newawesome.com as my identifier, and create a new hashed password
using ```hpg```:

    [nick@mymachine ~/]: hpg nick@newawesome.com
    Salt: 
    'P'@Lrnz0?5_
    Store this key? [y/N] y

And now I have a new password which I can recover easily. If I want to
just use it immediately, I can add the -c option to hpg and it will
copy it to the clipboard for me. This way I never even have to see the
password!

## Installation

Download hpg.py and put it somewhere on your $PATH. Make it executable
with ```chmod +x hpg.py```, and you're good to go! If you want to get
fancy you can rename it to just ```hpg```.

## FAQ

+ Does hpg store my passwords anywhere?

  Nope. Passwords are generated deterministically by the hashing
  algorithm, so there's no need to store them as long as you remember
  the identifier and salt used to generate them. If you choose, you
  may let hpg save the keys used to generate your passwords along with
  any options specified on the command line in a JSON file. This file
  is stored at ```~/.hpg/keys.json```. The save prompt can be disabled
  entirely with the ```-n```/```--no-save``` option.

* What hashing algorithm does it use?

  SHA512. Since not all of the bytes in a SHA512 hash are printable
  hpg strips some blacklisted characters out of the hash and uses the
  rest to generate the passwords. You can control the blacklist by
  setting the ```--exclude-chars``` option to your liking. Please note
  that this isn't a cryptographic tool and makes no claims to be;
  we're just trying to generate reasonably strong passwords in a
  deterministic fashion.

* What platforms does it work on?

  All of the features work on OSX and Linux. Copying to clipboard
  doesn't currently work on Windows, but password generation does.

* What's the license?

  hpg is licensed under the GPLv3.

## Options
These are the options currently supported by ```hpg```:

| Short | Long             | Description                              |
|-------|------------------|------------------------------------------|
|  -l   | --length         | password length                          |
|  -e   | --exclude-chars  | characters to exclude                    |
|  -i   | --include-chars  | characters to include                    |
|  -a   | --alphanumeric   | use only [a-zA-Z0-9] *default=False*     |
|  -c   | --copy           | copy to clipboard *default=False*        |
|  -n   | --no-save        | don't save key *default=False*           |
|  -p   | --print-keys     | show saved keys *default=False*          |
|  -s   | --search         | search stored keys                       |

* If both --include-chars and --exclude-chars are specified,
  --exclude-chars takes precedence for any common characters.

* If both --alphanumeric and --include-chars are specified,
  --include-chars adds the specified chars to the [a-zA-Z0-9] set.
