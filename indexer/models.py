from django.db import models

# Create your models here.
class Videos(models.Model):
    videoID = models.CharField(max_length=64 , primary_key=True)
    title = models.CharField(max_length=255)
    videoURL = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.title} ({self.videoId})"
    

class Words(models.Model):
    wordID = models.AutoField(primary_key=True)
    word = models.CharField(max_length=255)
    cnt = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.word} ({self.WordID})"
    
class Indexing(models.Model):
    word = models.ForeignKey(Words , on_delete=models.CASCADE)
    video = models.ForeignKey(Videos , on_delete=models.CASCADE)
    start = models.FloatField()
    end = models.FloatField()
    
    class Meta:
        unique_together = ('word', 'video', 'start', 'end')
    
    def __str__(self):
        return f"{self.word.word} in {self.video.videoId} [{self.start}-{self.end}]"