#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from pickle import TRUE
import sys
import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from Model import Venue, Artist, Show, db, app

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# app = Flask(__name__)
app.debug=True
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/fyyur'
db = SQLAlchemy(app)
#----------------------------------------------------------------------------#
# Models.
from Model import *
#----------------------------------------------------------------------------
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  city_states = {(venue.city, venue.state) for venue in venues}
  print(city_states)
  def City_States(city_states):
    city = city_states[0]
    state = city_states[1]
    response = {
      'city': city,
      'state': state,
      'venues': []
    }
    for venue in venues:
      if(venue.city == city and venue.state == state):
        d = {
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': db.session.query(Show).join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.today()).count()
          # Show.query.filter(Show.venue_id==venue.id, Show.start_time>datetime.today().count())
        }
        response['venues'].append(d)
        print(d)
    return response

  data=[City_States(city_state) for city_state in city_states]
  print(data)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  searchVenue = request.form.get("search_term", "")
  venues = Venue.query.filter(Venue.name.ilike(f'%{searchVenue}%')).all()
  count = Venue.query.filter(Venue.name.ilike(f'%{searchVenue}%')).count()
  
  # search for "band" should return "The Wild Sax Band".
  def SearchVenue(venues):
    num_upcoming_shows = 0
    for show in venues.shows:
      if show.start_time > datetime.today():
        num_upcoming_shows+=1


    d = {
      "id": venues.id,
      "name": venues.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    return d

  response={
    "count": count,
    "data": [SearchVenue(venue) for venue in venues]
  }
  print(response)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if (venue.genres == None):
    venue.genres = []
  if (venue == None):
    abort(404)
  
  def VenueDetails(details):
    show = details[0]
    artist = details[1]
    data = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    return data
  past_shows = db.session.query(Show,Artist).join(Artist).filter(Show.start_time<=datetime.today(),Show.venue_id==venue_id).all()
  upcoming_shows = db.session.query(Show,Artist).join(Artist).filter(Show.start_time>datetime.today(),Show.venue_id==venue_id).all()
  past_shows_count = db.session.query(Show).join(Venue).filter(Show.start_time<=datetime.today()).filter(Show.venue_id==venue_id).count()
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.start_time>datetime.today()).filter(Show.venue_id==venue_id).count()
          # Show.query.filter(Show.venue_id==venue.id, Show.start_time>datetime.today().count())
          # Show.query.filter(Show.start_time>datetime.today(),Show.venue_id==venue_id).count()
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link":venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [VenueDetails(show) for show in past_shows],
    "upcoming_shows": [VenueDetails(show) for show in upcoming_shows],
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  print(venue.genres)
    
 
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
  form = VenueForm()
  try:
    venueName = request.form.get('name')
    venueCity = request.form.get('city')
    venueState = request.form.get('state')
    venueAddress = request.form.get('address')
    contactNumber = request.form.get('phone')
    songGenres = request.form.getlist('genres')
    facebookLink = request.form.get('facebook_link')
    imageLink = request.form.get('image_link')
    websiteLink = request.form.get('website_link')
    seekingTalent = request.form.get('seeking_talent')
    seekingDescription = request.form.get('seeking_description')
    name_dub = Venue.query.filter_by(name=venueName).all()
    if (seekingTalent == 'y'):
      seekingTalent= True
    else:
      seekingTalent= False  
    if name_dub:
      flash('Venue ' + request.form['venueName'] + ' Already Exist!')
  
    else:
      createVenue = Venue(name=venueName, city=venueCity, state=venueState, address=venueAddress, phone=contactNumber, genres=songGenres, facebook_link=facebookLink, image_link=imageLink, website_link=websiteLink, seeking_talent=seekingTalent, seeking_description=seekingDescription)
      print(createVenue.__dict__)
      db.session.add(createVenue)
      db.session.commit()
      
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  form = VenueForm()
  try:
    
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    
  except Exception as e:
    print(f'Error ==> {e}')
    flash('An error occurred. Venue could not be deleted.')
    db.session.rollback()
    abort(400)
  finally:
    db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for("pages/venues.html"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    data = []
    artists = db.session.query(Artist.id, Artist.name).all()
    for artist in artists:
        artist = dict(zip(('id', 'name'), artist))
        data.append(artist)
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  searchArtists = request.form.get("search_term", "")
  artists = Artist.query.filter(Artist.name.ilike(f'%{searchArtists}%')).all()
  count = Artist.query.filter(Artist.name.ilike(f'%{searchArtists}%')).count()
  
  # search for "band" should return "The Wild Sax Band".
  def SearchArtist(artists):
    num_upcoming_shows = 0
    for show in artists.shows:
      if show.start_time > datetime.today():
        num_upcoming_shows+=1


    d = {
      "id": artists.id,
      "name": artists.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    return d

  response={
    "count": count,
    "data": [SearchArtist(artist) for artist in artists]
  }
  print(response)
  return render_template('pages/search_artists.html', results=response, searchArtists=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  if (artist.genres == None):
    artist.genres = []
  if (artist == None):
    abort(404)
  
  def ArtistDetail(details):
    show = details[0]
    venue = details[1]
    data = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time)
    }
    return data

  artist = Artist.query.get(artist_id)
  past_shows = db.session.query(Show,Venue).join(Venue).filter(Show.start_time<=datetime.today(),Show.artist_id==artist_id).all()
  upcoming_shows = db.session.query(Show,Venue).join(Venue).filter(Show.start_time>datetime.today(),Show.artist_id==artist_id).all()
  past_shows_count = Show.query.filter(Show.start_time<=datetime.today(),Show.artist_id==artist_id).count()
  upcoming_shows_count = Show.query.filter(Show.start_time>datetime.today(),Show.artist_id==artist_id).count()
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website":artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [ArtistDetail(show) for show in past_shows],
    "upcoming_shows": [ArtistDetail(show) for show in upcoming_shows],
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }

  if artist == None:
    abort(404)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.genres.data = artist.genres
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
 
  # TODO: populate form with fields from artist with ID <artist_id>
  # flash('Artist Data Updated Successfully')
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website')
    artist.genres = request.form.getlist('genres')
    artist.seeking_venue = request.form.get('seeking_venue')
    artist.seeking_description = request.form.get('seeking_description')
    if (artist.seeking_venue == 'y'):
      artist.seeking_venue= True
    else:
      artist.seeking_venue= False 
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  flash('Artist Details Updated Successfully')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.genres.data = venue.genres
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website')
    venue.genres = request.form.getlist('genres')
    venue.seeking_talent = request.form.get('seeking_talent')
    venue.seeking_description = request.form.get('seeking_description')
    if (venue.seeking_talent == 'y'):
      venue.seeking_talent= True
    else:
      venue.seeking_talent= False 
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  flash('Venue Details Updated Successfully')
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
  form = ArtistForm()
  try:
    artistName = request.form.get('name')
    artistCity = request.form.get('city')
    artistState = request.form.get('state')
    artistNumber = request.form.get('phone')
    artistGenres = request.form.getlist('genres')
    facebookLink = request.form.get('facebook_link')
    imageLink = request.form.get('image_link')
    websiteLink = request.form.get('website_link')
    seekingVenue = request.form.get('seeking_venue')
    seekingDescription = request.form.get('seeking_description')
    nameDub = Artist.query.filter_by(name=artistName).all()
    if (seekingVenue== 'y'):
      seekingVenue = True
    else:
      seekingVenue = False
    if nameDub:
      flash('Artist ' + request.form.get['artistName'] + ' Already Exist!')
  
    else:
      createArtist = Artist(name=artistName, city=artistCity, state=artistState,  phone=artistNumber, genres=artistGenres, facebook_link=facebookLink, image_link=imageLink, website_link=websiteLink, seeking_venue=seekingVenue, seeking_description=seekingDescription)
      print(createArtist.__dict__)
      db.session.add(createArtist)
      db.session.commit()
      
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  form = ShowForm()
  def displayShows(result):
    artist = result[0]
    venue = result[1]
    show = result[2]
    data = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
      # "start_time": show.start_time.isoformat()
    }
    return (data)
  results = db.session.query(Artist,Venue,Show).join(Artist).join(Venue).all()
  data = [displayShows(show) for show in results]
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm()
  try:
    artistID = request.form.get('artist_id')
    venueID = request.form.get('venue_id')
    startTime = request.form.get('start_time')
    artistDub = Show.query.filter_by(artist_id=artistID).all()
    venueDub = Show.query.filter_by(venue_id = venueID).all()
    startTimeDub = Show.query.filter_by(start_time = startTime).all()
    if (artistDub and venueDub and startTimeDub):
      flash('Show  Already Exist!')
    else:
      createShow = Show(artist_id=artistID, venue_id =venueID, start_time=startTime)
      db.session.add(createShow)
      db.session.commit()
      flash('Show was successfully listed!')
      print(createShow.__dict__)
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()


  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
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
