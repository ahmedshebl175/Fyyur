#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime

from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='showv', lazy=True)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='showa', lazy=True)
   
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  dat = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  d = []
  
  venues_all = Venue.query.order_by('city').all()
  venue_city = ""
  for venue in venues_all:
    if venue_city == venue.city:
      continue
    else:
      venue_city = venue.city
    venues_city = Venue.query.filter_by(city=venue.city).all()
    venues_list = []
    for v in venues_city:
      shows = Show.query.filter(Show.dat > datetime.now()).filter_by(venue_id=v.id).count()
      
      venues_list.append({
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": shows,
      })
    d.append({
        "city": venue.city,
        "state": venue.state,
        "venues": venues_list,
      })

  data = d

    
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venues = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all()
  venues_count = Venue.query.filter(Venue.name.ilike("%" + request.form['search_term'] + "%")).count()
  
  d = []
  for venue in venues:
    shows = Show.query.filter(Show.dat > datetime.now()).filter_by(venue_id=venue.id).count()
    d.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": shows,
    })
    
  response = {
    "count": venues_count,
    "data": d
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venues = Venue.query.all()
 
  data_all = []
  
  for venue in venues:
    shows_upcoming_count = Show.query.filter(Show.dat > datetime.now()).filter_by(venue_id=venue.id).count()
    shows_past_count = Show.query.filter(Show.dat < datetime.now()).filter_by(venue_id=venue.id).count()
    shows_upcoming = Show.query.filter(Show.dat > datetime.now()).filter_by(venue_id=venue.id).all()
    artists_upcoming=[]
    for show in shows_upcoming:
      artist = Artist.query.get(show.artist_id)
      artists_upcoming.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.dat),
      })
      
    shows_past = Show.query.filter(Show.dat < datetime.now()).filter_by(venue_id=venue.id).all()
    artists_past=[]
    for show in shows_past:
      artist = Artist.query.get(show.artist_id)
      artists_past.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.dat),
      })
    d = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(', '),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": artists_past,
      "upcoming_shows": artists_upcoming,
      "past_shows_count": shows_past_count,
      "upcoming_shows_count": shows_upcoming_count,
    }

    data_all.append(d)

  data = list(filter(lambda d: d['id'] == venue_id, data_all))[0]
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  except():
    db.session.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except():
    db.session.rollback()
  finally:
    db.session.close()
    
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = []
  d = []
  
  artists_all = Artist.query.all()
  
  for artist in artists_all:
    d.append({
      "id": artist.id,
      "name": artist.name,
    })

  data = d

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  artists = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
  artists_count = Artist.query.filter(Artist.name.ilike("%" + request.form['search_term'] + "%")).count()
  
  d = []
  for artist in artists:
    shows = Show.query.filter(Show.dat > datetime.now()).filter_by(artist_id=artist.id).count()
    d.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": shows,
    })
    
  response = {
    "count": artists_count,
    "data": d
  }


  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #######################################################################################
  artists = Artist.query.all()
 
  data_all = []
  
  for artist in artists:
    shows_upcoming_count = Show.query.filter(Show.dat > datetime.now()).filter_by(artist_id=artist.id).count()
    shows_past_count = Show.query.filter(Show.dat < datetime.now()).filter_by(artist_id=artist.id).count()
    shows_upcoming = Show.query.filter(Show.dat > datetime.now()).filter_by(artist_id=artist.id).all()
    venues_upcoming=[]
    for show in shows_upcoming:
      venue = Venue.query.get(show.venue_id)
      venues_upcoming.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.dat),
      })
      
    shows_past = Show.query.filter(Show.dat < datetime.now()).filter_by(artist_id=artist.id).all()
    venues_past=[]
    for show in shows_past:
      venue = Venue.query.get(show.venue_id)
      venues_past.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.dat),
      })
    d = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(', '),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": venues_past,
      "upcoming_shows": venues_upcoming,
      "past_shows_count": shows_past_count,
      "upcoming_shows_count": shows_upcoming_count,
    }

    data_all.append(d)

  # data = list(filter(lambda d: d['id'] == venue_id, data_all))[0]
  #######################################################################################





  
  data = list(filter(lambda d: d['id'] == artist_id, data_all))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_current = Artist.query.get(artist_id)
  artist = {
    "id": artist_current.id,
    "name": artist_current.name,
    "genres": artist_current.genres.split(', '),
    "city": artist_current.city,
    "state": artist_current.state,
    "phone": artist_current.phone,
    "website": artist_current.website,
    "facebook_link": artist_current.facebook_link,
    "seeking_venue": artist_current.seeking_venue,
    "seeking_description": artist_current.seeking_description,
    "image_link": artist_current.image_link
  }
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form['genres']
    artist.facebook_link = request.form['facebook_link']
    
    db.session.add(artist)
    db.session.commit()
  except():
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_current = Venue.query.get(venue_id)
  venue = {
    "id": venue_current.id,
    "name": venue_current.name,
    "genres": venue_current.genres.split(', '),
    "address": venue_current.address,
    "city": venue_current.city,
    "state": venue_current.state,
    "phone": venue_current.phone,
    "website": venue_current.website,
    "facebook_link": venue_current.facebook_link,
    "seeking_talent": venue_current.seeking_talent,
    "seeking_description": venue_current.seeking_description,
    "image_link": venue_current.image_link
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form['genres']
    venue.facebook_link = request.form['facebook_link']
    
    db.session.add(venue)
    db.session.commit()
  except():
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
  except():
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.all()
 
  data_all = []
  
  for show in shows:
    show_artist = Artist.query.get(show.artist_id)
    show_venue = Venue.query.get(show.venue_id)

    d = {
      "venue_id": show.venue_id,
      "venue_name": show_venue.name,
      "artist_id": show.artist_id,
      "artist_name": show_artist.name,
      "artist_image_link": show_artist.image_link,
      "start_time": str(show.dat),
    }

    data_all.append(d)

  data = data_all
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    dat = request.form['start_time']
    show = Show(artist_id=artist_id, venue_id=venue_id, dat=dat)
    db.session.add(show)
    db.session.commit()
  except():
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
