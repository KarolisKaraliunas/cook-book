import os
import math
from flask import Flask, render_template, redirect, url_for, request, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'online cookbook'
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", 'mongodb://localhost')
app.config['SECRET_KEY'] = os.urandom(24) 
mongo = PyMongo(app)


""" Variables """
users = mongo.db.users
recipes = mongo.db.recipes
cuisines = mongo.db.cuisines
dishes = mongo.db.dishes
allergens = mongo.db.allergens
