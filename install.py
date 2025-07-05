import os, shutil, urllib.request, subprocess, ctypes, configparser, ctypes, sys
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("🛡️ Requesting administrator privileges...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{__file__}"', None, 1
    )
    sys.exit()


# -------------------- Paths --------------------
INSTALL_DIR = Path(os.environ['LOCALAPPDATA']) / "404Stream"
VLC_PATH = Path(r"C:\Program Files\VideoLAN\VLC\vlc.exe")
QBIT_PATH = Path(r"C:\Program Files\qBittorrent\qbittorrent.exe")
QBIT_CONFIG_PATH = Path(os.environ["APPDATA"]) / "qBittorrent" / "qBittorrent.ini"

# -------------------- URLs --------------------
VLC_URL = "https://get.videolan.org/vlc/3.0.20/win64/vlc-3.0.20-win64.exe"
QBIT_URL = (
    "https://sourceforge.net/projects/qbittorrent/files/latest/download"
)

# -------------------- Install Functions --------------------
def create_install_dir():
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Install directory: {INSTALL_DIR}")

def copy_files():
    src = Path(__file__).parent
    for item in src.iterdir():
        if item.name.lower() == "install.py":
            continue
        dest = INSTALL_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
    print("✅ App files copied.")

def download_and_install(name, url, exe_name, silent_args):
    temp = Path(os.environ["TEMP"]) / exe_name
    try:
        print(f"⬇️  Downloading {name}...")
        urllib.request.urlretrieve(url, temp)
        print(f"🚀 Installing {name}...")
        subprocess.run([str(temp)] + silent_args, check=True)
        temp.unlink()
        print(f"✅ {name} installed.")
    except Exception as e:
        print(f"❌ Failed to install {name}: {e}")
        if temp.exists():
            temp.unlink()
        raise

def check_and_install_deps():
    # Check and install VLC only if it doesn't exist
    if not VLC_PATH.exists():
        print("🎥 VLC not found, downloading and installing...")
        download_and_install("VLC", VLC_URL, "vlc_inst.exe", ["/L=1033", "/S"])
    else:
        print("🎥 VLC already installed, skipping download.")

    # Check and install qBittorrent only if it doesn't exist
    if not QBIT_PATH.exists():
        print("🔁 qBittorrent not found, downloading and installing...")
        download_and_install("qBittorrent", QBIT_URL, "qbit_inst.exe", ["/S"])
    else:
        print("🔁 qBittorrent already installed, skipping download.")

    # Configure VLC PATH after installation check
    configure_vlc_path()

def configure_vlc_path():
    """Add VLC to system PATH if not already there"""
    print("⚙️ Configuring VLC PATH...")
    try:
        vlc_dir = VLC_PATH.parent

        # Check if VLC is already in PATH
        try:
            result = subprocess.run(["vlc", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ VLC already accessible via PATH")
                return
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Add VLC to user PATH environment variable
        import winreg

        # Open user environment variables registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )

        try:
            # Get current PATH
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""

        # Check if VLC directory is already in PATH
        vlc_dir_str = str(vlc_dir)
        if vlc_dir_str.lower() not in current_path.lower():
            # Add VLC directory to PATH
            new_path = f"{current_path};{vlc_dir_str}" if current_path else vlc_dir_str
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ Added VLC to PATH: {vlc_dir_str}")
            print("   (May require restart or new terminal session)")
        else:
            print("✅ VLC directory already in PATH")

        winreg.CloseKey(key)

        # Also create a VLC config file for our backend
        create_vlc_config()

    except Exception as e:
        print(f"⚠️  Failed to configure VLC PATH: {e}")
        print("You may need to add VLC to PATH manually or use full path in backend")
        create_vlc_config()

def create_vlc_config():
    """Create a VLC configuration file for the backend"""
    try:
        vlc_config_path = INSTALL_DIR / "vlc_config.json"
        vlc_config = {
            "vlc_path": str(VLC_PATH),
            "vlc_directory": str(VLC_PATH.parent),
            "added_to_path": True
        }

        import json
        with open(vlc_config_path, 'w') as f:
            json.dump(vlc_config, f, indent=2)

        print(f"✅ VLC config created: {vlc_config_path}")

    except Exception as e:
        print(f"⚠️  Failed to create VLC config: {e}")

def configure_qbittorrent():
    print("⚙️ Checking qBittorrent Web UI configuration...")
    try:
        QBIT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Check if config already exists and is correct
        if QBIT_CONFIG_PATH.exists():
            try:
                config = configparser.ConfigParser()
                config.read(QBIT_CONFIG_PATH, encoding='utf-8')

                # Check if WebUI is enabled and configured correctly
                preferences = config.get('Preferences', fallback={}) if config.has_section('Preferences') else {}

                webui_enabled = config.get('Preferences', 'WebUI\\Enabled', fallback='false').lower() == 'true'
                webui_port = config.get('Preferences', 'webui\\port', fallback='')
                webui_username = config.get('Preferences', 'webui\\username', fallback='')

                if (webui_enabled and webui_port == '8080' and webui_username == 'admin'):
                    print("✅ qBittorrent Web UI already configured correctly.")
                    return
                else:
                    print("⚙️ qBittorrent config exists but needs updating...")
            except Exception as e:
                print(f"⚙️ Could not read existing config ({e}), will recreate...")

        # qBittorrent config content - exact format as shown
            config_content = """[Preferences]
            General\\CloseToTrayNotified=true
            WebUI\\Enabled=true
            webui\\password_ha1=@ByteArray(e64b78fc3bc91bcbc7dc232ba8ec59e0)
            WebUI\\Password_PBKDF2="@ByteArray(xt7ArTjDRrqVhQvf+AabZA==:oE8KHpNNPJD7kRj9U5Uzy9fI7KjTK3/+mw/+P3Fl4q8WC+eSc3VfJQ+4SdLkOiOvocWDqLLJ6d9xzfAoUOZluw==)"
            WebUI\\LocalHostAuth=false
            general\\locale=en
            webui\\useupnp=false
            webui\\port=8080
            webui\\username=admin
            webui\\usereverseproxy=false
            webui\\csrfprotection=false
            """

        # Write the config directly to avoid ConfigParser formatting issues
        with open(QBIT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(config_content)

        print("✅ qBittorrent Web UI configured.")
        print("   Username: admin")
        print("   Password: admin")
        print("   Port: 8080")

    except Exception as e:
        print(f"⚠️  Failed to configure qBittorrent: {e}")
        print("You may need to configure Web UI manually:")
        print("  1. Open qBittorrent")
        print("  2. Go to Tools → Options → Web UI")
        print("  3. Enable Web UI on port 8080")
        print("  4. Set username: admin, password: admin")

def install_requirements():
    req_path = INSTALL_DIR / "backend" / "requirements.txt"
    flag_path = INSTALL_DIR / ".requirements_installed"

    if flag_path.exists():
        print("✅ Requirements already installed.")
        return

    if req_path.exists():
        print("📦 Installing requirements...")
        try:
            subprocess.run(["pip", "install", "-r", str(req_path)], check=True)
            flag_path.touch()
            print("✅ Requirements installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            print("You may need to install them manually.")
        except Exception as e:
            print(f"❌ Unexpected error installing requirements: {e}")
    else:
        print("⚠️  No requirements.txt found.")
        # Create flag anyway since there's nothing to install
        flag_path.touch()

def run():
    print("🚀 Installing 404Stream backend…")

    try:
        check_and_install_deps()
        configure_qbittorrent()
        install_requirements()

        ctypes.windll.user32.MessageBoxW(
            0,
            "404Stream installed successfully!\n\nYou can now launch using laucher.exe",
            "Installation Complete",
            0
        )
        print("🎉 Installation completed successfully!")

    except Exception as e:
        error_msg = f"Installation failed: {e}"
        print(f"❌ {error_msg}")
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Installation failed!\n\nError: {e}\n\nPlease check the console for more details.",
            "Installation Error",
            16  # Error icon
        )
        raise

if __name__ == "__main__":
    run()
