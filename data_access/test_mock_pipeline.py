"""
Test script for ERA5 pipeline mock processing.
Tests the workflow without downloading actual data.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Get the data_access directory
DATA_ACCESS_DIR = Path(__file__).parent

def run_test(test_name: str, command: list[str]) -> bool:
    """
    Run a test command and report results.
    
    Parameters
    ----------
    test_name : str
        Name of the test
    command : list[str]
        Command to run
    
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Command: {' '.join(command)}\n")
    
    try:
        result = subprocess.run(
            command,
            cwd=DATA_ACCESS_DIR,
            capture_output=False,
            text=True
        )
        
        success = result.returncode == 0
        print(f"\nResult: {'✓ PASSED' if success else '✗ FAILED'}")
        return success
        
    except Exception as e:
        print(f"\nResult: ✗ FAILED - {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ERA5 PIPELINE - MOCK PROCESSING TESTS")
    print("="*70)
    
    results = []
    
    # Test 1: Process single date with mock
    results.append(run_test(
        "Single date processing (2024-12-01) with mock",
        [sys.executable, "era5_pipeline.py", "2024-12-01", "--mock"]
    ))
    
    # Test 2: Process date range with mock
    results.append(run_test(
        "Date range processing (2024-12-01 to 2024-12-03) with mock",
        [sys.executable, "era5_pipeline.py", "--start", "2024-12-01", "--end", "2024-12-03", "--mock"]
    ))
    
    # Test 3: Default processing (should find oldest missing)
    results.append(run_test(
        "Default processing (find oldest missing) with mock",
        [sys.executable, "era5_pipeline.py", "--mock"]
    ))
    
    # Test 4: Find missing flag
    results.append(run_test(
        "Find missing flag with mock",
        [sys.executable, "era5_pipeline.py", "--find-missing", "--mock"]
    ))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    print("="*70 + "\n")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
