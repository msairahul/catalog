#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *

engine = create_engine('sqlite:///electronicgoods.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

FirstUser = User(
    name="Sai Rahul",
    email="msairahul98@gmail.com",
    picture='''https://lh3.googleusercontent.com/-JCLjkJnRqEM
               /AAAAAAAAAAI/AAAAAAAAAKA/_JsKq5kaSes/photo.jpg''')
session.add(FirstUser)
session.commit()

# Create sample Stores
store1 = Store(name="Jio Home Appliances",
               user_id=1)
session.add(store1)
session.commit()

store2 = Store(name="Airtel Home Appliances",
               user_id=1)
session.add(store2)
session.commit()

store3 = Store(name="Idea Home Appliances",
               user_id=1)
session.add(store3)
session.commit()

store4 = Store(name="Docomo Home Appliances",
               user_id=1)
session.add(store4)
session.commit()

# Create a sample of different goods for various stores for store1
goods_list1 = GoodsList(name="Vivo V11",
                        model="Vivo",
                        price="19500",
                        goodtype="Mobile",
                        user_id=1,
                        store=store1)
session.add(goods_list1)
session.commit()

goods_list2 = GoodsList(name="Samsung 32 Inch Basic Smart Full HD LED TV",
                        model="Samsung",
                        price="23510",
                        goodtype="Television",
                        user_id=1,
                        store=store1)
session.add(goods_list2)
session.commit()

goods_list3 = GoodsList(name="Dell Inspiron Intel Core i5 8th Gen 13.3-inch",
                        model="Dell",
                        price="56050",
                        goodtype="Laptop",
                        user_id=1,
                        store=store1)
session.add(goods_list3)
session.commit()


# Menu items for store2

goods_list1 = GoodsList(name="Dell Inspiron 5375 i7 8th Gen",
                        model="Dell",
                        price="65000",
                        goodtype="Laptop",
                        user_id=1,
                        store=store2)
session.add(goods_list1)
session.commit()

goods_list2 = GoodsList(name="HP 2350 i5 7th Gen",
                        model="HP",
                        price="58020",
                        goodtype="Laptop",
                        user_id=1,
                        store=store2)
session.add(goods_list2)
session.commit()


# Menu Items for store4
goods_list1 = GoodsList(name="Mi Max2",
                        model="Mi",
                        price="25000",
                        goodtype="Mobile",
                        user_id=1,
                        store=store4)
session.add(goods_list1)
session.commit()

goods_list2 = GoodsList(name="Sony Bravia",
                        model="Sony",
                        price="53020",
                        goodtype="Television",
                        user_id=1,
                        store=store4)
session.add(goods_list2)
session.commit()

print("Items have been inserted successfully")
