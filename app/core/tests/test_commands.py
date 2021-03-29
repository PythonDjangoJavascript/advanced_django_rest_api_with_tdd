from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandsTestCase(TestCase):
    """Test wait for db method is executing when calling"""

    def test_wait_for_db_ready(self):
        """Test wait for db actually get called when calling"""

        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = True  # Setting db connection true (mocking)

            # Calling our wait for db command
            call_command("wait_for_db")

            self.assertEqual(gi.call_count, 1)

    # Mocking default time function to avoid actual waiting time
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):  # here ts is for patch decoration
        """Test if connection failed multiple times"""

        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            # setting connection errror as side effect list
            gi.side_effect = [OperationalError] * 5 + [True]

            # Now it should raise OP error 5 time before showing db connected
            call_command("wait_for_db")

            self.assertEqual(gi.call_count, 6)
