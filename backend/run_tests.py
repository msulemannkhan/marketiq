"""Test runner for the Review Intelligence System"""

import subprocess
import sys
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def check_api_health():
    """Check if API is healthy"""
    port = os.getenv("BACKEND_PORT", "8005")
    api_url = f"http://localhost:{port}"

    try:
        response = requests.get(f"{api_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ API is healthy: {response.json().get('status')}")
            return True, api_url
        print(f"✗ API unhealthy: {response.status_code}")
        return False, api_url
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return False, api_url


def run_tests(test_type="basic"):
    """Run tests"""
    healthy, api_url = check_api_health()
    if not healthy:
        print("Start the API first: docker-compose up -d")
        return False

    if test_type == "docker":
        # Run tests inside Docker
        cmd = ["docker", "exec", "-t", "laptop_intelligence_backend_dev",
               "python", "-m", "pytest", "tests/", "-v"]
        result = subprocess.run(cmd)
        return result.returncode == 0

    # Basic API tests
    tests_passed = 0
    tests = [
        ("GET", "/api/v1/health", None, None, 200),
        ("GET", "/api/v1/products", None, None, 200),
        ("GET", "/api/v1/filters", None, None, 200),
        ("POST", "/api/v1/search", {"query": "laptop"}, None, 200),
    ]

    for method, endpoint, data, headers, expected_status in tests:
        try:
            url = f"{api_url}{endpoint}"
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=5)
            else:
                r = requests.post(url, json=data, headers=headers, timeout=5)

            if r.status_code == expected_status:
                print(f"✓ {method} {endpoint}")
                tests_passed += 1
            else:
                print(f"✗ {method} {endpoint} - Status: {r.status_code}")
        except Exception as e:
            print(f"✗ {method} {endpoint} - Error: {e}")

    print(f"\nTests: {tests_passed}/{len(tests)} passed")
    return tests_passed == len(tests)


def main():
    """Main entry point"""
    test_type = sys.argv[1] if len(sys.argv) > 1 else "basic"

    if test_type not in ["basic", "docker", "all"]:
        print("Usage: python run_tests.py [basic|docker|all]")
        sys.exit(1)

    success = True
    if test_type in ["basic", "all"]:
        success = run_tests("basic")

    if success and test_type in ["docker", "all"]:
        success = run_tests("docker")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()