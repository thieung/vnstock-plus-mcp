#!/usr/bin/env python3
"""
install_vnstock_data.py — Direct vnstock_data installer for Docker

Bypasses the full CLI installer. Directly:
1. Gets device ID from vnai
2. Registers device with vnstocks.com API
3. Downloads vnstock_data package
4. Installs it with pip
"""
import os
import sys
import json
import platform
import tempfile
import tarfile
import shutil
import subprocess
import requests
from datetime import datetime

BASE_URL = "https://vnstocks.com"


def get_device_id():
    """Get device ID using vnai (must be pre-installed)"""
    from vnai.scope.profile import inspector
    return inspector.fingerprint()


def register_device(api_key, device_id):
    """Register device with vnstocks.com (matches original installer format)"""

    system_info = {
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

    payload = {
        'api_key': api_key,
        'device_id': device_id,
        'device_name': platform.node(),
        'os_type': platform.system().lower(),
        'os_version': platform.release(),
        'machine_info': system_info
    }

    try:
        resp = requests.post(
            f'{BASE_URL}/api/vnstock/auth/device-register',
            json=payload,
            timeout=30
        )

        if resp.status_code == 200:
            data = resp.json()
            tier = data.get('tier', 'unknown')
            print(f"✅ Device registered! Tier: {tier}")
            return True
        else:
            error = resp.json().get('error', f'HTTP {resp.status_code}')
            print(f"⚠️  Device registration: {error} (continuing anyway)")
            return True  # Don't block on registration failure
    except Exception as e:
        print(f"⚠️  Device registration error: {e} (continuing anyway)")
        return True


def download_and_install(api_key, device_id, package_name="vnstock_data"):
    """Download and install a vnstock package"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Get download URL
    payload = {
        'device_id': device_id,
        'package_name': package_name
    }

    print(f"📦 Requesting download URL for {package_name}...")
    resp = requests.post(
        f'{BASE_URL}/api/vnstock/packages/download',
        json=payload,
        headers=headers,
        timeout=30
    )

    if resp.status_code != 200:
        error = resp.json().get('error', f'HTTP {resp.status_code}')
        print(f"❌ Failed to get download URL: {error}")
        return False

    download_url = resp.json()['downloadUrl']

    # Download package
    print(f"📥 Downloading {package_name}...")
    dl_resp = requests.get(download_url, timeout=300)
    if dl_resp.status_code != 200:
        print(f"❌ Download failed: HTTP {dl_resp.status_code}")
        return False

    print(f"   Downloaded {len(dl_resp.content)} bytes")

    # Save and extract
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tmp.write(dl_resp.content)
        tmp_path = tmp.name

    try:
        extract_dir = tempfile.mkdtemp(prefix=f'{package_name}_')

        with tarfile.open(tmp_path, 'r:gz') as tar:
            tar.extractall(path=extract_dir)

        # Find setup.py or pyproject.toml
        setup_dir = None
        for root, dirs, files in os.walk(extract_dir):
            if 'setup.py' in files or 'pyproject.toml' in files:
                setup_dir = root
                break

        if not setup_dir:
            print(f"❌ No setup.py/pyproject.toml found in {package_name}")
            return False

        # Install with pip
        print(f"🔧 Installing {package_name}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-q', setup_dir],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"❌ pip install failed: {result.stderr[:200]}")
            return False

        # Verify import
        try:
            __import__(package_name)
            print(f"✅ {package_name} installed and verified!")
            return True
        except ImportError as e:
            print(f"❌ {package_name} installed but import failed: {e}")
            return False

    finally:
        os.unlink(tmp_path)
        shutil.rmtree(extract_dir, ignore_errors=True)


def setup_config_files(api_key, device_id):
    """Create ~/.vnstock config files required by vnstock_data package.

    The package checks these files during import/install:
    - api_key.json: API key for authentication
    - user.json: User profile + device info
    """
    config_dir = os.path.expanduser("~/.vnstock")
    os.makedirs(config_dir, exist_ok=True)

    # Save API key
    api_key_path = os.path.join(config_dir, "api_key.json")
    with open(api_key_path, 'w') as f:
        json.dump({'api_key': api_key}, f, indent=2)

    # Get user profile from API
    username, email = "vnstock_user", "unknown"
    try:
        resp = requests.get(
            f'{BASE_URL}/api/vnstock/user/profile',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            username = data.get('username', 'vnstock_user')
            email = data.get('email', 'unknown')
    except Exception:
        pass

    # Save user info
    import socket
    import uuid

    user_info = {
        "user": username,
        "email": email,
        "uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname())),
        "os": platform.system(),
        "os_version": platform.version(),
        "ip": "unknown",
        "cwd": os.getcwd(),
        "python": {
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable,
            "is_virtual_env": False,
            "virtual_env_path": None
        },
        "time": datetime.now().isoformat(),
        "device_id": device_id,
        "hardware_uuid": "docker-container",
        "mac_address": "unknown"
    }

    user_path = os.path.join(config_dir, "user.json")
    with open(user_path, 'w') as f:
        json.dump(user_info, f, indent=2)

    print(f"📝 Config files created at {config_dir}")


def main():
    api_key = os.getenv('VNSTOCK_API_KEY')
    if not api_key:
        print("❌ VNSTOCK_API_KEY not set")
        sys.exit(1)

    # Check if already installed
    try:
        import vnstock_data
        print("✅ vnstock_data already installed")
        sys.exit(0)
    except ImportError:
        pass

    print("🔧 Installing vnstock_data (Bronze+ tier)...")

    # Step 1: Get device ID
    try:
        device_id = get_device_id()
        print(f"🔍 Device ID: {device_id[:16]}...")
    except ImportError:
        print("❌ vnai not installed — cannot get device ID")
        sys.exit(1)

    # Step 2: Register device
    register_device(api_key, device_id)

    # Step 3: Create config files (~/.vnstock/api_key.json, user.json)
    setup_config_files(api_key, device_id)

    # Step 4: Download and install vnstock_data
    if download_and_install(api_key, device_id, "vnstock_data"):
        print("🎉 vnstock_data installation complete!")
    else:
        print("⚠️  vnstock_data installation failed. Free-tier tools still available.")
        sys.exit(1)


if __name__ == "__main__":
    main()
