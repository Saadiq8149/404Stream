from fastapi import APIRouter
from backend.services.torrentio import get_torrents_for_movies, get_torrents_for_shows

router = APIRouter(prefix="/torrents", tags=["Torrents"])

@router.get("/movie", summary="Get torrents for a movie by IMDb ID")
async def get_torrent(imdb_id: str):
    print(f"🎬 Movie torrent request: {imdb_id}")
    return await get_torrents_for_movies(imdb_id)

@router.get("/show", summary="Get torrents for a show by IMDb ID, season, and episode")
async def get_show_torrent(imdb_id: str, season: int, episode: int):
    print(f"📺 Show torrent request: {imdb_id} S{season}E{episode}")
    return await get_torrents_for_shows(imdb_id, season, episode)
