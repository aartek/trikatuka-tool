__all__ = ['Playlist']

class Playlist:
    def __init__(self, item):
        self.id = item["id"]
        self.name = item["name"]
        self.public = item["public"]
        self.collaborative = item["collaborative"]