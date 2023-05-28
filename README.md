## overcast_archive
This project downloads podcast episodes from your Overcast export and organizes them into specific folders for each podcast. The downloader checks if an episode has been played before attempting to download it, skipping any episodes that have already been downloaded.

You will need to download your `All data` export from [Overcast's account page](https://overcast.fm/account).

#### Installation

Clone this repository:

`git clone https://github.com/newsommr/overcast_archive.git`

Navigate into the project directory:

`cd podcast_downloader`

Install the required dependencies:

`pip install -r requirements.txt`

Move your `overcast.opml` file to the project folder

#### Usage

`python overcast_archive.py`
