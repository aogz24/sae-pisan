#!/usr/bin/env python3
"""
Simple test runner script for SAE EBLUP Area unit tests.
This script provides a user-friendly way to run tests with proper formatting.
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    """Print a nice header for the test run."""
    print("=" * 80)
    print("🧪 SAE EBLUP AREA UNIT TESTS")
    print("🎯 Testing Framework: pytest")
    print("📋 Pattern: AAA (Arrange-Act-Assert)")
    print("=" * 80)
    print()

def print_footer(success: bool, test_count: int = None):
    """Print test results summary."""
    print("\n" + "=" * 80)
    if success:
        print("✅ ALL TESTS PASSED!")
        if test_count:
            print(f"🎉 {test_count} tests completed successfully!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please review the failures above")
    print("=" * 80)

def check_pytest():
    """Check if pytest is available."""
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pytest found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest not found!")
        print("📦 Installing pytest...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
            print("✅ pytest installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install pytest")
            print("💡 Please install manually: pip install pytest")
            return False

def run_tests():
    """Run the unit tests."""
    # Test file path
    test_file = Path("test/modelling/script/test_sae_eblup_area_new.py")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"📁 Test file: {test_file}")
    print("🚀 Running tests...\n")
    
    # Run pytest with nice formatting
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "--verbose",                # Verbose output
        "--tb=short",              # Short traceback format
        "--color=yes",             # Colored output
        "--disable-warnings",      # Disable warnings for cleaner output
        "--durations=5",           # Show 5 slowest tests
        "--no-header",             # No pytest header
        "--no-summary"             # No summary info
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main function."""
    print_header()
    
    # Check dependencies
    if not check_pytest():
        return 1
    
    print(f"📂 Working directory: {os.getcwd()}")
    print()
    
    # Run tests
    success = run_tests()
    
    # Print results
    print_footer(success)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
