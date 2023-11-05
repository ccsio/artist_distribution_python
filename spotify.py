import requests
import base64
from pprint import pprint
import json
import os
import matplotlib.pyplot as plt

# with open("C:\\Users\\Luky\\Documents\\Python\\spotify\\data.json", "r") as f: 
#     data = f.read()
#     data = dict(json.loads(data))


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


def display_graph(data):
    tracks = data["tracks"]["items"]
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

    plt.title("Artist Distribution")
    plt.show()



with open(".//.env") as f:
    x = f.readlines()
    client_token = x[0].split('"')[1]
    secret_token = x[1].split('"')[1]

is_authorized, access_token, status_code = authorize(client_token,secret_token)


if is_authorized:
    pl_id = input("input the url of your playlist: ")
    pl_id = pl_id.split("/")[-1] 
    pl_url = f"https://api.spotify.com/v1/playlists/{pl_id}"

    success, data = get_playlist(access_token, pl_url)

    if success:
        data = dict(data.json())
        tracks = data["tracks"]["items"]

        new_url = data["tracks"]["next"]

        while new_url is not None:
            new_url = data["tracks"]["next"]
            print(new_url)
            success, new_data = get_playlist(access_token,new_url)
            pprint(new_data)

        display_graph(data)

    else:
        print(f'Failed to get playlist. Status code: {data}')


else:
    print(f'Failed to get access token. Status code: {status_code}')