from indexer.models import *
from .schemas import IndexingSchema, VideoResultSchema, WordSchema
from typing import List, Dict, Optional
from collections import defaultdict


def search(words: List[str]) -> List[VideoResultSchema]:
    """Search for consecutive words and return video results."""
    if not words:
        return []
    
    positions: List[List[Indexing]] = []
    for word in words:
        searched_word = search_for_a_word(word)
        if not searched_word:
            return []  
        positions.append(searched_word)
    
    ans = positions[0]
    
    for i in range(1, len(positions)):
        ans = merge(ans, positions[i])
        if not ans:  
            return []
    
    results = []
    seen = set()  
    for indexing in ans:
        sentence = indexing.sentence
        key = (sentence.video.videoURL, sentence.start)
        if key not in seen:
            seen.add(key)
            results.append(VideoResultSchema(
                videoURL=sentence.video.videoURL,
                start=sentence.start,
                duration=sentence.duration
            ))
    
    return results 

def search_for_a_word(word) -> List[IndexingSchema]:
    word_obj = get_word_or_none(word)
    if word_obj is None:
        return []
    data = Indexing.objects.filter(word=word_obj).select_related('word', 'sentence', 'sentence__video')
    return list(data)

def get_word_or_none(word) -> WordSchema:
    try:
        return Words.objects.get(word=word)
    except Words.DoesNotExist:
        return None
    
def merge(word_list1: List, word_list2: List) -> List:
    if not word_list1 or not word_list2:
        return []    
    i = 0
    j = 0
    merged_list = []

    while i < len(word_list1) and j < len(word_list2):
        sent1_id = word_list1[i].sentence.id
        sent2_id = word_list2[j].sentence.id

        if sent1_id == sent2_id:
            pos1 = word_list1[i].posetion
            pos2 = word_list2[j].posetion
            
            if pos1 + 1 == pos2:
                merged_list.append(word_list2[j])
                i += 1
                j += 1
            elif pos1 < pos2:
                i += 1
            else:
                j += 1
        elif sent1_id < sent2_id:
            i += 1
        else:
            j += 1
    
    return merged_list
