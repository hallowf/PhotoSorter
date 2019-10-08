import unittest

from argparse import Namespace

from src.cmd_main import verify_required
from src.core.custom_exceptions import WhyWouldYou, DirMissing, OutDirNotEmpty


class TestCLIVerifier(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
      if not os.path.isdir("TEST_IMAGES"):
        os.mkdir("TEST_IMAGES")
      if not os.path.isdir("TEST_OUTPUT"):
        os.mkdir("TEST_OUTPUT")


    def test_raises_on_missing_source(self):
        """
        Test that check ifs an exception is raised
        when the source directory does not exist
        """
        args = Namespace(from_dir="/a_path_that_does_not_exist",
                         skip_copy=False,
                         sort_remaining=False,
                         split_by=None,
                         to_dir="")
        with self.assertRaises(DirMissing):
            verify_required(args)

    def test_raises_on_insufficient_files(self):
        """
        Checks that there are enough files
        in the source directory to process
        """
        args = Namespace(from_dir="./TEST_IMAGES",
                         skip_copy=False,
                         sort_remaining=False,
                         split_by=None,
                         to_dir="")
        with self.assertRaises(WhyWouldYou):
            verify_required(args)



if __name__ == "__main__":
    unittest.main()
