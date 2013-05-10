#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
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

def append_status(client, status):
    pass

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


