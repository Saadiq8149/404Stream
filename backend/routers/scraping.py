from fastapi import APIRouter

router = APIRouter(prefix="/scrape", tags=["Scraping"])

import requests
from bs4 import BeautifulSoup

@router.get("/{imdb_id}")
def scrape_imdb(imdb_id: str):
    print(f"🔍 Scraping IMDB: {imdb_id}")

    URL = f"https://www.imdb.com/title/{imdb_id}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.find("title").text.strip()

    is_movie = soup.find("meta", {"property": "og:type"})
    is_movie = True if is_movie["content"] == "video.movie" else False

    poster = soup.find("meta", {"property": "og:image"})
    poster = poster["content"] if poster else ""

    if is_movie:
        seasons = []
        episodes_array = []
    else:
        URL = f"https://www.imdb.com/title/{imdb_id}/episodes"
        res = requests.get(URL, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        seasons = len(list(soup.find("ul", { "class": "ipc-tabs ipc-tabs--base ipc-tabs--align-left", "role": "tablist"}).children)) - 1

        episodes_array = []

        for season in range(seasons):
            URL = f"https://www.imdb.com/title/{imdb_id}/episodes?season={season + 1}"
            res = requests.get(URL, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")

            texts = soup.find_all("div", {"class": "ipc-title__text ipc-title__text--reduced"})

            episodes = {"season": season + 1, "episodes": []}

            for text in texts:
                if "E" in text.text and "S" in text.text:
                    episode_season = text.text.split("∙")[0].strip()
                    episode = int(episode_season.split(".")[1].replace("E", "").strip())
                    episode_title = text.text.split("∙")[-1].strip()
                    episodes["episodes"].append({"episode": int(episode), "title": episode_title})

            if episodes:
                episodes_array.append(episodes)


    data = {"title": title, "is_movie": is_movie, "poster": poster, "seasons": seasons, "episodes": episodes_array}

    return data
# scrape_imdb("tt9335498")
