#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-03 10:48:04
# @Author  : awakeljw (liujw15@mails.tsinghua.edu.cn)
# @Link    : http://blog.csdn.net/awakeljw/
# @Version : $Id$

import os
from flask import Flask, render_template, session, redirect, url_for, flash,abort
from wtforms import StringField, SubmitField,TextAreaField,PasswordField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_moment import Moment
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from flask_uploads import UploadSet, configure_uploads,IMAGES,patch_request_class

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/tensorflow/sqlite/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['UPLOADED_PHOTOS_DEST'] = os.path.abspath(os.path.join(os.getcwd(),"static/Gravatar"))
db = SQLAlchemy(app)
app.debug = True
app.secret_key = 's3cr3'

photos = UploadSet('photos',IMAGES)
configure_uploads(app, photos)
patch_request_class(app, 32*1024*1024)

class User( db.Model):
	__tablename__ = 'user'
#	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), primary_key=True)
	phone = db.Column(db.String(128))
	location = db.Column(db.String(128))
	about_me = db.Column(db.Text())
	file_url = db.Column(db.Text())
	current_time = db.Column(db.DateTime, default = datetime.utcnow)
	def __repr__(self):
		return "<User %r>" %self.username

class UploadForm( FlaskForm ):
	photo = FileField(validators = [FileAllowed(photos,u'upload your photo'),FileRequired(u'choosen')])
	submit = SubmitField(u'upload')

class NameForm( FlaskForm ):
	name = StringField("Name", validators = [Required()])
	phone = StringField("Phone", validators = [Length(0,64)])
	location = StringField("location", validators = [Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

@app.route('/user/<username>', methods=['GET','POST'])
def user(username):
	form2 = UploadForm()
	if form2.validate_on_submit():
		filename = photos.save(form2.photo.data)
		file_url = photos.url(filename)
	else:
		file_url = None
		filename = None
	if filename is None:
		fn='default.png'
	else:
		fn=filename
	fn = os.path.abspath(os.path.join(app.config['UPLOADED_PHOTOS_DEST'],fn))
	user = User.query.filter_by(username = username).first()
	if user is None:
		abort(404)
	return render_template('user.html', user = user, form2 = form2,
							file_url = file_url, filename = fn)
#	return render_template('user.html')


@app.route('/', methods=['GET','POST'])
def edit_profile():
	form2 = UploadForm()
	form1 = NameForm()

	if form2.validate_on_submit():
		filename = photos.save(form2.photo.data)
		file_url = photos.url(filename)
	else:
		file_url = None
		filename = None
	if filename is None:
		fn='default.png'
	else:
		fn=filename

	fn = os.path.abspath(os.path.join(app.config['UPLOADED_PHOTOS_DEST'],fn))	

	if form1.validate_on_submit():
		name = session.get('name')
		about_me = session.get('about_me')
		location = session.get('location')
		phone = session.get('phone')

		user = User(username = form1.name.data, about_me = form1.about_me.data,
					phone = form1.phone.data, location = form1.location.data,
					file_url = file_url,
					current_time = datetime.utcnow())
		db.create_all()
		db.session.add(user)
		flash('Your profile has been updated!')
		return redirect(url_for('.user', username = form1.name.data))
	

	session['name'] = form1.name.data
	session['about_me'] = form1.about_me.data
	session['phone'] = form1.phone.data
	session['location'] = form1.location.data
	return render_template('edit_profile.html',
							form1 = form1,form2 = form2,
							file_url = file_url, filename = fn,
							current_time=datetime.utcnow())


if __name__ == '__main__':
	app.run()