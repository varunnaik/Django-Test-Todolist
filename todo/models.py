from django.db import models
from django.contrib.auth.models import User  
\

class Item(models.Model):
    """A single todo item."""
    name = models.CharField(max_length = 100)
    notes = models.TextField(max_length = 500, blank=True)
    created = models.DateField(auto_now_add=True)
    priority = models.IntegerField(choices=(
        (0, 'Urgent'),
        (1, 'High'),
        (2, 'Normal'),
        (3, 'Low'),    
    ), default=0)
    due = models.DateField(null=True, blank=True)
    done = models.BooleanField(default=False)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return  self.name + " :: " + unicode(self.created) + " ::" + unicode(self.priority) + "::"