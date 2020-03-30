from unittest import TestCase
import unittest
import requests
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from jibe import InJupyterApp, InJupyterMultiApp
from time import sleep


opts = Options()
opts.headless = True
opts.width = 600


class TestMultiApp(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("""
        #################################
        #          setUp                #
        #################################
        """)
        from examples.multiapp import ExampleAppA
        from examples.multiapp import ExampleAppB

        app = InJupyterMultiApp(
            a=ExampleAppA,
            b=ExampleAppB
        )

        cls.app = app
        cls.app.juprun(8881)
        cls.browser = Firefox(options=opts)
        sleep(2)

    def test_bringup(self):
        print("""
        #################################
        #         test_bringup          #
        #################################
        """)
        self.browser.get('http://localhost:8881/a')
        sleep(1)
        results = self.browser.find_elements_by_class_name('widget')
        self.assertNotEqual(0, len(results))
        print(f'/a has {len(results)} widgets.')
        __class__.widgets = results

    def test_redirect(self):
        print("""
        #################################
        #         test_redirect         #
        #################################
        """)

        for w in __class__.widgets:
            if w.text == "Go to B":
                break
        self.assertEqual(w.text, "Go to B")

        w.click()
        sleep(0.5)
        self.assertEqual('http://localhost:8881/b', self.browser.current_url)

        __class__.widgets = self.browser.find_elements_by_class_name('widget')
        for w in __class__.widgets:
            if w.text == "Go to A":
                break
        self.assertEqual(w.text, "Go to A")

        w.click()
        sleep(0.5)
        self.assertEqual('http://localhost:8881/a', self.browser.current_url)

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
