from ninja import Schema
from typing import List

class VideoSchema(Schema):
    videoID: str
    title: str
    videoURL: str

class SentenceSchema(Schema):
    id: int
    video: VideoSchema
    sentence: str
    start: float
    duration: float

class WordSchema(Schema):
    wordID: int
    word: str
    cnt: int

class IndexingSchema(Schema):
    word: WordSchema
    sentence: SentenceSchema
    position: int

class VideoResultSchema(Schema):
    videoURL:str
    start: float
    duration: float

