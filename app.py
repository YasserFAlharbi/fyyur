#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String))
    seeking = db.Column(db.CHAR)
    seeking_description = db.Column(db.String)
    website = db.Column(db.String)
    shows = db.relationship('Show', backref='Venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String))
    seeking = db.Column(db.CHAR)
    seeking_description = db.Column(db.String)
    website = db.Column(db.String)
    shows = db.relationship('Show', backref='Artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  time = db.Column(db.DateTime())
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  print('==========================meow==============================')
  print(Venue.query.all())
  print('==========================meow==============================')
  cities = set()
  for venue in Venue.query.all():
    cities.add((venue.city, venue.state))
  cities= list(cities)
  print('==========================meow==============================')
  print(cities)
  print('==========================meow==============================')
  for city in cities:
    temp = Venue.query.filter_by(city=city[0], state=city[1]).all()
    tempVenues = []
    for venue in temp:
      tempVenues.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).count()
      })
    data.append({
      'city': city[0],
      'state': city[1],
      'venues': tempVenues
    })
  print('==========================meow==============================')
  print(data)
  print('==========================meow==============================')

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  key = request.form.get('search_term')
  count = Venue.query.filter(Venue.name.ilike('%'+ key + '%')).count()
  temp = Venue.query.filter(Venue.name.ilike('%'+ key + '%')).all()
  print('==========================meow==============================')
  print(temp, count)
  print('==========================meow==============================')
  tempVenues = []
  for venue in temp:
    tempVenues.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': Show.query.filter_by(venue_id=venue.id).count()
    })
  response = {
    'count': count,
    'data': tempVenues
  }
  print('==========================meow==============================')
  print(response)
  print('==========================meow==============================')
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  venue = Venue.query.get(venue_id)
  seeking = False
  if venue.seeking == 't':
    seeking = True
  print('==========================meow==============================')
  print(venue)
  print('==========================meow==============================')
  for show in Show.query.filter_by(venue_id=venue_id).all():
    if show.time >= datetime.now():
      artist = Artist.query.get(show.artist_id)
      upcoming_shows_count+=1
      upcoming_shows.append({
        'artist_id': show.artist_id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.time)
      })
    else:
      artist = Artist.query.get(show.artist_id)
      past_shows_count+=1
      past_shows.append({
        'artist_id': show.artist_id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.time)
      })
  data = {
    'id': venue_id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': seeking,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': past_shows_count,
    'upcoming_shows_count': upcoming_shows_count
  }
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
  form = VenueForm()
  print('==========================meow==============================')
  print(type(form.data['seeking']))
  print('==========================meow==============================')
  error = False
  try:
    venue = Venue(
    name = form.data['name'],
    city = form.data['city'],
    state = form.data['state'],
    address = form.data['address'],
    phone = form.data['phone'],
    image_link = form.data['image_link'],
    facebook_link = form.data['facebook_link'],
    genres = form.data['genres'],
    seeking = form.data['seeking'],
    seeking_description = form.data['seeking_description'],
    website = form.data['website']
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # on successful db insert, flash success
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + form.data['name'] + ' could not be listed.')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/delete/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id = venue_id)
    for show in shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if not error:
    flash('Venue ' + venue.name + ' was successfully deleted')
    return jsonify({ 'success': True })
  flash('Venue ' + venue.name + ' could not be deleted')
  return jsonify({ 'success': False })

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None
  ###### The button added ######

@app.route('/artists/delete/<artist_id>', methods=['DELETE'])
def delete_artists(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id = artist_id)
    for show in shows:
      db.session.delete(show)
    db.session.delete(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if not error:
    flash('Artist ' + artist.name + ' was successfully deleted')
    return jsonify({ 'success': True })
  flash('Artist ' + artist.name + ' could not be deleted')
  return jsonify({ 'success': False })

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None
  ###### The button added ######

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  print('==========================meow==============================')
  print(artists)
  print('==========================meow==============================')
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  key = request.form.get('search_term')
  count = Artist.query.filter(Artist.name.ilike('%'+ key +'%')).count()
  temp = Artist.query.filter(Artist.name.ilike('%'+ key +'%')).all()
  print('==========================meow==============================')
  print(temp, count)
  print('==========================meow==============================')
  tempArtists = []
  for artist in temp:
    tempArtists.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': Show.query.filter_by(artist_id=artist.id).count()
    })
  response = {
    'count': count,
    'data': tempArtists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  artist = Artist.query.get(artist_id)
  seeking = False
  if artist.seeking == 't':
    seeking = True
  print('==========================meow==============================')
  print(artist.genres)
  print('==========================meow==============================')
  for show in Show.query.filter_by(artist_id=artist_id).all():
    if show.time >= datetime.now():
      venue = Venue.query.get(show.venue_id)
      upcoming_shows_count+=1
      upcoming_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(show.time)
      })
    else:
      venue = Venue.query.get(show.venue_id)
      past_shows_count+=1
      past_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(show.time)
      })
  data = {
    'id': artist_id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': seeking,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows':upcoming_shows,
    'past_shows_count': past_shows_count,
    'upcoming_shows_count': upcoming_shows_count
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  print('==========================meow==============================')
  targetArtist = Artist.query.get(artist_id)
  artist = {
    "id": targetArtist.id,
    "name": targetArtist.name,
    "genres": targetArtist.genres,
    "city": targetArtist.city,
    "state": targetArtist.state,
    "phone": targetArtist.phone,
    "website": targetArtist.website,
    "facebook_link": targetArtist.facebook_link,
    "seeking_venue": targetArtist.seeking,
    "seeking_description": targetArtist.seeking_description,
    "image_link": targetArtist.image_link
  }
  print(artist)
  form = ArtistForm(
    name=artist['name'],
    city=artist['city'],
    state=artist['state'],
    phone=artist['phone'],
    image_link=artist['image_link'],
    genres=artist['genres'],
    facebook_link=artist['facebook_link'],
    website=artist['website'],
    seeking=artist['seeking_venue'],
    seeking_description=artist['seeking_description']
  )
  print('==========================meow==============================')
  print(form)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.data['name']
    artist.city = form.data['city']
    artist.state = form.data['state']
    artist.phone = form.data['phone']
    artist.image_link = form.data['image_link']
    artist.facebook_link = form.data['facebook_link']
    artist.genres = form.data['genres']
    artist.seeking = form.data['seeking']
    artist.seeking_description = form.data['seeking_description']
    artist.website = form.data['website']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  if not error:
    flash('Artist ' + form.data['name'] + ' was successfully Updated!')
  else:
    flash('An error occurred. Artist ' + form.data['name'] + ' could not be Updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  print('==========================meow==============================')
  targetVenue = Venue.query.get(venue_id)
  venue = {
    "id": targetVenue.id,
    "name": targetVenue.name,
    "genres": targetVenue.genres,
    "address": targetVenue.address,
    "city": targetVenue.city,
    "state": targetVenue.state,
    "phone": targetVenue.phone,
    "website": targetVenue.website,
    "facebook_link": targetVenue.facebook_link,
    "seeking_talent": targetVenue.seeking,
    "seeking_description": targetVenue.seeking_description,
    "image_link": targetVenue.image_link
  }
  print(venue)
  form = VenueForm(
    name=venue['name'],
    city=venue['city'],
    state=venue['state'],
    address=venue['address'],
    phone=venue['phone'],
    image_link=venue['image_link'],
    genres=venue['genres'],
    facebook_link=venue['facebook_link'],
    website=venue['website'],
    seeking=venue['seeking_talent'],
    seeking_description=venue['seeking_description']
  )
  print('==========================meow==============================')
  print(form)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.data['name']
    venue.city = form.data['city']
    venue.state = form.data['state']
    venue.address = form.data['address']
    venue.phone = form.data['phone']
    venue.image_link = form.data['image_link']
    venue.facebook_link = form.data['facebook_link']
    venue.genres = form.data['genres']
    venue.seeking = form.data['seeking']
    venue.seeking_description = form.data['seeking_description']
    venue.website = form.data['website']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  if not error:
    flash('Venue ' + form.data['name'] + ' was successfully Updated!')
  else:
    flash('An error occurred. Venue ' + form.data['name'] + ' could not be Updated.')

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
  form = ArtistForm()
  print('==========================meow==============================')
  print(form.data['genres'])
  print('==========================meow==============================')
  error = False
  try:
    artist = Artist(
    name = form.data['name'],
    city = form.data['city'],
    state = form.data['state'],
    phone = form.data['phone'],
    image_link = form.data['image_link'],
    facebook_link = form.data['facebook_link'],
    genres = form.data['genres'],
    seeking = form.data['seeking'],
    seeking_description = form.data['seeking_description'],
    website = form.data['website']
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
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
  data = []
  print('==========================meow==============================')
  print(Show.query.all())
  print('==========================meow==============================')
  shows = Show.query.all()
  for show in shows:
    tempVenue = Venue.query.get(show.venue_id)
    tempArtist = Artist.query.get(show.artist_id)
    data.append({
      'venue_id': show.venue_id,
      'venue_name': tempVenue.name,
      'artist_id': show.artist_id,
      'artist_name': tempArtist.name,
      'artist_image_link' : tempArtist.image_link,
      'start_time': str(show.time)
    })
  print('==========================meow==============================')
  print(data)
  print('==========================meow==============================')
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
  form = ShowForm()
  print('==========================meow==============================')
  print(form.data)
  print('==========================meow==============================')
  error = False
  try:
    show = Show(
    artist_id = form.data['artist_id'],
    venue_id = form.data['venue_id'],
    time = form.data['start_time']
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!')
  else:
    flash('An error occurred. Show could not be listed.')
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
