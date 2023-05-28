from bs4 import BeautifulSoup
import requests
import os

def download_podcasts(file):
    if not os.path.exists(file):
        print(f"File '{file}' not found.")
        return

    try:
        with open(file, 'r') as f:
            data = f.read()
    except Exception as e:
        print(f"Failed to read the file '{file}'. Error: {e}")
        return

    try:
        bs_data = BeautifulSoup(data, "xml")
    except Exception as e:
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

                mp3_file = os.path.join(podcast_dir, f"{episode['title']}.mp3")

                if not os.path.exists(mp3_file):
                    print(f"Downloading {episode['title']}...")
                    try:
                        mp3_data = requests.get(mp3_url).content
                    except Exception as e:
                        print(f"Failed to download the episode '{episode['title']}'. Error: {e}")
                        continue

                    try:
                        with open(mp3_file, 'wb') as handler:
                            handler.write(mp3_data)
                    except Exception as e:
                        print(f"Failed to write the episode '{episode['title']}' to a file. Error: {e}")
                        continue
                else:
                    print(f"{episode['title']} already exists. Skipping download.")

download_podcasts('overcast.opml')
