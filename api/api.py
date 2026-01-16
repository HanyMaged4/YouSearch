from ninja import NinjaAPI
from .utils import search
api = NinjaAPI()
from .schemas import VideoResultSchema

@api.get("/search", response=list[VideoResultSchema])
def search_videos(request, q: str):
    words = q.lower().split()
    for w in words:
        print(w)
    results = search(words)
    return results