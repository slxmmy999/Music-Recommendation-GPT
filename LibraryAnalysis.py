import requests
import sqlite3
import threading
from time import sleep

db_file = "lastfm_data.db"

# Connect to the SQLite database file

# Create a new table for a user's listening history data
def create_user_table(username, conn):
    table_name = "user_history_" + username
    create_table_query = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        artist TEXT,
        title TEXT,
        album TEXT,
        timestamp INTEGER
    );
    """.format(table_name=table_name)
    conn.execute(create_table_query)

def insert_user_data(username, data, conn):
    if len(data) > 100:
        create_user_table(username, conn)
        table_name = "user_history_" + username
        select_query = """
        SELECT COUNT(*) FROM {table_name};
        """.format(table_name=table_name)
        result = conn.execute(select_query).fetchone()
        if result[0] == 0:
            create_user_table(username, conn)
            insert_query = """
            INSERT INTO {table_name} (
                artist,
                title,
                album,
                timestamp
            ) VALUES (?, ?, ?, ?);
            """.format(table_name=table_name)
            conn.executemany(insert_query, data)
            conn.commit()
        else:
            return



api_key = "87935e55f2e097dfdffbaa7cd1ab0851"
usernames = [
                "ampmminimarket",
                "zachlavine",
                "catherineisa",
                "Jemma117",
                "zigojacko",
                "romidaponte",
                "TB8S",
                "godsmith2",
                "illcallyouback",
                "Fidelmo",
                "helluvaboss",
                "Blazer223",
                "bummyjen",
                "posthxclove",
                "WayneSkywaler",
                "StrngerNTheAlps",
                "vinicanal1",
                "Emo_dude_kel",
                "SixEvening464",
                "ArbiterFacts",
                "Wendiggoat",
                "t_better",
                "fvalt05",
                "TheFreeWheelinQ",
                "trentssb",
                "ladywhiskers94",
                "Arpit7",
                "jojokimbles",
                "anastasiawomack",
                "vsick1",
                "kuriouskiwii",
                "palkopupa",
                "zigojacko",
                "MorganPog",
                "Lkate9",
                "Tecktoyouth",
                "James-Ingram",
                "hlhyde",
                "DeMoBeats1234",
                "CitoyenHarrison",
                "fepeinado",
                "In_Solitude",
                "brownbiatch",
                "yuzherr",
                "BesiBesiBesi"
            ]

usernames = list(set(usernames))

def process_user(user):
    limit = 200  # maximum limit

    conn = sqlite3.connect(db_file)
    # set initial page to 1
    page = 1
    total_pages = 99999  # set a high initial value for the total number of pages

    user_data = []

    while page <= total_pages:
        url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={user}&api_key={api_key}&format=json&page={page}&limit={limit}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            tracks = data['recenttracks']['track']
            for track in tracks:
                artist = track['artist']['#text']
                title = track['name']
                album = track['album']['#text']
                timestamp = int(track['date']['uts'])
                user_data.append((artist, title, album, timestamp))
            
            # update the total number of pages
            total_pages = int(data['recenttracks']['@attr']['totalPages'])
            print(f"REQUESTED PAGE {page} OF {total_pages} FOR {user}")
            # increment the page number
            page += 1
        else:
            print("Error: Unable to retrieve user listening history.")
            break
        sleep(1)
    insert_user_data(user, user_data, conn)
    print(f"DATA RETRIEVED AND STORED FOR {user}")

threads = []
for user in usernames:
    thread = threading.Thread(target=process_user, args=(user,))
    threads.append(thread)
    thread.start()

# wait for all threads to complete
for thread in threads:
    thread.join()