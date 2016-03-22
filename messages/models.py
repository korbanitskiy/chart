from django.db import models
from sensors.models import PLC, Location


class MessageType(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    text = models.CharField(max_length=50, db_column='Type')

    class Meta:
        db_table = 'MessageType'


class Message(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    text = models.CharField(max_length=255, db_column='Text')
    address = models.CharField(max_length=50, db_column='Address')
    plc = models.ForeignKey(PLC, db_column='PLCID')
    type = models.ForeignKey(MessageType, db_column='TypeId')
    location = models.ForeignKey(Location, db_column='LocationId')

    class Meta:
        db_table = 'Message'


class MessageList(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    message = models.ForeignKey(Message, db_column='MessageID')
    state = models.BooleanField(db_column='State')
    value = models.FloatField(db_column='Value', blank=True, null=True)
    time_stamp = models.DateTimeField(db_column='TimeStamp')

    class Meta:
        db_table = 'MessageList'
