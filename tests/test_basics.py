import unittest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from time import sleep
from pathlib import Path

import os
from subprocess import check_output
from multiprocessing import Process


class ExampleServerProcess(Process):

    def __init__(self, example, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.example = example

    def run(self) -> None:

        # exec(open(self.example).read())
        # os.popen('python ' + self.example)
        # os.popen('python3 ' + self.example, )
        o = check_output('/home/jpcaram/cloud/tornadowebsockets/venv/bin/python3 ' + self.example)


class TestBasics(unittest.TestCase):

    def setUp(self) -> None:
        self.path = Path(__file__).parent.parent
        print(self.path)
        opts = Options()
        opts.headless = True
        self.browser = Firefox(options=opts)

    def test_basic_example(self):

        # s = ExampleServerProcess(str(self.path) + '/examples/basic.py')
        # s.start()
        # sleep(1)

        # opts = Options()
        # opts.headless = True
        # self.browser = Firefox(options=opts)

        # Get the assets
        self.browser.get('http://localhost:8881')
        sleep(1)  # The above does not block. So wait.
        results = self.browser.find_elements_by_class_name('widget')
        self.assertEqual(len(results), 2)

        # Initial value
        val0 = results[1].get_property('value')
        self.assertEqual(val0, 'The value')

        # Click on button
        results[0].click()
        val1 = results[1].get_property('value')

        # Final value
        self.assertEqual(val1, 'Hello!')

        # s.terminate()

    def tearDown(self) -> None:
        self.browser.close()