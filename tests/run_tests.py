#!/usr/bin/env python3
"""
Test runner for the Dungeon Game.

Discovers and runs all test files in the tests/ directory with coloured output.

Usage:
  python tests/run_tests.py
"""

import sys
import os
import unittest

# Add the project root to sys.path so test files can import game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class that displays coloured dots."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.pass_count = 0
        self.fail_count = 0
        self.error_count = 0
        self.skipped_count = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.pass_count += 1
        self.stream.write('\033[92m●\033[0m')  # Green dot
        self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        self.error_count += 1
        self.stream.write('\033[91mE\033[0m')  # Red E
        self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.fail_count += 1
        self.stream.write('\033[91m●\033[0m')  # Red dot
        self.stream.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.skipped_count += 1
        self.stream.write('\033[93mS\033[0m')  # Yellow S
        self.stream.flush()

    def printSummary(self):
        """Print test summary."""
        self.stream.writeln('\n')
        self.stream.writeln(f'Tests: {self.testsRun}')
        self.stream.writeln(f'\033[92mPassed: {self.pass_count}\033[0m')
        if self.fail_count > 0:
            self.stream.writeln(f'\033[91mFailed: {self.fail_count}\033[0m')
        else:
            self.stream.writeln(f'Failed: {self.fail_count}')
        if self.error_count > 0:
            self.stream.writeln(f'\033[91mErrors: {self.error_count}\033[0m')
        else:
            self.stream.writeln(f'Errors: {self.error_count}')
        if self.skipped_count > 0:
            self.stream.writeln(f'\033[93mSkipped: {self.skipped_count}\033[0m')
        else:
            self.stream.writeln(f'Skipped: {self.skipped_count}')


class ColoredTextTestRunner(unittest.TextTestRunner):
    """Test runner that uses ColoredTextTestResult."""

    def __init__(self, stream=None, descriptions=True, verbosity=1):
        if stream is None:
            stream = sys.stderr
        self.stream = stream
        super().__init__(stream, descriptions, verbosity,
                        resultclass=ColoredTextTestResult)

    def run(self, test):
        """Run the test with our custom result class."""
        result = super().run(test)
        result.printSummary()
        return result


def run_tests():
    """Run all tests and display coloured results.

    Returns:
        bool: True if all tests passed, False otherwise.
    """
    print("=== Running Tests ===")

    # Discover all tests in the tests/ directory
    loader = unittest.TestLoader()
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(tests_dir)

    # Run the tests with coloured output
    runner = ColoredTextTestRunner(verbosity=1)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
