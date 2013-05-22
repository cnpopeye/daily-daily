#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
from datetime import datetime
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors
from evernote.api.client import EvernoteClient
import models as m
import config as conf


def update_user(access_token):
    "update or save user"
    client = get_evernote_client(access_token)
    user_store = client.get_user_store()
    user = user_store.getUser()
    if not user:
        return None
    if not m.update_user_evernote(user.id, user.username, access_token):
        return None
    return user

def get_notebook(id, access_token):
    "get notebook, if not exsits create it."
    client = get_evernote_client(access_token)
    note_store = client.get_note_store()
    guid = m.get_user_guid(id)
    if guid:
        notebook = note_store.getNotebook(guid)
    else:
        notebook = create_notebook(id, note_store)
    if not notebook:
        return None
    return notebook


def create_notebook(id, note_store):
    "create notebook and svaing to db"
    notebook = _create_notebook(conf.notebook_name, note_store)
    if not notebook:
        return None
    if not m.update_user_guid(id, notebook.guid):
        return None
    return notebook


def _create_notebook(name, note_store):
    try:
        notebook = Types.Notebook()
        notebook.name = name
        created_notebook = note_store.createNotebook(notebook)
    except Errors.EDAMUserException, e:
        logging.error("CreateNoteBook Error",e)
        return None
    return created_notebook


def makeNote(authToken, noteStore, noteTitle, noteBody, parentNotebook=None):
 	nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
	nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
	nBody += "<en-note>%s</en-note>" % noteBody

    ## Create note object
	ourNote = Types.Note()
	ourNote.title = noteTitle
	ourNote.content = nBody
 
	## parentNotebook is optional; if omitted, default notebook is used
	if parentNotebook and hasattr(parentNotebook, 'guid'):
		ourNote.notebookGuid = parentNotebook.guid
 
	## Attempt to create note in Evernote account
	try:
		note = noteStore.createNote(authToken, ourNote)
	except Errors.EDAMUserException, edue:
		## Something was wrong with the note data
		## See EDAMErrorCode enumeration for error code explanation
		## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
		print "EDAMUserException:", edue
		return None
	except Errors.EDAMNotFoundException, ednfe:
		## Parent Notebook GUID doesn't correspond to an actual notebook
		print "EDAMNotFoundException: Invalid parent notebook GUID", ednfe
		return None
	## Return created note object
	return note


def get_evernote_client_via_id(id):
    "using user.id get EvernoteClient"
    access_token = m.get_user_token(int(id))
    return get_evernote_client(access_token)

def get_evernote_client(access_token = None):
    "return EvernoteClient"
    if access_token:
        return EvernoteClient(
            token=access_token,
            sandbox=True)
    else:
        client = EvernoteClient(
            consumer_key=conf.consumer_key,
            consumer_secret=conf.consumer_secret,
            sandbox=True # Default: True
            )

        return client


def connect_facebook(id, user):
    return m.update_user_sns(id, user, "facebook")

def connect_twitter(id, user):
    return m.update_user_sns(id, user, "twitter")

def get_facebook_token(enid):
    return m.get_facebook_token(enid)

def get_twitter_token(enid):
    return m.get_twitter_token(enid)

def update_daily_facebook(enid, fbid, data):
    daily=[]
    for d in data["data"]:
        try:
            _daily = dict(
                ddid = d["id"],
                message = d["message"],
                created_time = datetime.strptime(
                                  d["created_time"],
                                  "%Y-%m-%dT%H:%M:%S+0000") )
        except:
            continue
        else:
            _daily.update(
                id = enid,
                sid = fbid,
                source = "facebook",
                picture = [d.get("full_picture")],
                description = d.get("description")
                )
        daily.append(_daily)
    return m.save_daily(daily)


def get_since_id(enid, twid):
    return m.get_since_id(enid, twid)

def get_media(data):
    "return media url list from entities"
    medias = []
    if not data:
        return None
    if not data.get("media"):
        return None
    for m in data.get("media"):
        if m.get("media_url"):
            medias.append(m.get("media_url"))
    return medias

def update_daily_twitter(enid, twid, data):
    daily = []
    for d in data:
        try:
            _daily = dict(
                ddid = d["id"],
                message = d["text"],
                created_time = datetime.strptime(
                                  d["created_at"],
                                  "%a %b %d %H:%M:%S +0000 %Y") )
        except:
            continue
        else:
            _daily.update(
                id = enid,
                sid = twid,
                source = "twitter",
                picture = get_media(d.get("entities") ),
                description = None
                )
        daily.append(_daily)

    return m.save_daily(daily)
        

def get_user(enid):
    return m.get_user(enid)
