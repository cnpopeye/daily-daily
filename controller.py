#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

def create_notebook(client):
    try:
        notebook = Types.Notebook()
        notebook.name = "Daily Daily"
        note_store = client.get_note_store()
        new_notebook = note_store.createNotebook(notebook)
    except Errors.EDAMUserException,e:
        logging.error("CreateNoteBook Error",e)
    return new_notebook.guid

def create_note(client):
    pass

def append_status(client, status):
    pass
