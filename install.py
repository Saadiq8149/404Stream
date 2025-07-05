import os, shutil, urllib.request, subprocess, ctypes, configparser, sys, json
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("🛡️ Requesting administrator privileges...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)
    sys.exit()

# -------------------- Paths --------------------
INSTALL_DIR = Path(os.environ['LOCALAPPDATA']) / "404Stream"
VLC_PATH = Path(r"C:\Program Files\VideoLAN\VLC\vlc.exe")
QBIT_PATH = Path(r"C:\Program Files\qBittorrent\qbittorrent.exe")
QBIT_CONFIG_PATH = Path(os.environ["APPDATA"]) / "qBittorrent" / "qBittorrent.ini"

# -------------------- URLs --------------------
VLC_URL = "https://get.videolan.org/vlc/3.0.20/win64/vlc-3.0.20-win64.exe"
QBIT_URL = "https://sourceforge.net/projects/qbittorrent/files/latest/download"

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
    if not VLC_PATH.exists():
        print("🎥 VLC not found, downloading and installing...")
        download_and_install("VLC", VLC_URL, "vlc_inst.exe", ["/L=1033", "/S"])
    else:
        print("🎥 VLC already installed, skipping download.")
    if not QBIT_PATH.exists():
        print("🔁 qBittorrent not found, downloading and installing...")
        download_and_install("qBittorrent", QBIT_URL, "qbit_inst.exe", ["/S"])
    else:
        print("🔁 qBittorrent already installed, skipping download.")
    configure_vlc_path()

def broadcast_env_update():
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, None
    )

def configure_vlc_path():
    print("⚙️ Configuring VLC PATH...")
    try:
        vlc_dir = VLC_PATH.parent
        try:
            result = subprocess.run(["vlc", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ VLC already accessible via PATH")
                return
        except:
            pass

        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
        try:
            current_path, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path = ""
        vlc_dir_str = str(vlc_dir)
        if vlc_dir_str.lower() not in current_path.lower():
            new_path = f"{current_path};{vlc_dir_str}" if current_path else vlc_dir_str
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            broadcast_env_update()
            print(f"✅ Added VLC to PATH: {vlc_dir_str}")
        else:
            print("✅ VLC directory already in PATH")
        winreg.CloseKey(key)
        create_vlc_config()
    except Exception as e:
        print(f"⚠️  Failed to configure VLC PATH: {e}")
        create_vlc_config()

def create_vlc_config():
    try:
        vlc_config_path = INSTALL_DIR / "vlc_config.json"
        vlc_config = {
            "vlc_path": str(VLC_PATH),
            "vlc_directory": str(VLC_PATH.parent),
            "added_to_path": True
        }
        with open(vlc_config_path, 'w') as f:
            json.dump(vlc_config, f, indent=2)
        print(f"✅ VLC config created: {vlc_config_path}")
    except Exception as e:
        print(f"⚠️  Failed to create VLC config: {e}")

def configure_qbittorrent():
    print("⚙️ Configuring qBittorrent Web UI...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "qbittorrent.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        QBIT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        config_content = """[Preferences]
General\\CloseToTrayNotified=true
WebUI\\Enabled=true
WebUI\\Password_PBKDF2="@ByteArray(xt7ArTjDRrqVhQvf+AabZA==:oE8KHpNNPJD7kRj9U5Uzy9fI7KjTK3/+mw/+P3Fl4q8WC+eSc3VfJQ+4SdLkOiOvocWDqLLJ6d9xzfAoUOZluw==)"
WebUI\\LocalHostAuth=false
WebUI\\Port=8080
WebUI\\Username=admin
WebUI\\UseUPnP=false
WebUI\\CSRFProtection=false
"""

        with open(QBIT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(config_content)

        os.chmod(QBIT_CONFIG_PATH, 0o444)  # Read-only
        print("✅ qBittorrent Web UI configured.")
        print("   🔒 Made qBittorrent config read-only.")
        print("   Username: admin")
        print("   Password: admin")
        print("   Port: 8080")

    except Exception as e:
        print(f"⚠️  Failed to configure qBittorrent: {e}")
        print("You may need to configure Web UI manually in settings.")

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
        except Exception as e:
            print(f"❌ Unexpected error installing requirements: {e}")
    else:
        print("⚠️  No requirements.txt found.")
        flag_path.touch()

def run():
    print("🚀 Installing 404Stream backend…")
    try:
        create_install_dir()
        copy_files()
        check_and_install_deps()
        configure_qbittorrent()
        install_requirements()

        ctypes.windll.user32.MessageBoxW(
            0,
            "404Stream installed successfully!\n\nYou can now launch using launcher.exe",
            "Installation Complete",
            0
        )
        print("🎉 Installation completed successfully!")
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Installation failed!\n\nError: {e}",
            "Installation Error",
            16
        )
        raise

if __name__ == "__main__":
    run()
