from django.db import models
from django.contrib.auth.models import User
 
class Events(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    
    class Meta:
        db_table = "tblevents"
    
    @classmethod
    def get_all_events(cls, user):
        all_events = cls.objects.filter(user=user)
        out = []
        for event in all_events:
            out.append({
                'title': event.name,
                'id': event.id,
                'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
                'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
                'finished': event.finished,
            })
        return out
    
