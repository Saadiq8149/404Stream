import subprocess
import os
import sys
import time
import threading
import colorama
from colorama import Fore
from pathlib import Path

import uvicorn

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR
REQUIREMENTS_PATH = str(PROJECT_DIR / "backend" / "requirements.txt")
QBITTORRENT_PATH = r"C:\Program Files\qBittorrent\qbittorrent.exe"

def show_banner():
    # Initialize colorama
    colorama.init(autoreset=True)

    # Display fancy bootup text
    print(f"\n{Fore.CYAN}{'█'*60}")
    print(f"{Fore.CYAN}█{' '*58}█")
    print(f"{Fore.CYAN}█  {Fore.RED}██   ██  ██████  ██   ██                              {Fore.CYAN}  █")
    print(f"{Fore.CYAN}█  {Fore.RED}██   ██ ██  ████ ██   ██                              {Fore.CYAN}  █")
    print(f"{Fore.CYAN}█  {Fore.RED}███████ ██ ██ ██ ███████                              {Fore.CYAN}  █")
    print(f"{Fore.CYAN}█  {Fore.RED}     ██ ████  ██      ██                              {Fore.CYAN}  █")
    print(f"{Fore.CYAN}█  {Fore.RED}     ██  ██████       ██                              {Fore.CYAN}  █")
    print(f"{Fore.CYAN}█{' '*58}█")
    print(f"{Fore.CYAN}█  {Fore.MAGENTA}███████ ████████ ██████  ███████  █████  ███    ███     {Fore.CYAN}█")
    print(f"{Fore.CYAN}█  {Fore.MAGENTA}██         ██    ██   ██ ██      ██   ██ ████  ████     {Fore.CYAN}█")
    print(f"{Fore.CYAN}█  {Fore.MAGENTA}███████    ██    ██████  █████   ███████ ██ ████ ██     {Fore.CYAN}█")
    print(f"{Fore.CYAN}█  {Fore.MAGENTA}     ██    ██    ██   ██ ██      ██   ██ ██  ██  ██     {Fore.CYAN}█")
    print(f"{Fore.CYAN}█  {Fore.MAGENTA}███████    ██    ██   ██ ███████ ██   ██ ██      ██     {Fore.CYAN}█")
    print(f"{Fore.CYAN}█{' '*58}█")
    print(f"{Fore.CYAN}{'█'*60}")
    print(f"\n{Fore.GREEN}🚀 {Fore.WHITE}Starting 404Stream Server...")
    print(f"{Fore.YELLOW}⚡ {Fore.WHITE}High-Performance Torrent Streaming Platform")
    print(f"\n{Fore.BLUE}📡 {Fore.WHITE}Server Information:")
    print(f"   {Fore.GREEN}🌐 {Fore.WHITE}Local URL:     {Fore.CYAN}http://127.0.0.1:8000")
    print(f"   {Fore.GREEN}📚 {Fore.WHITE}API Docs:      {Fore.CYAN}http://127.0.0.1:8000/docs")
    print(f"   {Fore.GREEN}📂 {Fore.WHITE}Downloads:     {Fore.CYAN}{Path.home() / '404Stream' / 'downloads'}")
    # print(f"   {Fore.GREEN}🔧 {Fore.WHITE}Health Check:  {Fore.CYAN}http://127.0.0.1:8000/")
    print(f"\n{Fore.MAGENTA}🎯 {Fore.WHITE}Features Available:")
    print(f"   {Fore.GREEN}• {Fore.WHITE}Torrent Search & Streaming")
    # print(f"   {Fore.GREEN}• {Fore.WHITE}IMDB Content Scraping")
    print(f"   {Fore.GREEN}• {Fore.WHITE}VLC Media Player Integration")
    # print(f"   {Fore.GREEN}• {Fore.WHITE}qBittorrent Management")
    print(f"\n{Fore.RED}⏹️  {Fore.WHITE}Press {Fore.YELLOW}Ctrl+C{Fore.WHITE} to stop the server")
    print(f"{Fore.CYAN}{'─'*60}\n")

def install_requirements():
    """Install Python requirements if requirements.txt exists"""
    if os.path.exists(REQUIREMENTS_PATH):
        print("📦 Installing Python requirements...")
        try:
            subprocess.run(
                ["pip", "install", "-r", REQUIREMENTS_PATH],
                check=True
            )
            print("✅ Requirements installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing requirements: {e}")
            print("Continuing anyway...")
    else:
        print("⚠️  No requirements.txt found, skipping installation")

def start_backend():
    show_banner()
    try:
        from backend import main  # make sure backend/__init__.py exists
        uvicorn.run(main.app, host="127.0.0.1", port=8000, log_level="critical")
    except Exception as e:
        print(f"❌ Backend failed to start: {e}")
        sys.exit(1)

def start_backend_thread():
    thread = threading.Thread(target=start_backend, daemon=True)
    thread.start()

def start_qbittorrent():
    subprocess.Popen(
        [QBITTORRENT_PATH, "--no-splash"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def main():
    print("🎉 Starting 404Stream launcher...")

    # Install Python requirements (if not bundled into EXE)
    install_requirements()

    # Start qBittorrent
    start_qbittorrent()
    time.sleep(1)

    # Start backend in background
    start_backend_thread()

    print("✅ 404Stream backend and qBittorrent started!")
    print("🌐 Backend should be available at: http://127.0.0.1:8000")
    print("📖 API docs available at: http://127.0.0.1:8000/docs")
    print("⏹️  Press Ctrl+C to stop all services")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down 404Stream...")
        sys.exit(0)

if __name__ == "__main__":
    main()
