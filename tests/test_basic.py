from unittest import TestCase
import unittest
import requests
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from jibe import InJupyterApp
from time import sleep


opts = Options()
opts.headless = True
opts.width = 600


class TestBasic(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("""
        #################################
        #          setUp                #
        #################################
        """)
        from examples.basic import ExampleApp as BasicExample

        # Make this an app that can be run in the background.
        class JBasicExample(BasicExample, InJupyterApp):
            pass

        cls.app = JBasicExample
        cls.app.juprun(8881)
        cls.browser = Firefox(options=opts)
        sleep(2)

    def test_bringup(self):
        print("""
        #################################
        #         test_bringup          #
        #################################
        """)
        self.browser.get('http://localhost:8881')
        sleep(5)
        results = self.browser.find_elements_by_class_name('widget')
        self.assertEqual(2, len(results))

    def test_clickchange(self):
        print("""
        #################################
        #     test_clickchange          #
        #################################
        """)
        self.browser.get('http://localhost:8881')
        sleep(1)
        results = self.browser.find_elements_by_class_name('widget')
        btn = results[0]
        inp = results[1]
        text0 = inp.get_property('value')
        self.assertEqual('The value', text0)
        btn.click()
        sleep(0.1)
        text1 = inp.get_property('value')
        self.assertEqual('Hello!', text1)

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
