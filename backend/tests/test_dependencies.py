"""
Test dependency compatibility and environment setup
Phase 19.6: Added to catch CI/CD dependency conflicts early

These tests verify that:
1. All installed packages have compatible dependencies
2. Critical packages can be imported
3. Version requirements are met
"""
import subprocess
import sys
import pytest


def test_pip_check():
    """
    Ensure no dependency conflicts in installed packages
    
    This test catches issues like:
    - pytest 7.4.3 conflicting with pytest-asyncio 0.24.0
    - Incompatible version constraints
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True
    )
    
    # If conflicts exist, pip check will have non-zero exit code
    assert result.returncode == 0, (
        f"Dependency conflicts found:\n"
        f"STDOUT: {result.stdout}\n"
        f"STDERR: {result.stderr}\n\n"
        f"This usually means incompatible package versions in requirements.txt"
    )


def test_pytest_version_compatibility():
    """
    Ensure pytest version is compatible with pytest-asyncio
    
    pytest-asyncio 0.24.x requires pytest >= 8.0.0
    """
    import pytest as pt
    try:
        import pytest_asyncio
        asyncio_version = pytest_asyncio.__version__
    except ImportError:
        pytest.skip("pytest-asyncio not installed")
    
    pytest_version = tuple(map(int, pt.__version__.split('.')[:2]))
    
    # Check compatibility
    if asyncio_version.startswith('0.24.'):
        assert pytest_version >= (8, 0), (
            f"pytest {pt.__version__} is incompatible with pytest-asyncio {asyncio_version}. "
            f"pytest-asyncio 0.24.x requires pytest >= 8.0.0"
        )
    elif asyncio_version.startswith('0.21.'):
        assert pytest_version >= (7, 0), (
            f"pytest {pt.__version__} is incompatible with pytest-asyncio {asyncio_version}. "
            f"pytest-asyncio 0.21.x requires pytest >= 7.0.0"
        )


def test_critical_imports():
    """
    Test that all critical packages can be imported
    
    This catches missing dependencies or broken installations
    """
    critical_packages = {
        'fastapi': 'FastAPI web framework',
        'sqlalchemy': 'Database ORM',
        'playwright': 'Browser automation',
        'apscheduler': 'Job scheduling',
        'pytest': 'Testing framework',
        'pytest_asyncio': 'Async test support',
        'pytest_cov': 'Coverage reporting',
    }
    
    failures = []
    for package, description in critical_packages.items():
        try:
            __import__(package)
        except ImportError as e:
            failures.append(f"{package} ({description}): {e}")
    
    assert not failures, (
        f"Failed to import critical packages:\n" +
        "\n".join(f"  - {f}" for f in failures)
    )


def test_python_version():
    """Ensure Python 3.13+ is being used"""
    assert sys.version_info >= (3, 13), (
        f"Python 3.13+ required for this project. "
        f"Currently using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )


def test_package_versions():
    """
    Verify specific package versions match requirements
    
    This helps catch accidental upgrades or downgrades
    """
    import pytest as pt
    
    # Critical version requirements
    pytest_version = tuple(map(int, pt.__version__.split('.')[:2]))
    
    # pytest must be 8.x for our pytest-asyncio version
    assert pytest_version[0] == 8, (
        f"pytest major version should be 8.x, got {pt.__version__}. "
        f"This is required for pytest-asyncio 0.24.x compatibility."
    )


def test_test_dependencies_available():
    """Ensure all testing tools are available"""
    test_packages = [
        'pytest',
        'pytest_asyncio',
        'pytest_cov',
        'pytest_timeout',
    ]
    
    for package in test_packages:
        try:
            __import__(package)
        except ImportError:
            pytest.fail(
                f"Test dependency '{package}' not available. "
                f"Make sure it's in requirements.txt and installed."
            )


if __name__ == "__main__":
    # Allow running tests standalone
    print("Testing dependencies...")
    print("=" * 60)
    
    # Test 1: pip check
    print("\n1. Checking for dependency conflicts...")
    result = subprocess.run([sys.executable, "-m", "pip", "check"])
    if result.returncode == 0:
        print("   ✅ No conflicts found")
    else:
        print("   ❌ Conflicts detected!")
        sys.exit(1)
    
    # Test 2: Critical imports
    print("\n2. Testing critical imports...")
    try:
        import pytest
        import pytest_asyncio
        import pytest_cov
        import fastapi
        import sqlalchemy
        print("   ✅ All critical packages importable")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        sys.exit(1)
    
    # Test 3: Version check
    print("\n3. Checking version compatibility...")
    import pytest as pt
    import pytest_asyncio
    print(f"   pytest: {pt.__version__}")
    print(f"   pytest-asyncio: {pytest_asyncio.__version__}")
    
    pytest_ver = tuple(map(int, pt.__version__.split('.')[:2]))
    if pytest_ver >= (8, 0):
        print("   ✅ Versions compatible")
    else:
        print("   ❌ pytest version too old for pytest-asyncio 0.24.x")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All dependency tests passed!")

