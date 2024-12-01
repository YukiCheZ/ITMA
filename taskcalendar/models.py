from django.db import models
 
class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    
    class Meta:
        db_table = "tblevents"
        
    @classmethod
    def get_all_events(cls):
        all_events = cls.objects.all()
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