from django.db import models

# Create your models here.
class Videos(models.Model):
    videoID = models.CharField(max_length=64 , primary_key=True)
    title = models.CharField(max_length=255)
    videoURL = models.URLField(max_length=500,unique=True)

    def __str__(self):
        return f"{self.title} ({self.videoID})"
    

class Words(models.Model):
    wordID = models.AutoField(primary_key=True)
    word = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return f"{self.word} ({self.wordID})"
    

class Sentences(models.Model):
    id = models.AutoField(primary_key=True)
    video = models.ForeignKey(Videos , on_delete=models.CASCADE)
    sentence = models.CharField(max_length=2064)
    start = models.FloatField()
    duration = models.FloatField()

class Indexing(models.Model):
    word = models.ForeignKey(Words , on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentences , on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('word', 'sentence')
    
    def __str__(self):
        return f"{self.word.word} in {self.video.videoID} [{self.start}-{self.end}]"
    