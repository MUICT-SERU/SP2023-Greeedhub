import os
from unittest import TestCase
from unittest.mock import Mock, patch

from unittest_additions import TestFile


TEST_FILE = 'deleteme.tmp'
TEST_DATA = 'some data'


class TestFileTestCase(TestCase):
    def test_context_manager_creates_and_deletes_file_as_expected(self):
        self.assertFalse(os.path.exists(TEST_FILE))

        with TestFile(TEST_FILE, TEST_DATA):
            self.assertTrue(os.path.exists(TEST_FILE))

        self.assertFalse(os.path.exists(TEST_FILE))

    def test_temporary_file_is_created_with_provided_content(self):
        with TestFile(TEST_FILE, TEST_DATA):
            with open(TEST_FILE, 'r') as f:
                self.assertEqual(f.read(), TEST_DATA)

    def test_temporary_file_append_adds_data_to_the_file(self):
        MORE_DATA = ' more data'
        with TestFile(TEST_FILE, TEST_DATA) as tf:
            with open(TEST_FILE, 'r') as f:
                self.assertEqual(f.read(), TEST_DATA)
            
            tf.append(MORE_DATA)

            with open(TEST_FILE, 'r') as f:
                self.assertEqual(f.read(), TEST_DATA + MORE_DATA)

    def test_assertion_error_if_target_file_already_exists(self):
        with TestFile(TEST_FILE, TEST_DATA):
            with self.assertRaisesRegex(AssertionError, f'Temporary file target already exists: {TEST_FILE}'):
                TestFile(TEST_FILE, TEST_DATA)

    def test_assertion_error_if_file_cannot_be_destroyed(self):
        with patch('os.remove'):
            with self.assertRaisesRegex(AssertionError, f'Failed to delete temporary file: {TEST_FILE}'):
                with TestFile(TEST_FILE, TEST_DATA):
                    os.remove(TEST_FILE)

        os.remove(TEST_FILE)