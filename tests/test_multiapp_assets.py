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
from jibe import InJupyterMultiApp
from time import sleep
from pathlib import Path


class TestMultiApp(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("""
        #################################
        #          setUp                #
        #################################
        """)
        from examples.multiapp_assets import ExampleAppA, ExampleAppB, mapp

        app = InJupyterMultiApp(
            a=ExampleAppA,
            b=ExampleAppB,
            assets_path={
                'to': '',
                'from': f'{Path(__file__).parent.absolute()}/data'
            }
        )

        cls.app = app
        cls.app.juprun(8881)

        sleep(2)

    def test_assets(self):
        print("""
        #################################
        #         test_assets           #
        #################################
        """)

        r = requests.get('http://localhost:8881/a/assets/image_orange.png')
        self.assertEqual(200, r.status_code)

        r = requests.get('http://localhost:8881/b/assets/image_blue.png')
        self.assertEqual(200, r.status_code)

        r = requests.get('http://localhost:8881/image.png')
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
