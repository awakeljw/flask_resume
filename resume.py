#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-03 10:48:04
# @Author  : awakeljw (liujw15@mails.tsinghua.edu.cn)
# @Link    : http://blog.csdn.net/awakeljw/
# @Version : $Id$

from flask import Flask, render_template, session, redirect, url_for, flash,abort
from wtforms import StringField, SubmitField,TextAreaField,PasswordField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_moment import Moment
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/tensorflow/sqlite/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
app.debug = True
app.secret_key = 's3cr3'

class User( db.Model):
	__tablename__ = 'user'
#	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), primary_key=True)
	phone = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	current_time = db.Column(db.DateTime, default = datetime.utcnow)
	def __repr__(self):
		return "<User %r>" %self.username


class NameForm( FlaskForm ):
	name = StringField("Name", validators = [Required()])
	phone = StringField("Phone", validators = [Length(0,64)])
	location = StringField("location", validators = [Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

@app.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		abort(404)
	if username in user.username:
		return render_template('user.html', user = user)
#	return render_template('user.html')


@app.route('/', methods=['GET','POST'])
def edit_profile():
	form = NameForm()
	if form.validate_on_submit():
		name = session.get('name')
		about_me = session.get('about_me')
		location = session.get('location')
		phone = session.get('phone')
		user = User(username = form.name.data, about_me = form.about_me.data,
					phone = form.phone.data, location = form.location.data,
					current_time = datetime.utcnow())
		db.create_all()
		db.session.add(user)
		flash('Your profile has been updated!')
		return redirect(url_for('.user', username = form.name.data))

	session['name'] = form.name.data
	session['about_me'] = form.about_me.data
	session['phone'] = form.phone.data
	session['location'] = form.location.data
	return render_template('edit_profile.html',
		form = form, current_time=datetime.utcnow())


if __name__ == '__main__':
	app.run()