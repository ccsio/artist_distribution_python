import requests
import base64
from pprint import pprint
import json
import matplotlib.pyplot as plt
from math import ceil


def authorize(client_token,secret_token):
    auth_url = "https://accounts.spotify.com/api/token"

    credentials = f"{client_token}:{secret_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }
    body = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, data=body, headers=headers)

    if response.status_code == 200:
        success = True
        access_token = response.json()['access_token']
    else:
        success = False
        access_token = None
        response = response.status_code

    return (success, access_token, response)


def get_playlist(access_token,url):
    headers = {
        'Authorization': f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [True, response]
    else:
        print(f'Failed to get access playlist. Status code: {response.status_code}')
        return [False, response.status_code]


def display_graph(tracks,name="Artist Disribution",owner="unknown",desc=""):
    total_tracks = len(tracks)
    artists = {}
    for i in tracks:
        z = i["track"]["album"]["artists"]
        for j in z:
            if j["name"] not in artists:
                artists[j["name"]] = 1
            else:
                artists[j["name"]] += 1

    sorted_artists = sorted(artists.items(), key=lambda x:x[1], reverse=True) 
    # pprint(sorted_artists)

    print(f"Tracks: {total_tracks}")
    for i in sorted_artists:
        print(f"{i[0]}: {i[1]} => {round(i[1]/total_tracks*100, 2)}%")


    explode = tuple(len(artists) * [0.05])

    plt.pie(artists.values(), labels=artists.keys(), autopct='%1.1f%%', pctdistance=0.85, explode=explode)
    my_circle = plt.Circle( (0,0), 0.7, color='white')
    p = plt.gcf()
    p.gca().add_artist(my_circle)


    plt.suptitle(name,fontsize=24)
    plt.title(f"By {owner}", fontsize=14,va="top")
    plt.show()



with open(".//.env") as f:
    x = f.readlines()
    client_token = x[0]
    secret_token = x[1]

is_authorized, access_token, status_code = authorize(client_token,secret_token)


if is_authorized:
    pl_id = input("Input the url of your playlist: ")
    pl_id = pl_id.split("/")[-1] 
    pl_url = f"https://api.spotify.com/v1/playlists/{pl_id}"
    
    tracks = []

    success, data = get_playlist(access_token,pl_url)
    if success:
        data = dict(data.json())
        track_total = data["tracks"]["total"]
        
        pl_name = data["name"]
        owner = data["owner"]["display_name"]
        description = data["description"]
        
        tracks.extend(data["tracks"]["items"])

        if track_total - 101 > 0:
            z = ceil((track_total-101) / 100)
            pl_url = data["tracks"]["next"]
            for i in range(z):
                success, data = get_playlist(access_token,pl_url)
                if success:
                    data = dict(data.json())
                    tracks.extend(data["items"])
                    pl_url = data["next"]

    display_graph(tracks,pl_name,owner)


else:
    print(f'Failed to get access token. Status code: {status_code}')