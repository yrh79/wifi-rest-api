import logging
import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import (Column,
                        Integer,
                        String,
                        ForeignKey,
                        JSON,
                        Sequence,
                        DateTime,
                        Text,
                        UniqueConstraint,
                        Index,
                       )
from sqlalchemy.dialects.mysql import INTEGER

from sqlalchemy.orm import relationship, backref

BaseModel = declarative_base()

class User(BaseModel):
    __tablename__ = 'mqtt_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=True, unique=True)
    password = Column(String(100), nullable=True)
    salt = Column(String(20), nullable=True)
    is_superuser = Column(INTEGER(display_width=1), nullable=True, default=0)
    created = Column(DateTime, nullable=True)
    def __str__(self):
        return self.username

class Acl(BaseModel):
    __tablename__ = 'mqtt_acl'

    id = Column(INTEGER(display_width=11), primary_key=True, autoincrement=True)
    allow = Column(INTEGER(display_width=1), nullable=True)
    ipaddr = Column(String(60), nullable=True)
    username = Column(String(100), nullable=True)
    clientid = Column(String(100), nullable=True)
    access = Column(INTEGER(display_width=2), nullable=False)
    topic = Column(String(100), nullable=False)
    def __str__(self):
        return self.username + ":" + self.topic

class Userdev(BaseModel):
    __tablename__ = 'user_dev'

    id = Column(INTEGER(display_width=11), primary_key=True, autoincrement=True)
    userid = Column(INTEGER(display_width=11), nullable=False)
    hwid = Column(String(12), nullable=False)
    devtype = Column(INTEGER(display_width=8), nullable=False)
    devname = Column(String(64), nullable=True)
    data = Column(String(1024), nullable=True)
    def __str__(self):
        return self.userid + ":" + self.hwid

