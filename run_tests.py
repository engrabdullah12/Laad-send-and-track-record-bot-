"""
Discovers every tests/test_lead_submission_*.py module, runs its run(driver)
function through the proxied Chrome driver, and writes a lead-submission
status report. No PageSpeed / timing logic here by design.
"""

import importlib
import pkgutil
import sys
import traceback

from driver_factory import get_driver
from reporting import LeadSubmissionReport

import tests as tests_package


def discover_site_modules():
    modules = []
    for _, name, _ in pkgutil.iter_modules(tests_package.__path__):
        if name.startswith("test_"):
            modules.append(name)
    return modules


def run_all(headless: bool = True) -> LeadSubmissionReport:
    report = LeadSubmissionReport()
    module_names = discover_site_modules()

    if not module_names:
        print("[run_tests] No test_*.py files found in tests/.")
        return report

    for module_name in module_names:
        module = importlib.import_module(f"tests.{module_name}")
        if not hasattr(module, "run"):
            print(f"[run_tests] Skipping module {module_name} (no 'run' function)")
            continue
        site_name = getattr(module, "SITE_NAME", module_name)

        driver = None
        try:
            driver = get_driver(headless=headless)
            success, message = module.run(driver)
            report.record(site_name, success, message)
            print(f"[run_tests] {site_name}: {'PASS' if success else 'FAIL'} - {message}")
        except Exception:
            err = traceback.format_exc()
            report.record(site_name, False, f"Unhandled exception:\n{err}")
            print(f"[run_tests] {site_name}: FAIL - unhandled exception")
        finally:
            if driver is not None:
                driver.quit()

    report.save()
    summary = report.summary()
    print(f"[run_tests] Summary: {summary}")
    return report


if __name__ == "__main__":
    headless_flag = "--no-headless" not in sys.argv
    run_all(headless=headless_flag)
