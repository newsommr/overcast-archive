from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime

def download_podcasts(file):
    if not os.path.isfile(file):
        print(f"File '{file}' not found.")
        return

    with open(file, 'r') as f:
        data = f.read()

    try:
        bs_data = BeautifulSoup(data, "xml")
    except AttributeError as e:
        print(f"Failed to parse the file '{file}' as XML. Error: {e}")
        return

    podcasts = bs_data.find_all('outline', {'type': 'rss'})
    podcast_names = [podcast['title'] for podcast in podcasts]

    print("Available podcasts:")
    for i, name in enumerate(podcast_names, start=1):
        print(f"{i}. {name}")

    selected_podcasts = input("Enter the numbers of the podcasts you want to download, separated by commas, or 'all' to download all: ")

    if selected_podcasts.lower() == 'all':
        selected_podcasts = list(range(1, len(podcast_names) + 1))
    else:
        try:
            selected_podcasts = [int(num.strip()) for num in selected_podcasts.split(",")]
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas, or 'all' to download all.")
            return

    for i in selected_podcasts:
        try:
            podcast = podcasts[i-1]
            podcast_name = podcast_names[i-1]
        except IndexError:
            print(f"No podcast found with the number {i}.")
            continue

        podcast_dir = os.path.join('podcasts', podcast_name)
        if not os.path.exists(podcast_dir):
            os.makedirs(podcast_dir)

        episodes = podcast.find_all('outline')

        for episode in episodes:
            if 'played' in episode.attrs and episode['played'] == '1':
                mp3_url = episode.get('enclosureUrl', None)
                if mp3_url is None:
                    print(f"No URL found for the episode '{episode.get('title', '')}'. Skipping.")
                    continue

                # Format pubDate
                pub_date = episode.get('pubDate', '')
                formatted_date = ''
                try:
                    dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%S%z")
                    formatted_date = dt.strftime('%Y-%m-%d')
                except ValueError:
                    print(f"Could not parse date '{pub_date}' for episode '{episode.get('title', '')}'.")

                # Append formatted pubDate to episode title
                mp3_file = os.path.join(podcast_dir, f"{formatted_date}: {episode['title']}.mp3")

                if not os.path.exists(mp3_file):
                    print(f"Downloading {episode['title']}...")
                    try:
                        with requests.get(mp3_url, stream=True) as r:
                            r.raise_for_status()
                            with open(mp3_file, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                    except Exception as e:
                        print(f"Failed to download the episode '{episode['title']}'. Error: {e}")
                        continue
                else:
                    print(f"{episode['title']} already exists. Skipping download.")

download_podcasts('overcast.opml')
