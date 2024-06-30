import io
import os

import whisper
import sys
import json
import requests
from collections import namedtuple
import datetime
from dotenv import load_dotenv
from whisper.utils import get_writer

TADDY_API = 'https://api.taddy.org/'
Episode = namedtuple("Episode", "name url description download_datetime")


def taddy_query(episode):
    """
    Returns a GraphQL query that searches for the episode number.
    See: https://api.taddy.org/
    :type episode: str
    """
    return """
    {
      getPodcastSeries(name: "OsProgramadores") {
        uuid
        name
        episodes(limitPerPage: 10, sortOrder: SEARCH, searchTerm: "$EPISODE") {
          uuid
          name
          description
          audioUrl
        }
      }
    }
    """.replace("$EPISODE", episode)

def taddy_get_episode(episode):
    # check for TADDY_API_KEY and TADDY_USER_ID is in env var and if not exit
    user_id = os.getenv('TADDY_USER_ID')
    api_key = os.getenv('TADDY_API_KEY')

    if api_key is None or user_id is None:
        print("Error: TADDY_API_KEY and TADDY_USER_ID environment variables are required.")
        print("Set then in a .env file from https://taddy.org/login")
        sys.exit(1)

    response = requests.post(TADDY_API,
                             json={"query": taddy_query(episode)},
                             headers={
                                 "X-API-KEY": api_key,
                                 "X-USER-ID": user_id
                             }
                             )
    # Check if the request was successful
    if response.status_code != 200:
        print(episode, "Search failed with status code", response.status_code)
        print(response.json())
        sys.exit(1)

    # Example response: docs/example_taddy_response.json
    json_response = response.json()

    # Check if the search was successful
    if 'errors' in json_response:
        print("Search failed:", json_response['errors'])
        sys.exit(1)

    # Get the unique episode searched, fail if more than one found
    episodes = list(json_response['data']['getPodcastSeries']['episodes'])
    if len(episodes) == 0:
        print("Search failed, no episodes found")
        sys.exit(1)
    if len(episodes) != 1:
        print("More than one episode found, narrow it down: ", episodes)
        sys.exit(1)

    episode_meta = episodes[0]

    return Episode(episode_meta['name'], episode_meta['audioUrl'], episode_meta['description'], get_utc_time())

def get_utc_time():
    now_utc = datetime.datetime.now(datetime.UTC)
    return now_utc.isoformat()

def download_episode(episode):
    # TODO: Maybe implement a way to force the download
    if not os.path.exists(episode):
        os.mkdir(episode)
    output_file = f'{episode}/episode.mp3'
    meta_file = f'{episode}/episode_meta.json'
    if not os.path.exists(output_file):
        print(f"Searching for {episode}")

        episode_meta = taddy_get_episode(episode)

        print(f'Downloading {episode_meta.name}')
        print(episode_meta.url)
        mp3 = requests.get(episode_meta.url)
        with open(output_file, 'wb') as f:
            f.write(mp3.content)
            print(f"MP3 saved to {output_file}")
        with open(meta_file, 'w') as f:
            json.dump(episode_meta._asdict(), f)
        return episode_meta
    else:
        print(f"Episode {episode} already downloaded")
        with open(meta_file, 'r') as f:
            episode_meta = Episode(**json.load(f))
            return episode_meta


def main():
    load_dotenv()
    if len(sys.argv) != 2:
        print("Usage: transcribe.py EXXX")
        sys.exit(1)

    episode = sys.argv[1]

    if not episode.startswith('E'):
        print("Error: The episode number must be in the format 'EXXX'.")
        sys.exit(1)

    episode_meta = download_episode(episode)

    transcribe = f"{episode}/transcribe_output.json"
    audio = f"{episode}/episode.mp3"
    if not os.path.exists(transcribe):
        print(f"Transcribing {episode_meta.name}")
        model = whisper.load_model("medium")
        result = model.transcribe(audio, verbose=True)
        with open(transcribe, 'w') as f:
            json.dump(result, f)
    else:
        print(f"Transcription for {episode} already exists")
        with open(transcribe, 'r') as f:
            result = json.load(f)

    lang = result['language']
    print(f"Outputting transcription for lang {lang}")
    writer = get_writer('all', episode)
    # Hack to output custom lang
    writer(result, f"{episode}/transcribe-{lang}.mp3", {})

if __name__ == "__main__":
    main()
