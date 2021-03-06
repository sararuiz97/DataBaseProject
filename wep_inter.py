from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from twitter_api import post_tweets, get_JSON
from json import loads

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    hash = TextField('Hashtag:', validators=[validators.required()])

@app.route("/test")
def test():
    return render_template('test.html')

@app.route("/graphFile.json")
def getJ():
    return render_template('graphFile.json')

@app.route("/getTweets/<string:hash>")
def getTweets(hash):
    tweets = get_JSON(hash)
    return redirect(url_for('test'))

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print (form.errors)
    if request.method == 'POST':
        hash=request.form['hash']
        print (hash)

        if form.validate():
            post_tweets(hash)
            return redirect(url_for('getTweets', hash = hash))
        else:
            flash('All the form fields are required. ')

    return render_template('postTweets.html', form=form)

if __name__ == "__main__":
    app.run()
