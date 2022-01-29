# malacology-rss

This repository contains scripts for forwarding [diary.malacology.net](https://diary.malacology.net/) to Telegram.

## Usage

Create and edit `config.json` and `lastpost`, then:

```sh
python download.py index.xml
python process.py index.xml data.jsonl
python send.py data.jsonl
```
