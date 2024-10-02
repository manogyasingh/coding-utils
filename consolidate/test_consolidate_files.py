import unittest
import os
import tempfile
from consolidate_files import load_gitignore_patterns, is_binary_file, should_ignore

class TestConsolidateFiles(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.input_dir = self.test_dir.name

        # Create sample files
        self.text_file = os.path.join(self.input_dir, 'test.txt')
        with open(self.text_file, 'w', encoding='utf-8') as f:
            f.write("This is a test file.")

        self.binary_file = os.path.join(self.input_dir, 'image.png')
        with open(self.binary_file, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00')

        # Create a .gitignore file
        self.gitignore_file = os.path.join(self.input_dir, '.gitignore')
        with open(self.gitignore_file, 'w', encoding='utf-8') as f:
            f.write("*.log\nimage.png\n")

    def tearDown(self):
        # Close the TemporaryDirectory
        self.test_dir.cleanup()

    def test_load_gitignore_patterns(self):
        spec = load_gitignore_patterns(self.input_dir)
        self.assertIsNotNone(spec)
        # Check if 'image.png' is ignored
        self.assertTrue(spec.match_file('image.png'))
        # Check if 'test.txt' is not ignored
        self.assertFalse(spec.match_file('test.txt'))

    def test_is_binary_file(self):
        self.assertFalse(is_binary_file(self.text_file))
        self.assertTrue(is_binary_file(self.binary_file))

    def test_should_ignore(self):
        spec = load_gitignore_patterns(self.input_dir)
        self.assertTrue(should_ignore(self.binary_file, spec, self.input_dir))
        self.assertFalse(should_ignore(self.text_file, spec, self.input_dir))

    def test_consolidate_files_skips_ignored_and_binary(self):
        # Import the consolidate_files function
        from consolidate_files import consolidate_files

        # Create an output file path
        output_file = os.path.join(self.input_dir, 'summarised.txt')

        # Run consolidation
        consolidate_files(
            input_dir=self.input_dir,
            output_file=output_file,
            include_subdirs=True,
            spec=load_gitignore_patterns(self.input_dir),
            extensions=None
        )

        # Read the output file
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ensure that 'test.txt' is included and 'image.png' is not
        self.assertIn('test.txt', content)
        self.assertNotIn('image.png', content)
        self.assertIn("This is a test file.", content)

if __name__ == '__main__':
    unittest.main()
