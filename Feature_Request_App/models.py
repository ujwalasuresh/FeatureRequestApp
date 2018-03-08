from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
#import enum
import json

Base = declarative_base()


class ClientName():
    """
    class to declare enum on possible client names
    """
    CLIENT_A = 'Client A'
    CLIENT_B = 'Client B'
    CLIENT_C = 'Client C'

    def client_list(self):
        return [self.CLIENT_A, self.CLIENT_B, self.CLIENT_C]


class ProductArea():
    """
    class to declare enum in possible product areas
    """
    POLICIES = 'Policies'
    BILLING = 'Billing'
    CLAIM = 'Claims'
    REPORTS = 'Reports'

    def production_area_list(self):
        return [self.POLICIES, self.BILLING, self.CLAIM, self.REPORTS]


# Model classes to declare schema of the DB
class RequestTicket(Base):
    """
    Schema to declare table of requests
    """
    __tablename__ = 'request_ticket'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    title = Column(String(50))
    description = Column(String(200))
    client = Column(Enum('Client A', 'Client B', 'Client C'))
    client_priority = Column(Integer)
    target_date = Column(DateTime)
    ticket_url = Column(String(100))
    product_area = Column(Enum('Policies', 'Billing', 'Claims', 'Reports'))
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, ind, title, description, client, client_priority, target_date, ticket_url, product_area, user_id):
        self.id = ind
        self.title = str(title)
        self.description = str(description)
        self.client = client
        self.client_priority = int(client_priority)
        self.target_date = target_date
        self.ticket_url = ticket_url     # to be updated right after getting an id
        self.product_area = product_area
        self.user_id = user_id

    def __str__(self):
        return json.dumps(self.serialize, indent=4)

    def __repr__(self):
        return json.dumps(self.serialize)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {u"id": self.id,
                u"title": self.title,
                u"description": self.description,
                u"client": self.client,
                u"client_priority": self.client_priority,
                u"target_date": str(self.target_date),
                u"ticket_url": str(self.ticket_url),
                u"product_area": self.product_area,
                u"user_id": self.user_id}

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    username = Column(String(30))
    email = Column(String(50))
    password = Column(String(200))
    request_tickets = relationship('RequestTicket', backref='user')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return json.dumps(self.serialize, indent=4)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {u"id": self.id,
                u"username": self.username,
                u"email": self.email}