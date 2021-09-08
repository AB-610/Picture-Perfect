# All imports

from dotenv import load_dotenv
load_dotenv()
import os
from flask import Flask, render_template, request, make_response
import urllib.request as req
import ssl
import json
import requests
import urllib.parse
from werkzeug.exceptions import HTTPException
import imdb
import random

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Basic API information necessary for everything

api_key = os.getenv("api_key")
api_version = "3"
api_baseurl = f"https://api.themoviedb.org/{api_version}"

# Initialising instance of IMDbPy
ia = imdb.IMDb()

# HomePage
@app.route('/', methods=['GET', 'POST'])
def home_page():
    page = 1
    endpoint_path = f"/trending/movie/week"
    ssl._create_default_https_context = ssl._create_unverified_context
    search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}"
    req.urlopen(search_endpoint)
    md2 = []

    # To browse by genre
    genre_list = [
        {"Action": "28"}, {"Adventure": "12"}, {"Animation": "16"},
        {"Comedy": "35"}, {"Crime": "80"}, {"Drama": "18"},
        {"Fantasy": "14"}, {"Horror": "27"}, {"Mystery": "9648"},
        {"Romance": "10749"}, {
            "Science-Fiction": "878"}, {"Thriller": "53"}, {"War": "10752"}
    ]
    
    # For trending movies
    for i in range(1, 3):

        page = f"{i}"
        search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&sort_by=popularity.desc&include_adult=false&page={page}"
        conn = req.urlopen(search_endpoint)
        temp = json.loads(conn.read())

        for n in range(0, 20):
            t2 = {"title": f"{(temp['results'][n]['title'])}", "poster_path": f"{(temp['results'][n]['poster_path'])}","overview": f"{(temp['results'][n]['overview'])}",
                  "id": f"{(temp['results'][n]['id'])}"}
            md2.append(t2)

    return render_template('index.html', data=md2, gl=genre_list)

# Error Handler
@app.errorhandler(Exception)

# for HTTP exceptions
def http_error_handler(error):
    return render_template('error.html', error=error)

for error in (401, 404, 500, 422):
    app.error_handler_spec[None][error] = http_error_handler

# SearchPage
@app.route('/search', methods=['GET', 'POST'])
def search_function():

    # API request
    endpoint_path = f"/search/movie"
    ssl._create_default_https_context = ssl._create_unverified_context
    text = request.form['search']
    search_input = text.upper()
    final_inp = urllib.parse.quote_plus(search_input)
    search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&query={final_inp}&page=1"
    conn = req.urlopen(search_endpoint)
    md = json.loads(conn.read())

    # Processing data received from API
    md2 = []
    limit = md['total_results']
    max_page = md['total_pages']
    rem = limit % 20

    for i in (1, max_page):

        page = f"{i}"
        search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&query={final_inp}&page={page}&include_adult=false"
        conn = req.urlopen(search_endpoint)
        json_data = json.loads(conn.read())
        temp = json_data
        try:
            if rem > limit-(i*20):
                for n in range(rem):

                    t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                          "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": f"{(temp['results'][n]['release_date'][0:4])}"}
                    md2.append(t2)
            else:
                for n in range(0, 20):
                    t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                          "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": f"{(temp['results'][n]['release_date'][0:4])}"}
                    md2.append(t2)

        except:
            if rem > limit-(i*20):
                for n in range(rem):

                    t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                          "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": "NA"}
                    md2.append(t2)
            else:
                for n in range(0, 20):
                    t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                          "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": "NA"}
                    md2.append(t2)

    return render_template('searchresults.html', data=md2, inp=text)

# MoviePage
@app.route('/movie/<exp>', methods=['GET', 'POST'])
def movie_page(exp):
    # API Request

    movie_id = request.form['pass']
    endpoint_path = f"/movie/{movie_id}"
    endpoint_path2 = f"/movie/{movie_id}/credits"
    endpoint_path3 = f"/movie/{movie_id}/recommendations"
    endpoint_path4 = f"/movie/{movie_id}/videos"
    endpoint_path5 = f"/movie/{movie_id}/release_dates"
    ssl._create_default_https_context = ssl._create_unverified_context

    # for movie info
    search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}"
    # for movie cast
    search_endpoint2 = f"{api_baseurl}{endpoint_path2}?api_key={api_key}"
    # for recommendations
    search_endpoint3 = f"{api_baseurl}{endpoint_path3}?api_key={api_key}"
    # for trailers
    search_endpoint4 = f"{api_baseurl}{endpoint_path4}?api_key={api_key}"
    # for certification
    search_endpoint5 = f"{api_baseurl}{endpoint_path5}?api_key={api_key}"

    # Getting all datasets after requests
    conn = req.urlopen(search_endpoint)
    raw_info = json.loads(conn.read())
    conn = req.urlopen(search_endpoint2)
    cred = json.loads(conn.read())
    conn = req.urlopen(search_endpoint3)
    rec = json.loads(conn.read())
    conn = req.urlopen(search_endpoint4)
    vid = json.loads(conn.read())
    conn = req.urlopen(search_endpoint5)
    cert = json.loads(conn.read())

    # cast information
    cast = []
    cast_temp = []

    for n in range(len(cred['cast'])):
        t2 = {"name": f"{(cred['cast'][n]['name'])}", "picture": f"{(cred['cast'][n]['profile_path'])}",
              "char_name": f"{(cred['cast'][n]['character'])}", "id": f"{(cred['cast'][n]['id'])}"}
        cast_temp.append(t2)

    if len(cast_temp) > 5:
        del cast_temp[8:]
        cast = cast_temp
    else:
        cast = cast_temp

    # Pass a variable for routing
    exp = f"{raw_info['title']}"

    # dictionary of movie details
    imdb_id = f"{raw_info['imdb_id'][2:]}"
    rating = f"{ia.get_movie(imdb_id)['rating']}"

    # for movie genres
    genres = []
    for n in range(len(raw_info['genres'])):
        genres.append(raw_info['genres'][n]['name'])

    # for box office collection
    rev = raw_info['revenue']
    revenue = '${:,}'.format(rev)

    # for trailer links
    links = []
    yt = "https://www.youtube.com/watch?v="
    for vids in vid['results']:
        if vids["type"] == "Trailer" and vids["site"] == "YouTube":
            links.append(yt+vids["key"])
    del links[1:]

    # for movie certification
    certification = []
    for item in cert['results']:
        if item["iso_3166_1"] == "IN":
            certification.append(item["release_dates"][0]['certification'])

    # Dictionary of all movie information
    info = {
        "title": f"{raw_info['title']}",
        "poster": f"{raw_info['poster_path']}",
        "backdrop": f"{raw_info['backdrop_path']}",
        "genres": genres,
        "runtime": f"{raw_info['runtime']}",
        "revenue": revenue,
        "overview": f"{raw_info['overview']}",
        "rating": f"{rating}",
        "year": f"{raw_info['release_date'][0:4]}",
        "trailer": links,
        "certification": certification
    }

   # for director of the movie
    directors = []
    for credit in cred['crew']:
        if credit["job"] == "Director":
            dire = {"name": f"{(credit['name'])}", "id": f"{(credit['id'])}"}
            directors.append(dire)

    # for movie recommendations
    limit = rec['total_results']
    max_page = rec['total_pages']
    rem = limit % 20
    recommendation = []
    for i in (1, max_page+1):

        page = f"{i}"
        conn = req.urlopen(search_endpoint3)
        temp = json.loads(conn.read())

        if rem > limit-(i*20):
            for n in range(rem):
                t3 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}","year": f"{(temp['results'][n]['release_date'][0:4])}",
                      "poster_path": f"{(temp['results'][n]['poster_path'])}", "overview": f"{(temp['results'][n]['overview'])}", "id": f"{(temp['results'][n]['id'])}"}
                recommendation.append(t3)
        else:
            for n in range(0, 20):
                t3 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}","year": f"{(temp['results'][n]['release_date'][0:4])}",
                      "poster_path": f"{(temp['results'][n]['poster_path'])}", "overview": f"{(temp['results'][n]['overview'])}", "id": f"{(temp['results'][n]['id'])}"}
                recommendation.append(t3)

    # limiting number of recommendations to 12
    del recommendation[12:]

    # final dictionary to pass to html page
    final = {"det": info, "credits": cast,
             "rec": recommendation, "director": directors}
    return render_template('movie.html', data=final)

# TopRatedPage
@app.route('/top-rated', methods=['GET', 'POST'])
def top_page():

    # getting top 250 movies
    search = ia.get_top250_movies()

    info = []
    # data for the top 100 movies title
    for n in range(100):
        external_id = "tt"+(search[n].movieID)
        endpoint_path2 = f"/find/"
        search_endpoint2 = f"{api_baseurl}{endpoint_path2}{external_id}?api_key={api_key}&language=en-US&external_source=imdb_id"
        conn = req.urlopen(search_endpoint2)
        raw_info = json.loads(conn.read())
        temp = {"title": f"{(raw_info['movie_results'][0]['title'])}", "poster_path": f"{(raw_info['movie_results'][0]['poster_path'])}","overview": f"{(raw_info['movie_results'][0]['overview'])}",
                "id": f"{(raw_info['movie_results'][0]['id'])}", "year": f"{(raw_info['movie_results'][0]['release_date'][0:4])}", "rating": f"{search[n]['rating']}"}
        info.append(temp)

    return render_template('top.html', data=info)

#MoviesByGenre
@app.route('/genre/<genre_name>', methods=['GET', 'POST'])
def genre_page(genre_name):
    
    # Movies by genre
    genre_id = request.form['pass1']
    genre_name = request.form['pass2']
    endpoint_path = f"/discover/movie"
    search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&language=en-US&sort_by=vote_average.desc&include_adult=false&page=1&vote_count.gte=5000&with_genres={genre_id}"
    conn = req.urlopen(search_endpoint)
    md = json.loads(conn.read())
    limit = md['total_results']
    max_page = md['total_pages']
    rem = limit % 20
    md2 = []
    for i in range(1, max_page+1):

        page = f"{i}"
        search_endpoint2 = f"{api_baseurl}{endpoint_path}?api_key={api_key}&language=en-US&sort_by=vote_average.desc&include_adult=false&page={page}&vote_count.gte=5000&with_genres={genre_id}"
        conn = req.urlopen(search_endpoint2)
        json_data = json.loads(conn.read())
        temp = json_data
        if rem > limit-(i*20):
            for n in range(rem):

                t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                      "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": f"{(temp['results'][n]['release_date'][0:4])}"}
                md2.append(t2)
        else:
            for n in range(0, 20):
                t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                      "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": f"{(temp['results'][n]['release_date'][0:4])}"}
                md2.append(t2)

    # changing the request if number of responses is less than 100
    if len(md2) < 100:
        md2 = []
        search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&language=en-US&sort_by=vote_average.desc&include_adult=false&page=1&vote_count.gte=3000&with_genres={genre_id}"
        conn = req.urlopen(search_endpoint)
        md = json.loads(conn.read())
        limit = md['total_results']
        max_page = md['total_pages']
        rem = limit % 20

        for i in range(1, max_page+1):

            page = f"{i}"
            search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&language=en-US&sort_by=vote_average.desc&include_adult=false&page={page}&vote_count.gte=3000&with_genres={genre_id}"
            conn = req.urlopen(search_endpoint)
            json_data = json.loads(conn.read())
            temp = json_data
            if rem > limit-(i*20):
                for n in range(rem):

                    t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                          "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": f"{(temp['results'][n]['release_date'][0:4])}"}
                    md2.append(t2)
            else:
                for n in range(0, 20):
                    t2 = {"title": f"{(temp['results'][n]['title'])}","overview": f"{(temp['results'][n]['overview'])}",
                          "poster_path": f"{(temp['results'][n]['poster_path'])}", "id": f"{(temp['results'][n]['id'])}", "year": f"{(temp['results'][n]['release_date'][0:4])}"}
                    md2.append(t2)
    return render_template('genre.html', d=md2, gn=genre_name)

#PersonSearch
@app.route('/person', methods=['GET', 'POST'])
def psearch_page():
    
    #API request
    endpoint_path = f"/search/person"
    ssl._create_default_https_context = ssl._create_unverified_context
    text = request.form['people']
    search_input = text.upper()
    final_inp = urllib.parse.quote_plus(search_input)
    search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&query={final_inp}&page=1"
    conn = req.urlopen(search_endpoint)
    md = json.loads(conn.read())
    md2 = []
    limit = md['total_results']
    max_page = md['total_pages']
    rem = limit % 20

    #Processing data needed
    for i in range(1, max_page+1):

        page = f"{i}"
        search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&query={final_inp}&page={page}&include_adult=false"
        conn = req.urlopen(search_endpoint)
        json_data = json.loads(conn.read())
        temp = json_data

        if rem > limit-(i*20):
            for n in range(rem):
                t2 = {"name": f"{(temp['results'][n]['name'])}",
                      "image": f"{(temp['results'][n]['profile_path'])}", "job": f"{(temp['results'][n]['known_for_department'])}", "id": f"{(temp['results'][n]['id'])}"}
                md2.append(t2)
        else:
            for n in range(0, 20):
                t2 = {"name": f"{(temp['results'][n]['name'])}",
                      "image": f"{(temp['results'][n]['profile_path'])}", "job": f"{(temp['results'][n]['known_for_department'])}", "id": f"{(temp['results'][n]['id'])}"}
                md2.append(t2)

    # Final dictionary to pass to HTML Page
    final = []
    for people in md2:
        if (people["job"] == "Acting") or (people["job"] == "Directing") or (people["job"] == "Production"):
            final.append(people)

    return render_template('personsearch.html', data=final, inp=text)

#PersonDetails
@app.route('/person/<name>', methods=['GET', 'POST'])
def person_page(name):
    #API Request
    person_id = request.form['pass']
    endpoint_path = f"/person/{person_id}"
    search_endpoint = f"{api_baseurl}{endpoint_path}?api_key={api_key}&append_to_response=images,movie_credits"
    conn = req.urlopen(search_endpoint)
    md = json.loads(conn.read())
   
    #Variable to pass for routing
    name = f"{md['name']}"

    #Gallery of images
    gallery = []
    for n in range(len(md['images']['profiles'])):
        img_temp = {
            "image_path": f"{(md['images']['profiles'][n]['file_path'])}"}
        gallery.append(img_temp)
    
    #Movies the person is involved in
    
    recs = []
    if (md["known_for_department"] == "Acting"):
        for n in range(0, len(md['movie_credits']['cast'])):
            rec_temp = {"title": f"{(md['movie_credits']['cast'][n]['title'])}", "poster": f"{(md['movie_credits']['cast'][n]['poster_path'])}", "id": f"{(md['movie_credits']['cast'][n]['id'])}",
                        "overview": f"{(md['movie_credits']['cast'][n]['overview'])}", "pop": int(md['movie_credits']['cast'][n]['popularity']), "year": f"{(md['movie_credits']['cast'][n]['release_date'][0:4])}"}
            recs.append(rec_temp)

    elif(md["known_for_department"] == "Directing"):
        for n in range(0, len(md['movie_credits']['crew'])):
            rec_temp = {"title": f"{(md['movie_credits']['crew'][n]['title'])}", "poster": f"{(md['movie_credits']['crew'][n]['poster_path'])}", "id": f"{(md['movie_credits']['crew'][n]['id'])}",
                        "overview": f"{(md['movie_credits']['crew'][n]['overview'])}", "pop": int(md['movie_credits']['crew'][n]['popularity']), "year": f"{(md['movie_credits']['crew'][n]['release_date'][0:4])}"}
            recs.append(rec_temp)
    
    #Information about the person
    random_number=random.randint(0,len(md['images']['profiles']))
    info = {
        "name": f"{(md['name'])}",
        "birthday": f"{(md['birthday'])}",
        "id": f"{(md['id'])}",
        "bio": f"{(md['biography'])}",
        "images": gallery,
        "profile": f"{(md['images']['profiles'][random_number]['file_path'])}",
        "birthplace": f"{(md['place_of_birth'])}",
        "gallery_len":len(gallery)
    }
    
    #Sort movies by popularity and then limit them to 16
    cred = sorted(recs, key=lambda i: i['pop'], reverse=True)
    res_list = [i for n, i in enumerate(cred) if i not in cred[n + 1:]]
    if len(res_list)>16:
        del res_list[16:]
    
    return render_template('persondetails.html',data=info,gallery=gallery,rec=res_list)


if __name__ == "__main__":
    app.run(debug=True)
