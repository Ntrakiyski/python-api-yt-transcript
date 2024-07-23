import json
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_youtube_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    
    Args:
        url (str): The YouTube video URL.
    
    Returns:
        str: The extracted video ID or None if the URL is invalid.
    """
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/|playlist\?list=)?([^"&?\/\s]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^"&?\/\s]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"An error occurred while fetching the transcript: {e}")
        return None

def get_video_info(video_id):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestaudio/best',
            'noplaylist': True,
            'age_limit': None,
            'dump_json': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info
    except Exception as e:
        print(f"An error occurred while fetching video info: {e}")
        return None

def get_chapters(video_id):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestaudio/best',
            'noplaylist': True,
            'age_limit': None
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            chapters = info.get('chapters', [])
            return chapters
    except Exception as e:
        print(f"An error occurred while fetching the chapters: {e}")
        return None

def count_words(text):
    return len(text.split())

def get_chapter_text(transcript, start_time, end_time):
    chapter_text = []
    total_word_count = 0
    for entry in transcript:
        if entry['start'] >= start_time and entry['start'] < end_time:
            entry['videoURL'] = f"https://www.youtube.com/watch?v=L2IgJ3Mh0lI&t={int(entry['start'])}s"
            entry_word_count = count_words(entry['text'])
            entry['wordCount'] = entry_word_count
            chapter_text.append(entry)
            total_word_count += entry_word_count
    return chapter_text, total_word_count

def process_video_url(url):
    """
    This function processes the given video URL and extracts the YouTube video ID, 
    then fetches and returns video info, transcript, and chapters.
    
    Args:
        url (str): The video URL.
    
    Returns:
        dict: A dictionary containing video info, transcript, and chapters.
    """
    video_id = extract_youtube_video_id(url)
    
    if not video_id:
        return {"status": "error", "message": "Invalid YouTube URL"}
    
    transcript = get_transcript(video_id)
    chapters = get_chapters(video_id)
    video_info = get_video_info(video_id)
    
    if not transcript or not chapters or not video_info:
        return {"status": "error", "message": "Failed to retrieve transcript, chapters, or video info."}
    
    channel_url = video_info.get('uploader_url', '#')
    
    result = {
        'videoInfo': {
            'title': video_info.get('title', 'No Title'),
            'URL': f"https://www.youtube.com/watch?v={video_id}",
            'channelName': video_info.get('uploader', 'Unknown Channel'),
            'channelLink': channel_url,
            'thumbnail': video_info.get('thumbnail', '')
        },
        'chapters': []
    }
    
    for chapter in chapters:
        chapter_start = chapter.get('start_time', 0)
        chapter_end = chapter.get('end_time', 0)
        
        chapter['videoURL'] = f"https://www.youtube.com/watch?v={video_id}&t={int(chapter_start)}s"
        
        chapter_text, total_word_count = get_chapter_text(transcript, chapter_start, chapter_end)
        
        result['chapters'].append({
            'title': chapter.get('title', 'No Title'),
            'start': chapter_start,
            'end': chapter_end,
            'videoURL': chapter['videoURL'],
            'wordCount': total_word_count,
            'chapterText': chapter_text
        })
    
    return result
