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

    # Example response:
    # json_response = { "data": { "getPodcastSeries": { "uuid": "bab14cf7-0d12-4a7d-ae60-5765c5373620", "name": "OsProgramadores", "episodes": [ { "uuid": "70d09240-7a73-4e6f-aeca-d11206231717", "name": "E75 (EN) - Brian Kernighan - Professor of Computer Science at Princeton University", "description": "<p>From <a href=\"https://en.wikipedia.org/wiki/Brian_Kernighan\">Brian's Wikipedia page</a>:<br>\n<br>\nBrian Wilson Kernighan is a Canadian <a href=\"https://en.wikipedia.org/wiki/Computer_scientist\">computer scientist</a>, he worked at <a href=\"https://en.wikipedia.org/wiki/Bell_Labs\">Bell Labs</a> and contributed to the development of <a href=\"https://en.wikipedia.org/wiki/Unix\">Unix</a> alongside Unix creators <a href=\"https://en.wikipedia.org/wiki/Ken_Thompson\">Ken Thompson</a> and <a href=\"https://en.wikipedia.org/wiki/Dennis_Ritchie\">Dennis Ritchie</a>. Kernighan's name became widely known through co-authorship of the first book on the <a href=\"https://en.wikipedia.org/wiki/C_(programming_language)\">C programming language</a> (<a href=\"https://en.wikipedia.org/wiki/The_C_Programming_Language\">The C Programming Language</a>) with Dennis Ritchie. Kernighan affirmed that he had no part in the design of the C language (\"it's entirely Dennis Ritchie's work\").[8] He authored many Unix programs, including <a href=\"https://en.wikipedia.org/wiki/Troff\">ditroff</a>. Kernighan is coauthor of the <a href=\"https://en.wikipedia.org/wiki/AWK\">AWK</a> and <a href=\"https://en.wikipedia.org/wiki/AMPL\">AMPL</a> programming languages. The \"K\" of K&amp;R C and of AWK both stand for \"Kernighan\". In collaboration with <a href=\"https://en.wikipedia.org/w/index.php?title=Shen_Lin&amp;action=edit&amp;redlink=1\">Shen Lin</a> he devised well-known <a href=\"https://en.wikipedia.org/wiki/Heuristic\">heuristics</a> for two <a href=\"https://en.wikipedia.org/wiki/NP-complete\">NP-complete</a> optimization problems: <a href=\"https://en.wikipedia.org/wiki/Graph_partition\">graph partitioning</a> and the <a href=\"https://en.wikipedia.org/wiki/Travelling_salesman_problem\">travelling salesman problem</a>. In a display of authorial equity, the former is usually called the <a href=\"https://en.wikipedia.org/wiki/Kernighan%E2%80%93Lin_algorithm\">Kernighan–Lin algorithm</a>, while the latter is known as the <a href=\"https://en.wikipedia.org/wiki/Lin%E2%80%93Kernighan_heuristic\">Lin–Kernighan heuristic</a>. Kernighan has been a Professor of Computer Science at <a href=\"https://en.wikipedia.org/wiki/Princeton_University\">Princeton University</a> since 2000 and is the Director of Undergraduate Studies in the Department of Computer Science. In 2015, he co-authored the book The Go Programming Language.</p>\n<p><strong>Links<br>\n</strong><a href=\"https://en.wikipedia.org/wiki/IBM_7090\">IBM 7094</a></p>\n<p><a href=\"https://en.wikipedia.org/wiki/Multics\">Multics</a></p>\n<p><a href=\"https://www.utoronto.ca/\">University of Toronto</a></p>\n<p><a href=\"https://en.wikipedia.org/wiki/Compatible_Time-Sharing_System\">CTSS</a></p>\n<p><a href=\"https://en.wikipedia.org/wiki/B_(programming_language)\">B programming Language</a></p>\n<p><a href=\"https://en.wikipedia.org/wiki/BCPL\">BCPL</a></p>\n<p><a href=\"https://go.dev/\">Go</a></p>\n<p><a href=\"https://openai.com/blog/chatgpt\">ChatGPT</a></p>\n<p><a href=\"htt...", "subtitle": null, "audioUrl": "https://anchor.fm/s/2e4db538/podcast/play/66036337/https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net%2Fstaging%2F2023-2-6%2Fbb3c967b-7f8f-9659-e85b-351ad4cc46b0.mp3" } ] } } }
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
