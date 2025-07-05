import requests, os, json, time
from datetime import datetime, timedelta

API_KEY = "your_api_key_here"  # Replace with your actual OpenSubtitles API key
USERNAME = "username"
PASSWORD = "password"

def get_auth_token():
    token_file = os.path.join(os.path.dirname(__file__), "opensubs_token.json")

    if os.path.exists(token_file):
        try:
            with open(token_file, "r") as f:
                token_data = json.load(f)

            if datetime.fromisoformat(token_data["expiry"]) > datetime.now():
                return token_data["token"]
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    response = requests.post(
        "https://api.opensubtitles.com/api/v1/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        },
        headers={
            "Content-Type": "application/json",
            "Api-Key": API_KEY,
            "User-Agent": "404Stream v1.0.0"
        }
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("token")

        with open(token_file, "w") as f:
            json.dump({
                "token": token,
                "expiry": (datetime.now() + timedelta(hours=23)).isoformat()
            }, f)

        return token
    else:
        raise Exception(f"Failed to get auth token: {response.status_code} - {response.text}")



def get_subtitles(imdb_id: str, season: int = None, episode: int = None, is_movie: bool = True):
    token = get_auth_token()

    params = {"imdb_id": imdb_id, "languages": "en"}
    if not is_movie:
        params["season_number"] = season
        params["episode_number"] = episode

    response = requests.get(
        "https://api.opensubtitles.com/api/v1/subtitles",
        params=params,
        headers={
            "Content-Type": "application/json",
            "Api-Key": API_KEY,
            "Authorization": f"Bearer {token}",
            "User-Agent": "404Stream v1.0.0"
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to fetch subtitles: {response.status_code} - {response.text}")

    time.sleep(5)  # To avoid hitting rate limits

    file_id = response.json()["data"][0]["attributes"]["files"][0]["file_id"]

    response = requests.post(
        f"https://api.opensubtitles.com/api/v1/download",
        headers={
            "Content-Type": "application/json",
            "Api-Key": API_KEY,
            "Authorization": f"Bearer {token}",
            "User-Agent": "404Stream v1.0.0"
        },
        json={
            "file_id": file_id,
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to download subtitles: {response.status_code} - {response.text}")

    time.sleep(5)  # To avoid hitting rate limits

    try:
        download_srt_file(response.json()["link"], imdb_id, season, episode, is_movie)
    except Exception as e:
        print(f"Error downloading SRT file: {e}")
        return None

def download_srt_file(url: str, imdb_id: str, season: int = None, episode: int = None, is_movie: bool = True):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.opensubtitles.com/"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Ensure directories exist
        if not is_movie:
            os.makedirs(f"../downloads/{imdb_id}/{season}/{episode}", exist_ok=True)
            filename = f"../downloads/{imdb_id}/{season}/{episode}/subtitles.srt"
        else:
            os.makedirs(f"../downloads", exist_ok=True)
            filename = f"../downloads/{imdb_id}.srt"

        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        raise Exception(f"Failed to download subtitle file: {response.status_code} - {response.text}")

# url = "https://www.opensubtitles.com/download/0272A183BB3C57D600E9D04303A57A03978F4E973E7D6D56E75E92ADC0F51F0424F7CE3E939DEA7D98AA31A60A9C1F5A0307DD0AE69893509B335BFD6A0F69703B3B7FE0042C4E49F203E07A46FCCB78E718ACF43447BE0B4CBBA95C34A900322FB54C1363EF9E6807550722FA1C68C39A57BA3F8381516EB528E79BB6F5CF340AD0E86B95BFE02D20747EF796A92008406B227D75AB4F5A54A9923098C1ECD51B8E98748911E53A8534465968A01313E418F4BBC4AFF33A2AF79469FE804B114C220F07F588D4795E54B102F6318B097DB6A9A3B7600D7764B3EF96B96E59E68322D2D7924FB68CFA32FE98EF870B352F99BACC01DAFE88A31BB61E2796697EA8ABB21E66206696AF8E37EE070074BA0FB59FAC8C9DF37B94C05AB7103E4EA97A27F604D88E3C5A55BD20F610CCFFE2B4A85B1BB5578BFF7F50B2166C590987/subfile/Kaguya-Sama.Love.Is.War.S01E01.JAPANESE.WEBRip.NF.en.srt"
# download_srt_file(url, "tt9522300", 1, 1, False)
