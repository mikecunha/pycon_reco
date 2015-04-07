#!/usr/bin/env python3

from bottle import route, run, request, static_file, get, response, hook
import pymongo

from datetime import datetime
from os import path, urandom
from base64 import b64encode
import sys
import re

try:
    client = pymongo.MongoClient('127.0.0.1', 27017, tz_aware=True)
    db = client.pycon
except:
    db = False

# for session id's in cookies
def generate_session():
    return str(b64encode(os.urandom(16)))


# read in related docs index
related_docs = {}
with open('rel_talks.txt', mode='rt', encoding='utf-8') as myfile:
    for doc_num, line in enumerate( myfile ):
        related_docs[str(doc_num)] = line.strip("\n").split(',')


rx = re.compile(u'([\u2014\-\u2019\n]|\.|\(|\)|\:|;|/|\[|\])', flags=re.UNICODE)

def sim_talks( dstring ):
    """ splits string of comma-delim docs into a list"""
    
    dstring = dstring.lower().strip(',')
    
    # replace punctuation with spaces
    dstring = rx.sub(" ", dstring )
    
    return [ doc_num.strip() for doc_num in dstring.split(',') ]
    
    
@route( '/rec', method='POST' )
def rec():
    """Handle ajax requests for related talks given a list 
    of doc ID's, return a list of related doc ID's """
    
    # FIXME do a proper connection class
    global db
    global client
    
    # Get list of requested talks to find rec's for
    response_val = { "talks": [] }
    inputval = request.forms.get('t')
    if inputval == None:
        return response_val
    elif inputval.strip(',') == '':
        return response_val
    else: 
        favd_docs = sim_talks( inputval )
        
    for fdoc in favd_docs:
        [ response_val['talks'].append(doc_id) for doc_id in related_docs[fdoc] ]
        
    if not db:
        # no databse, skip sessions and logging
        return response_val
    
    # handle user-session and logging
    if request.get_cookie("uid"):
        uid = request.get_cookie("uid")
    else:
        uid = generate_session()
        # 2592000 (30 days of seconds)
        response.set_cookie("uid", uid, secret=None, max_age=2592000 )
        
    # Gather info for logging and building a training set
    ip = request.get('REMOTE_ADDR')
    ua = request.get('HTTP_USER_AGENT')
    dt = datetime.now()
        
    # log favs to db for future training set
    try:
        db.sessions.update(
        { "_id": uid },
        { "$push": 
          { "favs": 
            { "talks": inputval.lower().strip(',').replace("$",""), 
              "ip": ip, 
              "user_agent": ua, 
              "time": dt } 
          }, "$inc": { "num_of_queries":1}
        },    
        upsert=True )
    except:
        # FIXME handle this better
        client = pymongo.MongoClient('127.0.0.1', 27017, tz_aware=True)
        db = client.pycon

    return response_val


@route('/milk_and', method='POST') 
def cookie():
    
    if request.get_cookie("uid"):
        return { }
    else:
        uid = generate_session()
        # 2592000 (30 days in seconds)
        response.set_cookie("uid", uid, secret=None, max_age=2592000 )

    return { }

if __name__ == '__main__':
    
    # need this if you're not serving the html page on localhost 
    # e.g. you're using file:///* in the browser
    @hook('after_request')
    def enable_cors():
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    run(host='localhost', port=8181)