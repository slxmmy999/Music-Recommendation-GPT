import requests
import sqlite3
from datetime import datetime

# Connect to the SQLite database file
db_file = "lastfm_data.db"
conn = sqlite3.connect(db_file)

# Function to calculate a numerical value that characterizes the user's music taste
def calculate_user_preference(username):
    # Get all the songs listened by the user
    table_name = "user_history_" + username
    select_query = """
    SELECT artist, title, album, timestamp
    FROM {table_name};
    """.format(table_name=table_name)
    cursor = conn.execute(select_query)
    songs = cursor.fetchall()
    
    # Get the play count for each song and store the data in a dictionary
    song_data = {}
    for song in songs:
        artist = song[0]
        title = song[1]
        album = song[2]
        timestamp = song[3]
        
        # Get the play count for the song using the Last.fm API
        api_key = "YOUR_LASTFM_API_KEY"
        url = "http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={title}&format=json".format(api_key=api_key, artist=artist, title=title)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            play_count = int(data['track']['userplaycount'])
            if play_count > 0:
                song_data[(artist, title, album)] = {
                    "play_count": play_count,
                    "timestamp": timestamp
                }
    
    # Normalize the data for each song
    genre_count = {}
    mood_count = {}
    total_play_count = 0
    total_timestamp_weight = 0
    current_timestamp = int(datetime.utcnow().strftime("%s"))
    for song, data in song_data.items():
        artist = song[0]
        title = song[1]
        album = song[2]
        play_count = data["play_count"]
        timestamp = data["timestamp"]
        
        # Get the genre for the song
        # You can use any API or dataset to get the genre information
        # For example, you can use the Last.fm API or the Spotify API
        genre = get_song_genre(artist, title)
        if genre:
            genre_count[genre] = genre_count.get(genre, 0) + play_count
        
        # Get the mood for the song
        # You can use any API or dataset to get the mood information
        # For example, you can use the Spotify API or the Echo Nest API
        mood = get_song_mood(artist, title)
        if mood:
            mood_count[mood] = mood_count.get(mood, 0) + play_count
        
        total_play_count += play_count
        
        # Calculate the timestamp weight for the song
        timestamp_diff = current_timestamp - timestamp
        timestamp_weight = 1 / (1 + (timestamp_diff / (3600 * 24))) # Use a decay function to give more weight to recent songs
        total_timestamp_weight += timestamp_weight
    
    # Calculate the user's overall music preference
    genre_preference = {}
    mood_preference = {}
    for genre, count in genre_count.items():
        genre_preference[genre] = count / total_play_count
    for mood, count in mood_count.items():
        mood_preference[mood] = count / total_play_count
    timestamp_preference = total_timestamp_weight / len(song_data)
    
    # Insert the user's music preference into the database
    insert_query = """
    INSERT INTO user_preference (
        username,
        genre_preference,
        playcount_preference,
        timestamp_preference,
        total_preference
    ) VALUES (?, ?, ?, ?, ?);
    """

    # Calculate the total user preference score
    total_preference = genre_preference_weight * genre_preference + playcount_preference_weight * playcount_preference + timestamp_preference_weight * timestamp_preference
    
    # Add the user preference score to the dictionary
    user_preference[username] = total_preference
    
    # Insert the user preference data into the new database
    conn.execute(insert_query, (username, genre_preference, playcount_preference, timestamp_preference, total_preference))
    conn.commit()

# Close the database connection
conn.close()

print("User preferences calculated and stored in the database.")