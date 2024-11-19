# Create your models here.
from django.db import models
 
class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    
    class Meta:
        db_table = "tblevents"
