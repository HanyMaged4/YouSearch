from django.core.management.base import BaseCommand
import json
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from indexer.models import * 
import urllib.request
import re

class Command(BaseCommand):

    def handle(self, *args, **options):
        urls_path = Path(__file__).resolve().parents[2] / 'data' / 'urls.json'

        if not urls_path.exists():
            self.stderr.write(f"URLs file not found: {urls_path}")
            return

        with urls_path.open('r', encoding='utf-8') as file:
            url_list = json.load(file)

        for url in url_list:
            title = self.get_video_title(url)
            print(f"Processing: {title}")
            video_id = url.split("v=")[1].split("&")[0]
            try:
                video = Videos.objects.create(videoID = video_id , title = title , videoURL = url)
            except Exception as e:
                print("this videos has been downloaded before")    
                continue
            subtitles_path = Path(__file__).resolve().parents[2] / 'data' / 'subtitles'
            try:
                transcript = self.get_subtitels(url)
                print(f"Transcript for {title} downloaded!")

                for snippet in transcript:
                    text = snippet.get('text') if isinstance(snippet, dict) else getattr(snippet, 'text', '') 
                    start = snippet.get('start', 0.0) if isinstance(snippet, dict) else getattr(snippet, 'start', 0.0)
                    duration = snippet.get('duration', 0.0) if isinstance(snippet, dict) else getattr(snippet, 'duration', 0.0)

                    sentence = Sentences.objects.create(
                        video=video,
                        sentence=text.strip(),
                        start=start,
                        duration=duration,
                    )

                    words = re.findall(r"\w+", text)
                    for w in words:
                        word_obj, _ = Words.objects.get_or_create(word=w)
                        Indexing.objects.get_or_create(word=word_obj, sentence=sentence)
                
            except Exception as e:
                print(f"Could not Processes {url}: {e}")

    def get_video_title(self , url):
        title = ""
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
                title = re.search(r'<title>(.*?)</title>', html).group(1)
                title = title.replace(" - YouTube", "")

        except Exception as e:
            print(f"Error: {e}")
        return title
    
    def get_subtitels(self , url):
        video_id = url.split("v=")[1].split("&")[0]
        try:
            ytt_api = YouTubeTranscriptApi()
            return ytt_api.fetch(video_id)
        except Exception as e:
            print(f"Error: {e}")
            return None
