import unittest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from time import sleep
from pathlib import Path


class TestAuthSession(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path(__file__).parent.parent
        print(self.path)
        opts = Options()
        opts.headless = True
        self.browser = Firefox(options=opts)

    def test_authsession(self):
        self.browser.get('http://localhost:8881/a')
        sleep(1)  # The above does not block. So wait.
        results = self.browser.find_elements_by_class_name('widget')
        print(len(results))
        for result in results:
            if 'Input' in result.get_property('id'):
                print(result)

    def tearDown(self) -> None:
        self.browser.close()