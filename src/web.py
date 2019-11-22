#!/usr/bin/python3

from flask import Flask, escape, request, render_template
from model.mainClass import Spot
app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get('name', 'world')
    return f'Hello, {escape(name)}!'

@app.route('/spotify/')
@app.route('/spotify/<query>')
def queueSong(query=None):
    spotify = Spot()
    spotify.authenticate()

    if query is not None:
        spotify.singleQuery(query)
        result = "Added {} to playback queue".format(query)

        return render_template('query.html', query=query, result=result)

    else:
        result = "Did not add anything to playlist."
        return render_template('query.html', query=query, result=result)
