
import os
import unittest

from ..pytupi.core import config_manager


class TestConfigManager(unittest.TestCase):

    def test_load_file(self):
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config_file_test.json')
        m_config = config_manager.ConfigManager(config_file)
        self.assertIsNone(m_config._configurations)
        m_config._load_config()
        self.assertIsNotNone(m_config._configurations)

    def test_check_config_keys(self):
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config_file_test.json')
        m_config = config_manager.ConfigManager(config_file)

        self.assertTrue(m_config.has_config_key('mail'))
        self.assertTrue(m_config.has_config_key('datasets'))
        self.assertFalse(m_config.has_config_key('not_this'))

    def test_basic_config(self):
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config_file_test.json')
        m_config = config_manager.ConfigManager(config_file)
        self.assertTrue(m_config.has_config_key('mail'))
        mail_config = m_config.get_config('mail')
        self.assertIsNotNone(mail_config)
        self.assertEqual(mail_config['user'], 'abc')
        self.assertEqual(mail_config['password'], '123')
