# app/models/bacula_models.py
from peewee import *
from datetime import datetime

database = SqliteDatabase('bacul.db')  # Will be configured later

class BaseModel(Model):
    class Meta:
        database = database

class Client(BaseModel):
    clientid = AutoField()
    name = CharField(unique=True)
    uname = CharField()
    autoprune = IntegerField(default=0)
    fileretention = IntegerField(default=0)
    jobretention = IntegerField(default=0)

class Pool(BaseModel):
    poolid = AutoField()
    name = CharField(unique=True)
    numvols = IntegerField(default=0)
    maxvols = IntegerField(default=0)
    useonce = IntegerField(default=0)
    usecatalog = IntegerField(default=0)
    acceptanyvolume = IntegerField(default=0)
    volretention = IntegerField(default=0)
    voluseduration = IntegerField(default=0)
    maxvoljobs = IntegerField(default=0)
    maxvolbytes = BigIntegerField(default=0)
    recyclepool = IntegerField(null=True)
    scratchpoolid = IntegerField(null=True)
    recycle = IntegerField(default=0)
    actiononpurge = IntegerField(default=0)

class Job(BaseModel):
    jobid = AutoField()
    job = CharField()
    name = CharField()
    type = CharField()
    level = CharField()
    clientid = ForeignKeyField(Client, backref='jobs')
    jobstatus = CharField()
    schedtime = DateTimeField()
    starttime = DateTimeField(null=True)
    endtime = DateTimeField(null=True)
    jobtdate = BigIntegerField(null=True)
    volsessionid = IntegerField(null=True)
    volsessiontime = IntegerField(null=True)
    jobbytes = BigIntegerField(default=0)
    jobfiles = IntegerField(default=0)
    joberrors = IntegerField(default=0)
    jobmissingfiles = IntegerField(default=0)

class FileSet(BaseModel):
    filesetid = AutoField()
    fileset = CharField()
    md5 = CharField(null=True)
    createtime = DateTimeField(default=datetime.now)

class Storage(BaseModel):
    storageid = AutoField()
    name = CharField(unique=True)
    autochanger = IntegerField(default=0)

class Media(BaseModel):
    mediaid = AutoField()
    volumename = CharField(unique=True)
    slot = IntegerField(default=0)
    poolid = ForeignKeyField(Pool, backref='media')
    mediatype = CharField()
    mediatypeid = IntegerField(default=0)
    labeltype = IntegerField(default=0)
    firstwritten = DateTimeField(null=True)
    lastwritten = DateTimeField(null=True)
    labeldate = DateTimeField(null=True)
    volbytes = BigIntegerField(default=0)
    volstatus = CharField()
    enabled = IntegerField(default=1)
    recycle = IntegerField(default=0)
    actiononpurge = IntegerField(default=0)
    volretention = BigIntegerField(default=0)
    voluseduration = BigIntegerField(default=0)
    maxvoljobs = IntegerField(default=0)
    maxvolfiles = IntegerField(default=0)
    maxvolbytes = BigIntegerField(default=0)
    inchanger = IntegerField(default=0)
    storageid = ForeignKeyField(Storage, backref='media', null=True)