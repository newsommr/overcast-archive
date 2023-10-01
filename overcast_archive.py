import concurrent.futures
import hashlib
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class PodcastDownloader:
    def __init__(self, source_file: str):
        """Initialize the PodcastDownloader object with the source_file path."""
        self.source_file = source_file
        self.downloaded_file = 'downloaded_episodes.txt'
        self.downloaded_episodes = self.load_downloaded_episodes()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filenames by replacing invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', ' ', filename)

    @staticmethod
    def hash_url(url: str) -> str:
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def load_downloaded_episodes(self) -> set:
        """Load downloaded episodes from the file."""
        try:
            with open(self.downloaded_file, 'r') as file:
                return set(line.strip() for line in file)
        except FileNotFoundError:
            return set()

    def download_episode(self, episode, podcast_dir):
        """Download a podcast episode."""
        if 'played' in episode.attrs and episode['played'] == '1':
            mp3_url = episode.get('enclosureUrl', None)
            if mp3_url is None:
                print(f"No URL found for the episode '{episode.get('title', '')}'. Skipping.")
                return

            url_hash = self.hash_url(mp3_url)
            if url_hash in self.downloaded_episodes:
                print(f"Episode '{episode['title']}' already exists. Skipping.")
                return

            # Handling date and formatting
            pub_date = episode.get('pubDate', '')
            formatted_date = ''
            try:
                dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%S%z")
                formatted_date = dt.strftime('%Y-%m-%d')
            except ValueError:
                print(f"Could not parse date '{pub_date}' for episode '{episode.get('title', '')}'.")

            sanitized_title = self.sanitize_filename(episode['title'])
            mp3_file = os.path.join(podcast_dir, f"{formatted_date} {sanitized_title}.mp3")

            # Downloading the episode
            print(f"Downloading {episode['title']}...")
            try:
                with requests.get(mp3_url, stream=True) as r:
                    r.raise_for_status()
                    with open(mp3_file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                with open(self.downloaded_file, 'a') as f:
                    f.write(f"{url_hash}\n")
            except Exception as e:
                print(f"Failed to download the episode '{episode['title']}'. Error: {e}")

    def download_podcasts(self):
        """Download podcasts listed in the source file."""
        if not os.path.isfile(self.source_file):
            print(f"File '{self.source_file}' not found.")
            return

        with open(self.source_file, 'r') as f:
            data = f.read()

        try:
            bs_data = BeautifulSoup(data, "xml")
        except AttributeError as e:
            print(f"Failed to parse the file '{self.source_file}' as XML. Error: {e}")
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
                selected_podcasts = [int(num.strip()) for num in selected_podcasts.split(",") if num.strip().isdigit()]
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas, or 'all' to download all.")
                return
            

        for i in selected_podcasts:
            try:
                podcast = podcasts[i - 1]
                podcast_name = podcast_names[i - 1]
            except IndexError:
                print(f"No podcast found with the number {i}.")
                continue

            podcast_dir = os.path.join('podcasts', self.sanitize_filename(podcast_name))
            os.makedirs(podcast_dir, exist_ok=True)

            episodes = podcast.find_all('outline')
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.download_episode, episodes, [podcast_dir] * len(episodes))



if __name__ == "__main__":
    downloader = PodcastDownloader('overcast.opml')
    downloader.download_podcasts()
    print("Complete.")
