#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
from pickle import TRUE
import dateutil.parser
import babel
from flask import(
Flask, render_template, request, Response, 
flash, redirect, url_for,abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import DateTime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost:5432/fyurr'

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
    website_link = db.Column(db.String(120), nullable=False)#______________
    seeking_description = db.Column(db.String(500), nullable = False)     #|
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False) #|-----Missing Fields
    genres = db.Column(db.JSON, nullable=False, default=[])               #|
    shows = db.relationship('Show', backref='venue', lazy=False)#__________|

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120), nullable=False)#______________
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)    #|
    seeking_description = db.Column(db.String(500), nullable = False)       #|-----Missing Fields
    shows = db.relationship('Show', backref='artist', lazy=False) #__________|

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

# db.create_all()
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
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
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
          }
          response['venues'].append(d)
          print(d)
      return response

    data=[City_States(city_state) for city_state in city_states]
    print(data)
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_request = request.form['search_term']
    venue_result = Venue.query.filter(
        Venue.name.ilike(f'%{search_request}%')).all()
    data = []
    for result in venue_result:
        data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(result.shows)
        })

    response = {
        "count": len(venue_result),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
   
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
      filter = Venue.query.get(venue_id)
      if (filter.genres == None):
        filter.genres = []
      if (filter == None):
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
            
      data={
        "id": filter.id,
        "name":filter.name,
        "genres": filter.genres,
        "address": filter.address,
        "city": filter.city,
        "state": filter.state,
        "phone": filter.phone,
        "website_link": filter.website_link,
        "facebook_link":filter.facebook_link,
        "image_link":filter.image_link,
        "seeking_description": filter.seeking_description,
        "seeking_talent": filter.seeking_talent,
        "past_shows": [VenueDetails(show) for show in past_shows],
        "upcoming_shows": [VenueDetails(show) for show in upcoming_shows],
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
      }
      print(filter.genres)
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
  error = False
  try:
    venue_name = request.form.get('name')
    venue_city = request.form.get('city')
    venue_state = request.form.get('state')
    venue_address = request.form.get('address')
    contact = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebookLink = request.form.get('facebook_link')
    imageLink = request.form.get('image_link')
    websiteLink = request.form.get('website_link')
    seekingTalent = request.form.get('seeking_talent')
    seekingDescription = request.form.get('seeking_description')
    name_dub = Venue.query.filter_by(name=venue_name).all()
   
    if error: 
        flash('An error occurred. Venue ' + request.form['venue_name'] + ' could not be listed.')
    if not error:
      flash('Venue ' + request.form['venue_name'] + ' was successfully listed!') 
    
    else:
        createVenue = Venue(name=venue_name, city=venue_city, state=venue_state, address=venue_address, phone=contact, genres=genres, facebook_link=facebookLink, image_link=imageLink, website_link=websiteLink, seeking_talent=seekingTalent, seeking_description=seekingDescription)
        print(createVenue.__dict__)
        db.session.add(createVenue)
        db.session.commit()

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()
    return render_template('pages/home.html')
      

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

      error=False
      try:
          venue_name = Venue.query.filter(Venue.id == 'venue_id').all()
          db.session.delete(venue_name)
          db.session.commit()
          flash('Venue successfully deleted!')
      except:
          error=True
          db.session.rollback()
          flash('Error: Venue could not be deleted')
          
      finally:
          db.session.close()

      return redirect(url_for('venues'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    user_search_request = request.form['search_term']
    artists_search_result = Artist.query.filter(
        Artist.name.ilike(f'%{user_search_request}%')).all()
    data = []

    for artist in artists_search_result:
        num_upcoming_shows = 0
        shows = db.session.query(Show).filter(Show.artist_id == artist.id)
        for show in shows:
            if(show.start_time > datetime.now()):
                num_upcoming_shows += 1

        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })
    response = {
        "count": len(artists_search_result),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

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
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    edit_form = ArtistForm(request.form)
    artist_to_update = Artist.query.filter(Artist.id == artist_id)

    # updated artist based on user input
    updated_artist_details = {
        "name": edit_form.name.data,
        "genres": edit_form.genres.data,
        "city": edit_form.city.data,
        "state": edit_form.state.data,
        "phone": edit_form.phone.data,
        "website": edit_form.website_link.data,
        "facebook_link": edit_form.facebook_link.data,
        "seeking_venue": edit_form.seeking_venue.data,
        "seeking_description": edit_form.seeking_description.data,
        "image_link": edit_form.image_link.data,
    }

    try:
        artist_to_update.update(updated_artist_details)
        db.session.commit()
        flash(f'Artist {edit_form.name.data}  was successfully updated!')
    except:
        db.session.rollback()
        flash(
            f'An error occurred. {edit_form.name.data} could not be updated.')
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).one()

  # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    form_submit = VenueForm(request.form)
    venue_to_update = Venue.query.filter(Venue.id == venue_id)
    updated_venue = {
        "name": form_submit.name.data,
        "genre": form_submit.genres.data,
        "address": form_submit.address.data,
        "city": form_submit.city.data,
        "state": form_submit.state.data,
        "phone": form_submit.phone.data,
        "website_link": form_submit.website_link.data,
        "facebook_link": form_submit.facebook_link.data,
        "seeking_talent": form_submit.seeking_talent.data,
        "seeking_description": form_submit.seeking_description.data,
        "image_link": form_submit.image_link.data
    }
    try:
        venue_to_update.update(updated_venue)
        db.session.commit()
        flash('Venue' + form_submit.name.data + ' was successfully updated!')
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Venue ' +
              form_submit.name.data +
            ' could not be updated.')
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
      form = ArtistForm(request.form)
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      error = False
      body = {}
      form = ArtistForm(request.form)
      id = form.id.data
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      genres = form.genres.data
      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      website = form.website_link.data
      venue = form.seeking_venue.data
      description = form.seeking_description.data
      try:
        artist = Artist(
          id=id,
          name=name,
          city=city,
          state=state,
          phone=phone,
          genres=genres,
          image_link=image_link,
          facebook_link=facebook_link,
          website=website,
          venue = venue,
          description=description
        )
        db.session.add(artist)
        db.session.commit()
        body['id'] = artist.id
        body['name'] = artist.name
        body['city'] = artist.city
        body['state'] = artist.state
        body['phone'] = artist.phone
        body['genres'] = artist.genres
        body['image_link'] = artist.image_link
        body['facebook_link'] = artist.facebook_link
        body['venue'] = artist.venue
        body['description'] = artist.description
      except:
          error = True
          db.session.rollback()
          print(sys.exc_info())
      if error: 
        flash('An error occurred. Venue ' + name + ' could not be listed.')
      if not error:
        flash('Artist ' + name + ' was successfully listed!')

      
      db.session.close()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      return render_template('pages/home.html')


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
  # TODO: insert form data as a new Show record in the db, instead
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
          # on successful db insert, flash success
          flash('Show was successfully listed!')
          print(createShow.__dict__)
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()

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
