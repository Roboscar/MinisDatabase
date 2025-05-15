from datetime import datetime

class Figurine:
    def __init__(self, id=None, name="", full_image="", thumbnail="", tags=None):
        self.id = id
        self.name = name
        self.full_image = full_image
        self.thumbnail = thumbnail
        self.tags = tags or []
        self.modified_date = datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data):
        instance = cls()
        instance.id = data.get('id')
        instance.name = data.get('name', '')
        instance.full_image = data.get('fullImage', '')
        instance.thumbnail = data.get('thumbnail', '')
        instance.tags = data.get('tags', [])
        instance.modified_date = data.get('modified_date', datetime.now().isoformat())
        return instance
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'fullImage': self.full_image,
            'thumbnail': self.thumbnail,
            'tags': self.tags,
            'modified_date': self.modified_date
        }