#!/usr/bin/env python3
import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    picture = Column(String(250))


class Store(Base):
    __tablename__ = 'store'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


class GoodsList(Base):
    __tablename__ = 'goods_list'
    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    model = Column(String(250))
    price = Column(String(8))
    goodtype = Column(String(250))
    store_id = Column(Integer, ForeignKey('store.id'))
    store = relationship(Store)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self. name,
            'model': self. model,
            'price': self. price,
            'goodtype': self. gdtype,
            'id': self. id
        }


engine = create_engine('sqlite:///electronicgoods.db')
Base.metadata.create_all(engine)
