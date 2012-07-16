#!/usr/bin/env python
import unittest
import scanner

class TestFtpTester(unittest.TestCase):
    """Some test for the prober, the ping prober and the ftp prober
    """
    FTP_ADDRESS = "62.220.135.248"
    NOT_FTP_ADDRESS = "56.3.23.3"
    DOWN_HOST = "kadkjfkjahdskfjhsadkjfsadkfhsakjdhfakjs.comff"
    UP_HOST = "google.ch"

    def test_login_test_bad(self):
        ftp_up = scanner.test_by_login(TestFtpTester.NOT_FTP_ADDRESS, timeout=3)
        self.assertFalse(ftp_up)

    def test_login_test(self):
        ftp_up = scanner.test_by_login(TestFtpTester.FTP_ADDRESS, timeout=3)
        self.assertTrue(ftp_up)

    def test_ping_bad(self):
        ping_avg = scanner.ping(TestFtpTester.DOWN_HOST)
        self.assertEqual(ping_avg, 0)

    def test_ping(self):
        ping_avg = scanner.ping(TestFtpTester.UP_HOST)
        self.assertNotEqual(ping_avg, 0)
        self.assertGreater(ping_avg, 0)

if __name__ == "__main__":
    unittest.main()
