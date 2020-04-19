import unittest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from time import sleep
from jibe import InJupyterMultiApp


opts = Options()
opts.headless = True
opts.width = 600


class TestAuthSession(unittest.TestCase):

    widgets = None

    @classmethod
    def setUpClass(cls) -> None:
        print("""
                #################################
                #          setUp                #
                #################################
                """)
        from examples.authsession import AuthenticationApp
        from examples.authsession import ExampleApp
        from examples.authsession import AuthMultiApp

        class InJupAuthMultiApp(InJupyterMultiApp, AuthMultiApp):
            pass

        app = InJupAuthMultiApp(
            a=AuthenticationApp,
            b=ExampleApp
        )

        cls.app = app
        cls.app.juprun(8881)
        cls.browser = Firefox(options=opts)
        sleep(2)

    def test_A_bringup(self):
        print("""
        #################################
        #         test_bringup          #
        #################################
        """)
        self.browser.get('http://localhost:8881/a')
        sleep(0.5)

        # We have not been redirected to /b because we have not logged in.
        self.assertEqual('http://localhost:8881/a', self.browser.current_url)

        results = self.browser.find_elements_by_class_name('widget')
        self.assertNotEqual(0, len(results))
        print(f'/a has {len(results)} widgets.')
        __class__.widgets = results

    def test_B_good_login(self):

        input_box = None

        # Find input box
        for w in __class__.widgets:
            if w.tag_name == 'input':
                input_box = w
                break

        self.assertIsNotNone(input_box)
        input_box.send_keys('password')

        button = None

        # Find button
        for w in __class__.widgets:
            if w.tag_name == 'button':
                button = w
                break

        self.assertIsNotNone(button)

        # Click
        button.click()
        sleep(1)

        # We have been redirected to the main application.
        self.assertEqual('http://localhost:8881/b', self.browser.current_url)

        self.verify_app()

    def test_C_auto_redirect(self):
        self.browser.get('http://localhost:8881/a')
        sleep(0.5)

        # We have been redirected to the main application.
        self.assertEqual('http://localhost:8881/b', self.browser.current_url)

        self.verify_app()

    def verify_app(self):
        results = self.browser.find_elements_by_class_name('widget')
        self.assertNotEqual(0, len(results))
        print(f'/b has {len(results)} widgets.')
        __class__.widgets = results

        input_box = None
        for w in __class__.widgets:
            if w.tag_name == 'input':
                input_box = w
                break

        self.assertIsNotNone(input_box)
        self.assertEqual(input_box.get_property('value'), '')

        for w in __class__.widgets:
            if w.tag_name == 'button' and w.text == 'button':
                w.click()
                break

        sleep(0.5)
        self.assertNotEqual(input_box.get_property('value'), '')

    @classmethod
    def tearDownClass(cls) -> None:
        print("""
            #################################
            #         tearDown              #
            #################################
            """)
        cls.app.server.stop()


if __name__ == '__main__':
    unittest.main(failfast=True)