from sources.mangaflix import MangaFlixSource
from sources.toonbr import ToonBrSource

_sources = {
    "MangaFlix": MangaFlixSource(),
    "ToonBr": ToonBrSource()
}

def get_all_sources():
    return _sources
