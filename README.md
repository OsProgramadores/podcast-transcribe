# OsProgramadores Podcast Transcribe

## Quick Start

Install dependencies.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure the environment.

Get Taddy API key here (free): https://taddy.org/dashboard/my-apps
```
cp .env.example .env
```

Transcribe a podcast.
```
python transcribe.py E78

Searching for E78
Downloading E78 - Willian Azevedo - Software Engineer
MP3 saved to E78/episode.mp3
Transcribing E78 - Willian Azevedo - Software Engineer
Detecting language using up to the first 30 seconds. Use `--language` to specify the language
Detected language: Portuguese
[00:00.000 --> 00:03.000]  Olá, gente. Mais um episódio aqui do podcast.
[00:03.000 --> 00:08.000]  Hoje eu tenho o prazer enorme de ter o William Zivido aqui comigo.
...
[01:01:57.000 --> 01:01:59.000]  Forte abraço. Até mais.
[01:01:59.000 --> 01:02:11.000]  Chegamos ao final de mais um episódio, agradeço a todos a atenção e o nosso site é osprogramadores.com, participem e até o próximo episódio.
[01:02:11.000 --> 01:02:13.000]  Um bom dia para todos.
Outputting transcription for lang pt
```

```
tree E78
E78
├── episode_meta.json
├── episode.mp3
├── transcribe_output.json
├── transcribe-pt.json
├── transcribe-pt.srt
├── transcribe-pt.tsv
├── transcribe-pt.txt
└── transcribe-pt.vtt
```

With an RTX 3060 mobile, this takes 5 minutes, it's a very resource heavy operation.

