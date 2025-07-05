import httpx


TORRENTIO_BASE_URL = "https://torrentio.strem.fun/stream"
PUBLIC_TRACKERS = ['udp://tracker.opentrackr.org:1337/announce', 'http://tracker.opentrackr.org:1337/announce', 'udp://open.demonii.com:1337/announce', 'udp://open.stealth.si:80/announce', 'udp://tracker.torrent.eu.org:451/announce', 'udp://exodus.desync.com:6969/announce', 'udp://tracker-udp.gbitt.info:80/announce', 'udp://explodie.org:6969/announce', 'udp://wepzone.net:6969/announce', 'udp://ttk2.nbaonlineservice.com:6969/announce', 'udp://tracker1.bt.moack.co.kr:80/announce', 'udp://tracker.tryhackx.org:6969/announce', 'udp://tracker.srv00.com:6969/announce', 'udp://tracker.qu.ax:6969/announce', 'udp://tracker.ololosh.space:6969/announce', 'udp://tracker.gmi.gd:6969/announce', 'udp://tracker.gigantino.net:6969/announce', 'udp://tracker.filemail.com:6969/announce', 'udp://tracker.dump.cl:6969/announce', 'udp://tracker.dler.org:6969/announce', 'udp://tracker.darkness.services:6969/announce', 'udp://tracker.bittor.pw:1337/announce', 'udp://tr4ck3r.duckdns.org:6969/announce', 'udp://t.overflow.biz:6969/announce', 'udp://retracker01-msk-virt.corbina.net:80/announce', 'udp://retracker.lanta.me:2710/announce', 'udp://public.tracker.vraphim.com:6969/announce', 'udp://p4p.arenabg.com:1337/announce', 'udp://p2p.publictracker.xyz:6969/announce', 'udp://opentracker.io:6969/announce', 'udp://open.free-tracker.ga:6969/announce', 'udp://open.dstud.io:6969/announce', 'udp://ns-1.x-fins.com:6969/announce', 'udp://martin-gebhardt.eu:25/announce', 'udp://leet-tracker.moe:1337/announce', 'udp://isk.richardsw.club:6969/announce', 'udp://ipv4announce.sktorrent.eu:6969/announce', 'udp://evan.im:6969/announce', 'udp://discord.heihachi.pw:6969/announce', 'udp://d40969.acod.regrucolo.ru:6969/announce', 'udp://bt.ktrackers.com:6666/announce', 'udp://bittorrent-tracker.e-n-c-r-y-p-t.net:1337/announce', 'udp://bandito.byterunner.io:6969/announce', 'udp://1c.premierzal.ru:6969/announce', 'https://tracker.yemekyedim.com:443/announce', 'https://tracker.pmman.tech:443/announce', 'https://tracker.moeblog.cn:443/announce', 'https://tracker.gcrenwp.top:443/announce', 'https://tracker.bt4g.com:443/announce', 'http://www.torrentsnipe.info:2701/announce', 'http://www.genesis-sp.org:2710/announce', 'http://wepzone.net:6969/announce', 'http://tracker810.xyz:11450/announce', 'http://tracker2.dler.org:80/announce', 'http://tracker1.bt.moack.co.kr:80/announce', 'http://tracker.xiaoduola.xyz:6969/announce', 'http://tracker.waaa.moe:6969/announce', 'http://tracker.vanitycore.co:6969/announce', 'http://tracker.sbsub.com:2710/announce', 'http://tracker.renfei.net:8080/announce', 'http://tracker.qu.ax:6969/announce', 'http://tracker.mywaifu.best:6969/announce', 'http://tracker.moxing.party:6969/announce', 'http://tracker.lintk.me:2710/announce', 'http://tracker.ipv6tracker.org:80/announce', 'http://tracker.dmcomic.org:2710/announce', 'http://tracker.dler.com:6969/announce', 'http://tracker.darkness.services:6969/announce', 'http://tracker.corpscorp.online:80/announce', 'http://tracker.bz:80/announce', 'http://tracker.bt4g.com:2095/announce', 'http://tracker.bt-hash.com:80/announce', 'http://tracker.bittor.pw:1337/announce', 'http://tr.kxmp.cf:80/announce', 'http://taciturn-shadow.spb.ru:6969/announce', 'http://t.overflow.biz:6969/announce', 'http://t.jaekr.sh:6969/announce', 'http://shubt.net:2710/announce', 'http://share.hkg-fansub.info:80/announce.php', 'http://servandroidkino.ru:80/announce', 'http://seeders-paradise.org:80/announce', 'http://retracker.spark-rostov.ru:80/announce', 'http://public.tracker.vraphim.com:6969/announce', 'http://p4p.arenabg.com:1337/announce', 'http://open.trackerlist.xyz:80/announce', 'http://home.yxgz.club:6969/announce', 'http://highteahop.top:6960/announce', 'http://finbytes.org:80/announce.php', 'http://buny.uk:6969/announce', 'http://bt1.xxxxbt.cc:6969/announce', 'http://bt.poletracker.org:2710/announce', 'http://bittorrent-tracker.e-n-c-r-y-p-t.net:1337/announce', 'http://0d.kebhana.mx:443/announce', 'http://0123456789nonexistent.com:80/announce', 'udp://tracker2.dler.org:80/announce', 'udp://tracker.torrust-demo.com:6969/announce', 'udp://tracker.therarbg.to:6969/announce', 'udp://tracker.fnix.net:6969/announce', 'udp://tracker.ddunlimited.net:6969/announce', 'udp://ipv4.rer.lol:2710/announce', 'udp://concen.org:6969/announce', 'udp://bt.rer.lol:6969/announce', 'udp://bt.rer.lol:2710/announce', 'https://tracker.zhuqiy.top:443/announce', 'https://tracker.linvk.com:443/announce', 'https://tracker.leechshield.link:443/announce', 'https://tracker.ghostchu-services.top:443/announce', 'https://tracker.expli.top:443/announce', 'https://sparkle.ghostchu-services.top:443/announce', 'http://tracker1.itzmx.com:8080/announce', 'http://tracker.zhuqiy.top:80/announce', 'http://tracker.ghostchu-services.top:80/announce', 'http://tracker.dler.org:6969/announce', 'http://tracker.23794.top:6969/announce']


async def get_torrents_for_movies(imdb_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TORRENTIO_BASE_URL}/movie/{imdb_id}.json")
        if response.status_code == 200:
            data = response.json().get("streams", [])
            result = get_torrents(data)
            return result
        else:
            return {"torrents": []}

async def get_torrents_for_shows(imdb_id: str, season: int, episode: int):
    if imdb_id == "tt9335498":
        if season > 1:
            season += 1
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TORRENTIO_BASE_URL}/series/{imdb_id}:{season}:{episode}.json")
        if response.status_code == 200:
            data = response.json().get("streams", [])
            result = get_torrents(data)
            return result
        else:
            return {"torrents": []}

def get_torrents(data):
    torrents_array = []
    qualityOptions = ["1080p", "4k", "720p", "480p", "DVDRip", "BDRip", "WEBRip", "WEB-DL", "HDRip", "HDTV", "BluRay"]

    for item in data:
        title = item.get("title")

        seeders = int(title.split("👤")[-1].split("💾")[0].strip())
        size = title.split("💾")[-1].split("⚙️")[0].strip()

        tags = item.get("behaviorHints", {}).get("bingeGroup", "")
        quality = item.get("name").split("\n")[-1].replace("HDR", "").strip()

        if quality not in qualityOptions:
            for option in qualityOptions:
                if option in tags.lower():
                    quality = option
                    break
            else:
                quality = "Unknown"

        trackers = item.get("sources", []) + PUBLIC_TRACKERS
        trackers = "&tr=".join(trackers)
        magnet = f"magnet:?xt=urn:btih:{item.get('infoHash')}&dn={item.get('behaviorHints', {}).get('filename', '')}&tr={trackers}&so={item.get('fileIdx', '0')}"


        torrents_array.append({
            "name": item.get("behaviorHints", {}).get("filename", ""),
            "quality": quality,
            "info_hash": item.get("infoHash"),
            "file_idx": item.get("fileIdx"),
            "magnet": magnet,
            "seeders": seeders,
            "size": size,
        })



    sorted_torrents = sorted(torrents_array, key=lambda x: x["seeders"], reverse=True)

    torrents = {}
    for torrent in sorted_torrents:
        if torrent["quality"] in torrents:
            torrents[torrent["quality"]].append(torrent)
        else:
            torrents[torrent["quality"]] = [torrent]

    sorted_torrents = []

    for quality in qualityOptions:
        if quality not in torrents:
            torrents[quality] = []
        sorted_torrents += torrents[quality]

    return {"torrents": sorted_torrents}
