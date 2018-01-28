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

"""Tests for HPG."""

import hpg
import string
import unittest

class TestHpgPasswordGeneration(unittest.TestCase):

  KEYS = {
    "foo@bar.com": {
      "alpha": "cNUesqtZ8MCXSQ",
      "symbols": "c-NUesqtZ8'M]C"
    },
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ": {
      "alpha": "6Q4azB5quDxZLl",
      "symbols": "6Q?4azB;5qu}%D"
    },
    "1234567890": {
      "alpha": "FA1DvUflwvVmib",
      "symbols": "FA|,1Dv`\"Ufl*w"
    },
    "AsDf$!#$@&)*QwErTy": {
      "alpha": "uPwG7GTfBgAsga",
      "symbols": "uPw%$G7>GTfBgA"
    }}

  SALT = "U7tsE8fCy*JN@P_L"
  LENGTH = 14

  def test_alpha(self):
    for key in self.KEYS:
      generated = hpg.generate_password(
        key, self.SALT, self.LENGTH, hpg.ALPHANUM)
      expected = self.KEYS[key]["alpha"]
      self.assertEqual(generated, expected,
        msg = "For key %s, generated pass %s is not expected pass %s" % (
          key, generated, expected))

  def test_all_symbols(self):
    for key in self.KEYS:
      generated = hpg.generate_password(
        key, self.SALT, self.LENGTH, hpg.ALPHANUM + hpg.SYMBOLS)
      expected = self.KEYS[key]["symbols"]
      self.assertEqual(generated, expected,
        msg = "For key %s, generated pass %s is not expected pass %s" % (
          key, generated, expected))

if __name__ == '__main__':
    unittest.main()
