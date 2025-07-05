from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from fastapi.responses import StreamingResponse
from backend.services.qbittorrent import add_torrent
from backend.services.opensubs import get_subtitles
from pathlib import Path
import os, time, mimetypes, subprocess, ctypes, threading, asyncio

# Use the same downloads directory as qbittorrent service
DOWNLOADS_BASE_DIR = Path.home() / "404Stream" / "downloads"

CONTENT_CHUNK_SIZE=100*1024

router = APIRouter(prefix="/stream", tags=["Stream"])

# WILL FINISH THIS PATH LATER
@router.get("/", summary="Stream a video by its IMDb ID")
async def stream_video(magnet_link: str, file_idx: int, file_name: str, imdb_id: str, is_movie: bool, info_hash: str, episode: int = 1, season: int = 1, range_header: Optional[str] = Header(None)):
    content_type = "Movie" if is_movie else f"S{season}E{episode}"
    print(f"▶️  Stream request: {imdb_id} ({content_type})")

    add_torrent(magnet_link, file_idx, file_name, episode, season, imdb_id, is_movie, info_hash)

    video_path = get_video_path(imdb_id, is_movie, episode, season, file_name)

    if video_path == "":
        for _ in range(30): # Wait for the file to appear, with a timeout of 30 seconds
            time.sleep(1)
            video_path = get_video_path(imdb_id, is_movie, episode, season, file_name)
            if video_path:
                break
        else:
            return {"error": "File not found"}

    mime_type, _ = mimetypes.guess_type(video_path)
    stream, total_size = get_file(video_path)

    range_header = range_header or "bytes=0-"
    range_match = range_header.replace("bytes=", "").split("-")
    start_byte = int(range_match[0])
    end_byte = min(start_byte + CONTENT_CHUNK_SIZE - 1, total_size - 1)


    return StreamingResponse(
        chunk_generator_from_stream(
            stream,
            start=start_byte,
            chunk_size=CONTENT_CHUNK_SIZE,
        )
        ,headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte}-{end_byte}/{total_size}",
            "Content-Type": mime_type or "application/octet-stream",
        },
        status_code=206)

# FOCUSING ON VLC STREAMING
@router.get("/vlc", summary="Opens the stream in VLC")
async def stream_in_vlc(magnet_link: str, file_idx: int, file_name: str, imdb_id: str, is_movie: bool, info_hash: str, episode: int = 1, season: int = 1):
    content_type = "Movie" if is_movie else f"S{season}E{episode}"
    print(f"🎯 VLC Stream: {imdb_id} ({content_type})")

    add_torrent(magnet_link, file_idx, file_name, episode, season, imdb_id, is_movie, info_hash)

    video_path = get_video_path(imdb_id, is_movie, episode, season, file_name)

    # get_subtitles(imdb_id, season, episode, is_movie)
    # subtitle_path = ""
    # if is_movie:
    #     subtitle_path = str(DOWNLOADS_BASE_DIR / imdb_id / "subtitles.srt")
    # else:
    #     subtitle_path = str(DOWNLOADS_BASE_DIR / imdb_id / str(season) / str(episode) / "subtitles.srt")
    # for _ in range(30):
    #     time.sleep(1)
    #     if os.path.exists(subtitle_path):
    #         break

    if video_path == "":
        for i in range(30):
            time.sleep(1)
            video_path = get_video_path(imdb_id, is_movie, episode, season, file_name)
            if video_path:
                break
        else:
            return {"error": "File not found"}

    for i in range(30):
        time.sleep(1)
        buffer_size = 200 if is_movie else 50 # MB
        if is_buffer_ready(video_path, buffer_size):
            break

    video_path = get_short_path_name(video_path)
    video_file = Path(video_path)
    video_dir = str(video_file.parent)

    # Get short name version of filename
    short_video = get_short_path_name(str(video_file))
    short_video = short_video.split("\\")[-1]  # Get the last part of the path

    def launch_vlc(video_dir, short_video):
        subprocess.Popen([
            "vlc", short_video, "--start-time=0", "--repeat"
        ], cwd=video_dir)

    threading.Thread(target=launch_vlc, args=(video_dir, short_video)).start()

    return {"status": "VLC launched"}


def get_short_path_name(long_path: str) -> str:
    """Convert long Windows path to short (8.3) path to avoid special character issues."""
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.kernel32.GetShortPathNameW(long_path, buf, 260)
    return buf.value

def is_buffer_ready(path: str, min_mb: int = 50) -> bool:
    try:
        return os.path.getsize(path) > min_mb * 1024 * 1024
    except FileNotFoundError:
        return False

def get_video_path(imdb_id: str, is_movie: bool, episode: int, season: int, file_name: str) -> str:
    base_path = DOWNLOADS_BASE_DIR / imdb_id if is_movie else DOWNLOADS_BASE_DIR / imdb_id / str(season) / str(episode)
    if not base_path.exists():
        return ""

    for root, _, files in os.walk(str(base_path)):
        if file_name in files:
            return os.path.join(root, file_name)
    return ""


def get_file(path: str):
    f = open(path,'rb')
    return f, os.path.getsize(path)

def chunk_generator_from_stream(stream, chunk_size, start):
    stream.seek(start)
    while True:
        data = stream.read(chunk_size)
        if not data:
            break
        yield data
    stream.close()


# magnet_link = "magnet:?xt=urn:btih:aa1cf914b2d134990833e744e278c7d1bba54cc2&dn=S01E01-I Want to Make You Invite Me to a Movie, Kaguya Wants You to Stop Her [DF2AEB1B].mkv&tr=tracker:udp://tracker.opentrackr.org:1337/announce&tr=tracker:udp://open.demonii.com:1337/announce&tr=tracker:udp://open.stealth.si:80/announce&tr=tracker:udp://exodus.desync.com:6969/announce&tr=tracker:udp://tracker.torrent.eu.org:451/announce&tr=tracker:udp://wepzone.net:6969/announce&tr=tracker:udp://ttk2.nbaonlineservice.com:6969/announce&tr=tracker:udp://tracker1.bt.moack.co.kr:80/announce&tr=tracker:udp://tracker.tryhackx.org:6969/announce&tr=tracker:udp://tracker.therarbg.to:6969/announce&tr=tracker:udp://tracker.theoks.net:6969/announce&tr=tracker:udp://tracker.srv00.com:6969/announce&tr=tracker:udp://tracker.qu.ax:6969/announce&tr=tracker:udp://tracker.ololosh.space:6969/announce&tr=tracker:udp://tracker.dump.cl:6969/announce&tr=tracker:udp://tracker.dler.org:6969/announce&tr=tracker:udp://tracker.darkness.services:6969/announce&tr=tracker:udp://tracker.bittor.pw:1337/announce&tr=tracker:udp://tracker-udp.gbitt.info:80/announce&tr=tracker:udp://tr4ck3r.duckdns.org:6969/announce&tr=tracker:http://nyaa.tracker.wf:7777/announce&tr=tracker:http://anidex.moe:6969/announce&tr=tracker:http://tracker.anirena.com:80/announce&tr=tracker:udp://tracker.uw0.xyz:6969/announce&tr=tracker:http://share.camoe.cn:8080/announce&tr=tracker:http://t.nyaatracker.com:80/announce&tr=dht:aa1cf914b2d134990833e744e278c7d1bba54cc2&tr=udp://tracker.opentrackr.org:1337/announce&tr=http://tracker.opentrackr.org:1337/announce&tr=udp://open.demonii.com:1337/announce&tr=udp://open.stealth.si:80/announce&tr=udp://tracker.torrent.eu.org:451/announce&tr=udp://exodus.desync.com:6969/announce&tr=udp://tracker-udp.gbitt.info:80/announce&tr=udp://explodie.org:6969/announce&tr=udp://wepzone.net:6969/announce&tr=udp://ttk2.nbaonlineservice.com:6969/announce&tr=udp://tracker1.bt.moack.co.kr:80/announce&tr=udp://tracker.tryhackx.org:6969/announce&tr=udp://tracker.srv00.com:6969/announce&tr=udp://tracker.qu.ax:6969/announce&tr=udp://tracker.ololosh.space:6969/announce&tr=udp://tracker.gmi.gd:6969/announce&tr=udp://tracker.gigantino.net:6969/announce&tr=udp://tracker.filemail.com:6969/announce&tr=udp://tracker.dump.cl:6969/announce&tr=udp://tracker.dler.org:6969/announce&tr=udp://tracker.darkness.services:6969/announce&tr=udp://tracker.bittor.pw:1337/announce&tr=udp://tr4ck3r.duckdns.org:6969/announce&tr=udp://t.overflow.biz:6969/announce&tr=udp://retracker01-msk-virt.corbina.net:80/announce&tr=udp://retracker.lanta.me:2710/announce&tr=udp://public.tracker.vraphim.com:6969/announce&tr=udp://p4p.arenabg.com:1337/announce&tr=udp://p2p.publictracker.xyz:6969/announce&tr=udp://opentracker.io:6969/announce&tr=udp://open.free-tracker.ga:6969/announce&tr=udp://open.dstud.io:6969/announce&tr=udp://ns-1.x-fins.com:6969/announce&tr=udp://martin-gebhardt.eu:25/announce&tr=udp://leet-tracker.moe:1337/announce&tr=udp://isk.richardsw.club:6969/announce&tr=udp://ipv4announce.sktorrent.eu:6969/announce&tr=udp://evan.im:6969/announce&tr=udp://discord.heihachi.pw:6969/announce&tr=udp://d40969.acod.regrucolo.ru:6969/announce&tr=udp://bt.ktrackers.com:6666/announce&tr=udp://bittorrent-tracker.e-n-c-r-y-p-t.net:1337/announce&tr=udp://bandito.byterunner.io:6969/announce&tr=udp://1c.premierzal.ru:6969/announce&tr=https://tracker.yemekyedim.com:443/announce&tr=https://tracker.pmman.tech:443/announce&tr=https://tracker.moeblog.cn:443/announce&tr=https://tracker.gcrenwp.top:443/announce&tr=https://tracker.bt4g.com:443/announce&tr=http://www.torrentsnipe.info:2701/announce&tr=http://www.genesis-sp.org:2710/announce&tr=http://wepzone.net:6969/announce&tr=http://tracker810.xyz:11450/announce&tr=http://tracker2.dler.org:80/announce&tr=http://tracker1.bt.moack.co.kr:80/announce&tr=http://tracker.xiaoduola.xyz:6969/announce&tr=http://tracker.waaa.moe:6969/announce&tr=http://tracker.vanitycore.co:6969/announce&tr=http://tracker.sbsub.com:2710/announce&tr=http://tracker.renfei.net:8080/announce&tr=http://tracker.qu.ax:6969/announce&tr=http://tracker.mywaifu.best:6969/announce&tr=http://tracker.moxing.party:6969/announce&tr=http://tracker.lintk.me:2710/announce&tr=http://tracker.ipv6tracker.org:80/announce&tr=http://tracker.dmcomic.org:2710/announce&tr=http://tracker.dler.com:6969/announce&tr=http://tracker.darkness.services:6969/announce&tr=http://tracker.corpscorp.online:80/announce&tr=http://tracker.bz:80/announce&tr=http://tracker.bt4g.com:2095/announce&tr=http://tracker.bt-hash.com:80/announce&tr=http://tracker.bittor.pw:1337/announce&tr=http://tr.kxmp.cf:80/announce&tr=http://taciturn-shadow.spb.ru:6969/announce&tr=http://t.overflow.biz:6969/announce&tr=http://t.jaekr.sh:6969/announce&tr=http://shubt.net:2710/announce&tr=http://share.hkg-fansub.info:80/announce.php&tr=http://servandroidkino.ru:80/announce&tr=http://seeders-paradise.org:80/announce&tr=http://retracker.spark-rostov.ru:80/announce&tr=http://public.tracker.vraphim.com:6969/announce&tr=http://p4p.arenabg.com:1337/announce&tr=http://open.trackerlist.xyz:80/announce&tr=http://home.yxgz.club:6969/announce&tr=http://highteahop.top:6960/announce&tr=http://finbytes.org:80/announce.php&tr=http://buny.uk:6969/announce&tr=http://bt1.xxxxbt.cc:6969/announce&tr=http://bt.poletracker.org:2710/announce&tr=http://bittorrent-tracker.e-n-c-r-y-p-t.net:1337/announce&tr=http://0d.kebhana.mx:443/announce&tr=http://0123456789nonexistent.com:80/announce&tr=udp://tracker2.dler.org:80/announce&tr=udp://tracker.torrust-demo.com:6969/announce&tr=udp://tracker.therarbg.to:6969/announce&tr=udp://tracker.fnix.net:6969/announce&tr=udp://tracker.ddunlimited.net:6969/announce&tr=udp://ipv4.rer.lol:2710/announce&tr=udp://concen.org:6969/announce&tr=udp://bt.rer.lol:6969/announce&tr=udp://bt.rer.lol:2710/announce&tr=https://tracker.zhuqiy.top:443/announce&tr=https://tracker.linvk.com:443/announce&tr=https://tracker.leechshield.link:443/announce&tr=https://tracker.ghostchu-services.top:443/announce&tr=https://tracker.expli.top:443/announce&tr=https://sparkle.ghostchu-services.top:443/announce&tr=http://tracker1.itzmx.com:8080/announce&tr=http://tracker.zhuqiy.top:80/announce&tr=http://tracker.ghostchu-services.top:80/announce&tr=http://tracker.dler.org:6969/announce&tr=http://tracker.23794.top:6969/announce&so=12"
# file_idx = 12
# file_name = "S01E01-I Want to Make You Invite Me to a Movie, Kaguya Wants You to Stop Her [DF2AEB1B].mkv"
# episode = 1
# season = 1
# imdb_id = "tt9522300"
# is_movie = False
# info_hash = "aa1cf914b2d134990833e744e278c7d1bba54cc2"

# stream_video(magnet_link, file_idx, file_name, imdb_id, is_movie, info_hash, episode, season)
