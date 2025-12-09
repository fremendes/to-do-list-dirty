"""Custom Django test runner that exports results to JSON."""

import json
import time
import unittest
from datetime import datetime

from django.test.runner import DiscoverRunner


class JSONTestResult(unittest.TextTestResult):
    """Custom test result class that captures test outcomes."""

    def __init__(self, *args, **kwargs):
        """Initialize the test result."""
        super().__init__(*args, **kwargs)
        self.test_results = []

    def startTest(self, test):
        """Called when a test starts."""
        super().startTest(test)

    def addSuccess(self, test):
        """Called when a test passes."""
        super().addSuccess(test)
        self._add_result(test, 'passed', None)

    def addError(self, test, err):
        """Called when a test has an error."""
        super().addError(test, err)
        self._add_result(test, 'error', self._exc_info_to_string(err, test))

    def addFailure(self, test, err):
        """Called when a test fails."""
        super().addFailure(test, err)
        self._add_result(test, 'failed', self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        """Called when a test is skipped."""
        super().addSkip(test, reason)
        self._add_result(test, 'skipped', reason)

    def _add_result(self, test, status, error_message):
        """Add a test result to the list."""
        test_method = getattr(test, test._testMethodName, None)
        test_number = getattr(test_method, 'test_number', None)

        self.test_results.append({
            'test_id': test_number,
            'test_class': test.__class__.__name__,
            'test_method': test._testMethodName,
            'test_name': f"{test.__class__.__name__}.{test._testMethodName}",
            'status': status,
            'error_message': error_message,
            'description': test_method.__doc__.strip() if test_method and test_method.__doc__ else None
        })


class JSONTestRunner(DiscoverRunner):
    """
    Custom test runner that exports test results to result_test_auto.json.

    Usage:
        python manage.py test --testrunner=tests.json_test_runner.JSONTestRunner
    """

    def __init__(self, *args, **kwargs):
        """Initialize the test runner."""
        super().__init__(*args, **kwargs)
        self.json_result = None
        self.start_time = None
        self.end_time = None

    def get_resultclass(self):
        """Return the custom result class."""
        return JSONTestResult

    def run_suite(self, suite, **kwargs):
        """Run the test suite and capture results."""
        self.start_time = time.time()

        # Run tests with custom result class
        result = super().run_suite(suite, **kwargs)

        self.end_time = time.time()
        self.json_result = result

        # Export results to JSON
        self._export_to_json(result)

        return result

    def _export_to_json(self, result):
        """Export test results to JSON file."""
        if not hasattr(result, 'test_results'):
            print("Warning: Result object doesn't have test_results attribute")
            return

        output = {
            'timestamp': datetime.now().isoformat(),
            'duration': round(self.end_time - self.start_time, 3),
            'total_tests': len(result.test_results),
            'summary': {
                'passed': sum(1 for t in result.test_results if t['status'] == 'passed'),
                'failed': sum(1 for t in result.test_results if t['status'] == 'failed'),
                'errors': sum(1 for t in result.test_results if t['status'] == 'error'),
                'skipped': sum(1 for t in result.test_results if t['status'] == 'skipped')
            },
            'tests': result.test_results
        }

        with open('result_test_auto.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        if self.verbosity >= 1:
            print("\n✓ Test results exported to result_test_auto.json")
            print(f"  Total: {output['total_tests']}, "
                  f"Passed: {output['summary']['passed']}, "
                  f"Failed: {output['summary']['failed']}, "
                  f"Errors: {output['summary']['errors']}")
