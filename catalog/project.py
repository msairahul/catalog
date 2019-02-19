#!/usr/bin/env python3
from flask import Flask, render_template
from flask import request, redirect, jsonify
from flask import url_for, flash, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, GoodsList, Store, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Electronic Goods"

engine = create_engine('sqlite:///electronicgoods.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;height:300px;border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all Stores
@app.route('/')
@app.route('/home/')
def home():
    stores = session.query(Store).all()
    if 'username' not in login_session:
        return render_template('stores.html', stores=stores)
    else:
        return render_template('authstores.html', stores=stores)


# JSON APIs to view Restaurant Information
@app.route('/store/<int:store_id>/goods/JSON')
def storeGoodsJSON(store_id):
    store = session.query(Store).filter_by(id=store_id).one()
    items = session.query(GoodsList).filter_by(
        store_id=store_id).all()
    return jsonify(GoodsList=[i.serialize for i in items])


@app.route('/store/<int:store_id>/goods/<int:goods_id>/JSON')
def goodsListJSON(store_id, goods_id):
    Goods_List = session.query(GoodsList).filter_by(id=goods_id).one()
    return jsonify(GoodsList=Good_List.serialize)


@app.route('/store/JSON')
def storeJSON():
    stores = session.query(Store).all()
    return jsonify(store=[r.serialize for r in stores])


# Show a Store Items
@app.route('/store/<int:store_id>/')
@app.route('/store/<int:store_id>/goods/')
def showGoods(store_id):
    newlist = []
    store = session.query(Store).filter_by(id=store_id).one()
    creator = getUserInfo(store.user_id)
    list = session.query(GoodsList).filter_by(store_id=store_id).all()
    for i in range(len(list)):
        if list[i].goodtype not in newlist:
            newlist.append(list[i].goodtype)
    sess = login_session
    if(
        'username' not in sess or creator.id != login_session['user_id']
    ):
        return render_template(
            'plist.html',
            list=list,
            store=store,
            creator=creator,
            newlist=newlist)
    else:
        return render_template(
            'list.html',
            list=list,
            store=store,
            creator=creator,
            newlist=newlist)


# Create a new Store
@app.route('/store/new', methods=['GET', 'POST'])
def newStore():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newStore = Store(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newStore)
        flash('New Store %s has been created successfully' % newStore.name)
        session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('newStore.html')


# Edit details of a store
@app.route('/store/<int:store_id>/edit/', methods=['GET', 'POST'])
def editStore(store_id):
    editedStore = session.query(Store).filter_by(id=store_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedStore.user_id != login_session['user_id']:
        # return "<script>function myFunction() {alert('You cant edit the store
        # as you are not authorised.');}</script><body onload='myFunction()'>"
        flash('You cant edit this store as you are not authorized')
        return redirect(url_for('home'))
    if request.method == 'POST':
        editedStore.name = request.form['name']
        flash('Store edited %s' % editedStore.name)
        return redirect(url_for('home'))
    else:
        return render_template('editStore.html', store=editedStore)


# Delete a Store
@app.route('/store/<int:store_id>/delete/', methods=['GET', 'POST'])
def deleteStore(store_id):
    storeDelete = session.query(Store).filter_by(id=store_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if storeDelete.user_id != login_session['user_id']:
        # return ",script>function myFunction() {alert('You cant delete this
        # Store as you are not the authorized person to
        # delete');}</script><body onload='myFunction()'>"
        flash('You cant delete this store as you are not authorized')
        return redirect(url_for('home'))
    if request.method == 'POST':
        session.delete(storeDelete)
        flash('Store %s deleted successfully' % storeDelete.name)
        session.commit()
        return redirect(url_for('home', store_id=store_id))
    else:
        return render_template('deletestore.html', store=storeDelete)


# Create a new Item in the store
@app.route('/store/<int:store_id>/goods/new/', methods=['GET', 'POST'])
def newGoodsList(store_id):
    if 'username' not in login_session:
        return redirect('/login')
    store = session.query(Store).filter_by(id=store_id).one()
    if login_session['user_id'] != store.user_id:
        flash("You cant add items to this store as you are not authorized")
    if request.method == 'POST':
        newItem = GoodsList(
            name=request.form['name'],
            model=request.form['model'],
            price=request.form['price'],
            goodtype=request.form['goodtype'],
            store_id=store_id,
            user_id=store.user_id)
        session.add(newItem)
        session.commit()
        flash('New Good %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showGoods', store_id=store_id))
    else:
        return render_template('newGoodsList.html', store_id=store_id)


# Edit the Appliance in the store
@app.route(
    '/store/<int:store_id>/goods/<int:goods_id>/edit',
    methods=[
        'GET',
        'POST'])
def editGoodsList(store_id, goods_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedgood = session.query(GoodsList).filter_by(id=goods_id).one()
    store = session.query(Store).filter_by(id=store_id).one()
    if login_session['user_id'] != store.user_id:
        flash('You cant edit the goods in the store as you are not authorized')
    if request.method == 'POST':
        if request.form['name']:
            editedgood.name = request.form['name']
        if request.form['model']:
            editedgood.model = request.form['model']
        if request.form['price']:
            editedgood.price = request.form['price']
        if request.form['goodtype']:
            editedgood.goodtype = request.form['goodtype']
        session.add(editedgood)
        session.commit()
        flash('Successfully Edited')
        return redirect(url_for('showGoods', store_id=store_id))
    else:
        return render_template(
            'editGoodsList.html',
            store_id=store_id,
            goods_id=goods_id,
            item=editedgood)

# Delete an Appliance


@app.route(
    '/store/<int:store_id>/goods/<int:goods_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteGoodsList(store_id, goods_id):
    if 'username' not in login_session:
        return redirect('/login')
    store = session.query(Store).filter_by(id=store_id).one()
    itemToDelete = session.query(GoodsList).filter_by(id=goods_id).one()
    if login_session['user_id'] != store.user_id:
        flash("You cant delete goods in this store as you are not authorized")
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item successfully deleted')
        return redirect(url_for('showGoods', store_id=store_id))
    else:
        return render_template(
            'deleteGoodsList.html',
            item=itemToDelete,
            store_id=store_id)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
