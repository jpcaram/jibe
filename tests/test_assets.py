# Jibe
# A Full-Stack Pure-Python Web Framework.
# Copyright (c) 2020 Juan Pablo Caram
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from unittest import TestCase
import unittest
import requests
from jibe import InJupyterApp
from time import sleep


class TestBasic(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("""
        #################################
        #          setUp                #
        #################################
        """)
        from examples.assets import AppWithAssets

        # Make this an app that can be run in the background.
        class JBasicExample(AppWithAssets, InJupyterApp):
            pass

        cls.app = JBasicExample
        cls.app.juprun(8881)
        sleep(2)

    def test_bringup(self):
        print("""
        #################################
        #         test_bringup          #
        #################################
        """)
        r = requests.get('http://localhost:8881')
        self.assertEqual(200, r.status_code)

    def test_assets(self):
        print("""
        #################################
        #     test_assets               #
        #################################
        """)

        r = requests.get('http://localhost:8881/assets/image.png')
        self.assertEqual(200, r.status_code)

    @classmethod
    def tearDownClass(cls) -> None:
        print("""
        #################################
        #         tearDown              #
        #################################
        """)
        cls.app.server.stop()


if __name__ == '__main__':
    unittest.main()
