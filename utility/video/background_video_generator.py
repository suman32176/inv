import os
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_KEY')

def search_videos(query_string, orientation_landscape=True):
    print(f"Searching videos for query: '{query_string}' with orientation {'landscape' if orientation_landscape else 'portrait'}...")
    
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        print("Video search successful. Processing results...")
    else:
        print(f"Error searching videos: {response.status_code} - {response.text}")
    
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, json_data)
    
    return json_data

def getBestVideo(query_string, orientation_landscape=True, used_vids=[]):
    print(f"Getting best video for query: '{query_string}'...")
    vids = search_videos(query_string, orientation_landscape)
    videos = vids['videos']  # Extract the videos list from JSON

    # Filter and extract videos based on orientation
    if orientation_landscape:
        filtered_videos = [video for video in videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
    else:
        filtered_videos = [video for video in videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]

    print(f"Found {len(filtered_videos)} filtered videos based on dimensions.")
    
    # Sort the filtered videos by duration
    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15 - int(x['duration'])))
    print("Filtered and sorted videos by duration.")

    # Extract the top video URL
    for video in sorted_videos:
        for video_file in video['video_files']:
            if orientation_landscape:
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        print(f"Best video found: {video_file['link']}")
                        return video_file['link']
            else:
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        print(f"Best video found: {video_file['link']}")
                        return video_file['link']
    
    print("NO LINKS found for this round of search with query:", query_string)
    return None

def generate_video_url(timed_video_searches, video_server):
    timed_video_urls = []
    if video_server == "pexel":
        used_links = []
        print("Generating video URLs from Pexels...")
        for (t1, t2), search_terms in timed_video_searches:
            url = ""
            for query in search_terms:
                url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
                if url:
                    used_links.append(url.split('.hd')[0])
                    print(f"URL added for time segment [{t1}, {t2}]: {url}")
                    break
            timed_video_urls.append([[t1, t2], url])
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)

    print("Video URL generation completed.")
    return timed_video_urls
