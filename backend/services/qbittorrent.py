import qbittorrentapi, time, os, asyncio
from pathlib import Path

# Define a consistent downloads directory
DOWNLOADS_BASE_DIR = Path.home() / "404Stream" / "downloads"

conn_config = {
    "host": "localhost",
    "port": 8080,
    "username": "admin",
    "password": "adminadmin"
}

client = qbittorrentapi.Client(**conn_config)

try:
    client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(f"Could not connect to qBittorrent: {e}")

if not client.app.preferences.dht:
    client.app.preferences = {"dht": True}

def add_torrent(magnet_link: str, file_idx: int, file_name: str, episode: int, season: int, imdb_id: str, is_movie: bool, info_hash: str):
    try:
        torrents = client.torrents_info(torrent_hashes=info_hash)
        if torrents:
            for torrent in torrents:
                if torrent.name == file_name:
                    files = client.torrents_files(torrent_hash=torrent.hash)
                    for file in files:
                        if file.index == file_idx:
                            return file.name
                else:
                    client.torrents_delete(torrent_hashes=info_hash, delete_files=True)

        # Create downloads directory structure if it doesn't exist
        if is_movie:
            output_path = DOWNLOADS_BASE_DIR / imdb_id
        else:
            output_path = DOWNLOADS_BASE_DIR / imdb_id / str(season) / str(episode)

        # Ensure the directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        client.torrents_add(
            urls=magnet_link,
            save_path=str(output_path),  # Convert Path to string
            category="404stream",
            is_sequential_download=True,
            is_first_last_piece_priority=True,
            rename=file_name,
        )

        time.sleep(1)

        stateEnums = qbittorrentapi.definitions.TorrentStates
        torrent = client.torrents_info(torrent_hashes=info_hash)
        if torrent:
            while torrent[0].state == stateEnums.METADATA_DOWNLOAD:
                torrent = client.torrents_info(torrent_hashes=info_hash)

            client.torrents_pause(torrent_hashes=torrent[0].hash)
            files = client.torrents_files(torrent_hash=torrent[0].hash)
            for file in files:
                priority = 1 if file.index == file_idx else 0
                client.torrents_file_priority(torrent_hash=torrent[0].hash, file_ids=file.id, priority=priority)

        client.torrents_resume(torrent_hashes=torrent[0].hash)

        files = client.torrents_files(torrent_hash=torrent[0].hash)
        for file in files:
            if file.index == file_idx:
                return file.name

    except Exception as e:
        print(f"Error adding torrent: {e}")

# magnet_link = "magnet:?xt=urn:btih:33db66cdfb4ba091cb47621f000ddc0946e82eb6&dn=[Anime Land] Tenki no Ko (BDRip 1080p HEVC HDR10 QAAC) [88E43D38].mkv&tr=tracker:udp://tracker.opentrackr.org:1337/announce&tr=tracker:udp://open.demonii.com:1337/announce&tr=tracker:udp://open.stealth.si:80/announce&tr=tracker:udp://tracker.torrent.eu.org:451/announce&tr=tracker:udp://exodus.desync.com:6969/announce&tr=tracker:udp://tracker-udp.gbitt.info:80/announce&tr=tracker:udp://explodie.org:6969/announce&tr=tracker:udp://wepzone.net:6969/announce&tr=tracker:udp://ttk2.nbaonlineservice.com:6969/announce&tr=tracker:udp://tracker1.bt.moack.co.kr:80/announce&tr=tracker:udp://tracker.tryhackx.org:6969/announce&tr=tracker:udp://tracker.srv00.com:6969/announce&tr=tracker:udp://tracker.qu.ax:6969/announce&tr=tracker:udp://tracker.ololosh.space:6969/announce&tr=tracker:udp://tracker.gmi.gd:6969/announce&tr=tracker:udp://tracker.gigantino.net:6969/announce&tr=tracker:udp://tracker.filemail.com:6969/announce&tr=tracker:udp://tracker.dump.cl:6969/announce&tr=tracker:udp://tracker.dler.org:6969/announce&tr=tracker:udp://tracker.darkness.services:6969/announce&tr=tracker:http://nyaa.tracker.wf:7777/announce&tr=tracker:http://anidex.moe:6969/announce&tr=tracker:http://tracker.anirena.com:80/announce&tr=tracker:udp://tracker.uw0.xyz:6969/announce&tr=tracker:http://share.camoe.cn:8080/announce&tr=tracker:http://t.nyaatracker.com:80/announce&tr=dht:33db66cdfb4ba091cb47621f000ddc0946e82eb6&tr=udp://tracker.opentrackr.org:1337/announce&tr=http://tracker.opentrackr.org:1337/announce&tr=udp://open.demonii.com:1337/announce&tr=udp://open.stealth.si:80/announce&tr=udp://tracker.torrent.eu.org:451/announce&tr=udp://exodus.desync.com:6969/announce&tr=udp://tracker-udp.gbitt.info:80/announce&tr=udp://explodie.org:6969/announce&tr=udp://wepzone.net:6969/announce&tr=udp://ttk2.nbaonlineservice.com:6969/announce&tr=udp://tracker1.bt.moack.co.kr:80/announce&tr=udp://tracker.tryhackx.org:6969/announce&tr=udp://tracker.srv00.com:6969/announce&tr=udp://tracker.qu.ax:6969/announce&tr=udp://tracker.ololosh.space:6969/announce&tr=udp://tracker.gmi.gd:6969/announce&tr=udp://tracker.gigantino.net:6969/announce&tr=udp://tracker.filemail.com:6969/announce&tr=udp://tracker.dump.cl:6969/announce&tr=udp://tracker.dler.org:6969/announce&tr=udp://tracker.darkness.services:6969/announce&tr=udp://tracker.bittor.pw:1337/announce&tr=udp://tr4ck3r.duckdns.org:6969/announce&tr=udp://t.overflow.biz:6969/announce&tr=udp://retracker01-msk-virt.corbina.net:80/announce&tr=udp://retracker.lanta.me:2710/announce&tr=udp://public.tracker.vraphim.com:6969/announce&tr=udp://p4p.arenabg.com:1337/announce&tr=udp://p2p.publictracker.xyz:6969/announce&tr=udp://opentracker.io:6969/announce&tr=udp://open.free-tracker.ga:6969/announce&tr=udp://open.dstud.io:6969/announce&tr=udp://ns-1.x-fins.com:6969/announce&tr=udp://martin-gebhardt.eu:25/announce&tr=udp://leet-tracker.moe:1337/announce&tr=udp://isk.richardsw.club:6969/announce&tr=udp://ipv4announce.sktorrent.eu:6969/announce&tr=udp://evan.im:6969/announce&tr=udp://discord.heihachi.pw:6969/announce&tr=udp://d40969.acod.regrucolo.ru:6969/announce&tr=udp://bt.ktrackers.com:6666/announce&tr=udp://bittorrent-tracker.e-n-c-r-y-p-t.net:1337/announce&tr=udp://bandito.byterunner.io:6969/announce&tr=udp://1c.premierzal.ru:6969/announce&tr=https://tracker.yemekyedim.com:443/announce&tr=https://tracker.pmman.tech:443/announce&tr=https://tracker.moeblog.cn:443/announce&tr=https://tracker.gcrenwp.top:443/announce&tr=https://tracker.bt4g.com:443/announce&tr=http://www.torrentsnipe.info:2701/announce&tr=http://www.genesis-sp.org:2710/announce&tr=http://wepzone.net:6969/announce&tr=http://tracker810.xyz:11450/announce&tr=http://tracker2.dler.org:80/announce&tr=http://tracker1.bt.moack.co.kr:80/announce&tr=http://tracker.xiaoduola.xyz:6969/announce&tr=http://tracker.waaa.moe:6969/announce&tr=http://tracker.vanitycore.co:6969/announce&tr=http://tracker.sbsub.com:2710/announce&tr=http://tracker.renfei.net:8080/announce&tr=http://tracker.qu.ax:6969/announce&tr=http://tracker.mywaifu.best:6969/announce&tr=http://tracker.moxing.party:6969/announce&tr=http://tracker.lintk.me:2710/announce&tr=http://tracker.ipv6tracker.org:80/announce&tr=http://tracker.dmcomic.org:2710/announce&tr=http://tracker.dler.com:6969/announce&tr=http://tracker.darkness.services:6969/announce&tr=http://tracker.corpscorp.online:80/announce&tr=http://tracker.bz:80/announce&tr=http://tracker.bt4g.com:2095/announce&tr=http://tracker.bt-hash.com:80/announce&tr=http://tracker.bittor.pw:1337/announce&tr=http://tr.kxmp.cf:80/announce&tr=http://taciturn-shadow.spb.ru:6969/announce&tr=http://t.overflow.biz:6969/announce&tr=http://t.jaekr.sh:6969/announce&tr=http://shubt.net:2710/announce&tr=http://share.hkg-fansub.info:80/announce.php&tr=http://servandroidkino.ru:80/announce&tr=http://seeders-paradise.org:80/announce&tr=http://retracker.spark-rostov.ru:80/announce&tr=http://public.tracker.vraphim.com:6969/announce&tr=http://p4p.arenabg.com:1337/announce&tr=http://open.trackerlist.xyz:80/announce&tr=http://home.yxgz.club:6969/announce&tr=http://highteahop.top:6960/announce&tr=http://finbytes.org:80/announce.php&tr=http://buny.uk:6969/announce&tr=http://bt1.xxxxbt.cc:6969/announce&tr=http://bt.poletracker.org:2710/announce&tr=http://bittorrent-tracker.e-n-c-r-y-p-t.net:1337/announce&tr=http://0d.kebhana.mx:443/announce&tr=http://0123456789nonexistent.com:80/announce&tr=udp://tracker2.dler.org:80/announce&tr=udp://tracker.torrust-demo.com:6969/announce&tr=udp://tracker.therarbg.to:6969/announce&tr=udp://tracker.fnix.net:6969/announce&tr=udp://tracker.ddunlimited.net:6969/announce&tr=udp://ipv4.rer.lol:2710/announce&tr=udp://concen.org:6969/announce&tr=udp://bt.rer.lol:6969/announce&tr=udp://bt.rer.lol:2710/announce&tr=https://tracker.zhuqiy.top:443/announce&tr=https://tracker.linvk.com:443/announce&tr=https://tracker.leechshield.link:443/announce&tr=https://tracker.ghostchu-services.top:443/announce&tr=https://tracker.expli.top:443/announce&tr=https://sparkle.ghostchu-services.top:443/announce&tr=http://tracker1.itzmx.com:8080/announce&tr=http://tracker.zhuqiy.top:80/announce&tr=http://tracker.ghostchu-services.top:80/announce&tr=http://tracker.dler.org:6969/announce&tr=http://tracker.23794.top:6969/announce&so=0"
# file_name = "[Anime Land] Tenki no Ko (BDRip 1080p HEVC HDR10 QAAC) [88E43D38].mkv"
# episode = 1
# season = 1
# imdb_id = "tt9426210"
# file_idx = 0
# is_movie = True
# info_hash = "33db66cdfb4ba091cb47621f000ddc0946e82eb6"

# add_torrent(magnet_link, file_idx, file_name, episode, season, imdb_id, is_movie, info_hash)
