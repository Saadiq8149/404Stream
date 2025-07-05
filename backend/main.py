from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import torrents, stream, scraping
import colorama
from colorama import Fore
from pathlib import Path

app = FastAPI()

app.include_router(torrents.router)
app.include_router(stream.router)
app.include_router(scraping.router)


# Only for development purposes, to allow CORS from any origin.
# In production, you should specify allowed origins to prevent CORS issues.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
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


@app.get("/")
async def root():
    return {"message": "Welcome to the 404stream API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")
