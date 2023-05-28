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

    # Find all the main 'outline' elements with type attribute 'rss' that represent individual podcasts
    podcasts = bs_data.find_all('outline', {'type': 'rss'})

    # Get a list of podcast names
    podcast_names = [podcast['title'] for podcast in podcasts]

    # Ask the user to select which podcasts to download
    print("Available podcasts:")
    for i, name in enumerate(podcast_names, start=1):
        print(f"{i}. {name}")

    selected_podcasts = input("Enter the numbers of the podcasts you want to download, separated by commas: ")
    try:
        selected_podcasts = [int(num.strip()) for num in selected_podcasts.split(",")]
    except ValueError:
        print("Invalid input. Please enter numbers separated by commas.")
        return

    for i in selected_podcasts:
        try:
            podcast = podcasts[i-1]  # list indices start at 0, but we displayed the list starting at 1
            podcast_name = podcast_names[i-1]
        except IndexError:
            print(f"No podcast found with the number {i}.")
            continue

        podcast_dir = os.path.join('podcasts', podcast_name)

        # Create a directory for the podcast if it doesn't exist
        if not os.path.exists(podcast_dir):
            os.makedirs(podcast_dir)

        # Find all the 'outline' elements within the current podcast that represent individual episodes
        episodes = podcast.find_all('outline')

        for episode in episodes:
            if 'played' in episode.attrs and episode['played'] == '1':  # The episode has been played
                mp3_url = episode.get('enclosureUrl', None)
                if mp3_url is None:
                    print(f"No URL found for the episode '{episode.get('title', '')}'. Skipping.")
                    continue

                mp3_file = os.path.join(podcast_dir, f"{episode['title']}.mp3")

                if not os.path.exists(mp3_file):  # Check if the file already exists
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

# Call the function
download_podcasts('overcast.opml')
