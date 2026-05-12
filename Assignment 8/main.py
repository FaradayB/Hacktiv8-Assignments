from fastapi import FastAPI
import requests

app = FastAPI()

data_contoh = {'nama': 'bobe', 'hobby': 'mancing', 'pekerjaan': 'nelayan'}

from fastapi import FastAPI, HTTPException

app = FastAPI(title="User data summary")

USERS_URL = 'https://jsonplaceholder.typicode.com/users'
POSTS_URL = 'https://jsonplaceholder.typicode.com/posts'

users_response = requests.get(USERS_URL)
posts_response = requests.get(POSTS_URL)

if users_response.status_code == 200 and posts_response.status_code == 200:
    users = users_response.json()
    posts = posts_response.json()

posts_per_user = {}
for post in posts:
    user_id = post["userId"]
    posts_per_user[user_id] = posts_per_user.get(user_id, 0) + 1

user_summary = []
for user in users:
    if  user["id"] in posts_per_user:
        user_summary.append({
            "id": user["id"],
            "nama": user["name"],
            "email": user["email"],
            "kota": user["address"]["city"],
            "jumlah_post": posts_per_user[user["id"]]
        })

user_summary = sorted(user_summary, key=lambda x: x['jumlah_post'])

@app.get("/users")
def get_users(kota:str=None):
    if kota:
        return [user for user in user_summary if user["kota"] == kota]
    return user_summary

@app.get("/users/{user_id}/posts")
def get_user_posts(user_id: int):
    user = next((us for us in users if us["id"] == user_id),None)

    if not user:
        raise HTTPException(
            status_code=404,
            detail='User tidak ditemukan'
        )
    user_post = [post["title"] for post in posts if post["id"] == user_id]
    return {
        "user_id" : user_id,
        "nama" : user["name"],
        "post": user_post
    } 