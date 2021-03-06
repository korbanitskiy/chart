from django.db import models


class PLC(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_PLC')
    name = models.CharField(max_length=50, db_column='PLC_Name')
    address = models.CharField(max_length=50, db_column='PLC_Adress')
    num = models.IntegerField(null=True, db_column='PLC_Num')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'PLC_List'


class Location(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Location')
    name = models.CharField(max_length=50, db_column='Location_Name')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'Location_List'


class Sensor(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Sensor')
    address = models.CharField(max_length=50, db_column='Adress_InPLC', null=True)
    description = models.CharField(max_length=250, db_column='Descr', null=True)
    egu = models.CharField(max_length=50, db_column='EGU', null=True)
    name = models.CharField(max_length=50, db_column='Name', null=True)
    plc = models.ForeignKey(PLC, db_column='ID_PLC')
    location = models.ForeignKey(Location, db_column='ID_Location')
    factor = models.FloatField(db_column='Factor', default=1)
    deadband = models.FloatField(db_column='Deadband', default=0)
    dublicate = models.BooleanField(db_column='Dublicate', default=1)

    def __unicode__(self):
        return self.description

    class Meta:
        db_table = 'Sensor_List'


class Value(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id')
    value = models.FloatField(null=True, db_column='Value')
    change = models.DateTimeField(db_column='ChangeDate')
    sensor = models.ForeignKey(Sensor, db_column='ID_Sensor', related_name='value_set')

    def __unicode__(self):
        return str(self.value)

    class Meta:
        db_table = 'Value_List'


class Trend(models.Model):
    number = models.IntegerField(db_column='Number')
    location = models.ForeignKey(Location, db_column='Location')
    trend1 = models.ForeignKey(Sensor, db_column='Trend1', blank=True, null=True, related_name='trend1')
    trend2 = models.ForeignKey(Sensor, db_column='Trend2', blank=True, null=True, related_name='trend2')
    trend3 = models.ForeignKey(Sensor, db_column='Trend3', blank=True, null=True, related_name='trend3')
    trend4 = models.ForeignKey(Sensor, db_column='Trend4', blank=True, null=True, related_name='trend4')
    trend5 = models.ForeignKey(Sensor, db_column='Trend5', blank=True, null=True, related_name='trend5')
    trend6 = models.ForeignKey(Sensor, db_column='Trend6', blank=True, null=True, related_name='trend6')
    trend7 = models.ForeignKey(Sensor, db_column='Trend7', blank=True, null=True, related_name='trend7')
    trend8 = models.ForeignKey(Sensor, db_column='Trend8', blank=True, null=True, related_name='trend8')
    color1 = models.CharField(max_length=50, default='#ff0000')
    color2 = models.CharField(max_length=50, default='#ffff00')
    color3 = models.CharField(max_length=50, default='#00ff00')
    color4 = models.CharField(max_length=50, default='#0000ff')
    color5 = models.CharField(max_length=50, default='#ff00e0')
    color6 = models.CharField(max_length=50, default='#ffa000')
    color7 = models.CharField(max_length=50, default='#00ffaf')
    color8 = models.CharField(max_length=50, default='#ab00ff')


    def __unicode__(self):
        return str(self.number)

    class Meta:
        db_table = 'Trend'