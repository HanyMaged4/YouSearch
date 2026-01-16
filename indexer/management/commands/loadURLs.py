from django.core.management.base import BaseCommand
from django.db import transaction
import json
import re
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from indexer.models import Videos, Sentences, Words, Indexing
import urllib.request

class Command(BaseCommand):
    def handle(self, *args, **options):
        urls_path = Path(__file__).resolve().parents[2] / 'data' / 'urls.json'
        if not urls_path.exists():
            print(f"File not found: {urls_path}")
            return

        with urls_path.open('r', encoding='utf-8') as file:
            url_list = json.load(file)

        word_cache = {w.word: w for w in Words.objects.all()}
        print(f"Cache loaded with {len(word_cache)} words.")

        for url in url_list:
            video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
            if not video_id_match:
                print(f"Skipping invalid URL: {url}")
                continue
            
            video_id = video_id_match.group(1)
            
            if Videos.objects.filter(videoID=video_id).exists():
                print(f"Skipping: {video_id} already exists.")
                continue

            title = self.get_video_title(url)
            transcript = self.get_subtitels(video_id)
            
            if not transcript:
                print(f"No transcript found for: {title} ({video_id})")
                continue

            try:
                with transaction.atomic():
                    video = Videos.objects.create(videoID=video_id, title=title, videoURL=url)
                    print(f"Created Video object: {title}")
                    
                    sentences_to_create = []
                    for snippet in transcript:
                        text = snippet['text'] if isinstance(snippet, dict) else getattr(snippet, 'text', '')
                        start = snippet['start'] if isinstance(snippet, dict) else getattr(snippet, 'start', 0.0)
                        duration = snippet['duration'] if isinstance(snippet, dict) else getattr(snippet, 'duration', 0.0)

                        sentences_to_create.append(Sentences(
                            video=video,
                            sentence=text.strip(),
                            start=start,
                            duration=duration,
                        ))
                    
                    created_sentences = Sentences.objects.bulk_create(sentences_to_create)
                    print(f"Bulk created {len(created_sentences)} sentences.")

                    all_words_in_vid = set()
                    for snippet in transcript:
                        text = snippet['text'] if isinstance(snippet, dict) else getattr(snippet, 'text', '')
                        all_words_in_vid.update(re.findall(r"\w+", text.lower()))
                    
                    new_words_list = [Words(word=w) for w in all_words_in_vid if w not in word_cache]
                    if new_words_list:
                        Words.objects.bulk_create(new_words_list, ignore_conflicts=True)
                        added_words = Words.objects.filter(word__in=[nw.word for nw in new_words_list])
                        for w_obj in added_words:
                            word_cache[w_obj.word] = w_obj
                        print(f"Added {len(new_words_list)} new words to database.")

                    indexing_to_create = []
                    for i, snippet in enumerate(transcript):
                        sentence_obj = created_sentences[i]
                        text = snippet['text'] if isinstance(snippet, dict) else getattr(snippet, 'text', '')
                        words_in_order = re.findall(r"\w+", text.lower())
                        for pos, w in enumerate(words_in_order):
                            word_obj = word_cache.get(w)
                            if word_obj:
                                indexing_to_create.append(Indexing(word=word_obj, sentence=sentence_obj, posetion=pos))
                    
                    Indexing.objects.bulk_create(indexing_to_create, batch_size=1000)
                    print(f"Bulk created {len(indexing_to_create)} indexing records.")
                    print(f"Finished processing: {title}")
            except Exception as e:
                print(f"Error processing {url}: {e}")

    def get_video_title(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
                match = re.search(r'<title>(.*?)</title>', html)
                return match.group(1).replace(" - YouTube", "") if match else "Untitled"
        except:
            return "Untitled"

    def get_subtitels(self, video_id):
        try:
            ytt_api = YouTubeTranscriptApi()
            return ytt_api.fetch(video_id)
        except Exception as e:
            print(e)
            return None