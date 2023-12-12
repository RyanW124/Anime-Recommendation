from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from typing import Self
from tqdm import tqdm
import pickle
import pandas as pd
import numpy as np
import random
from multiprocessing import Pool
from fake_useragent import UserAgent
from time import perf_counter, sleep
from sklearn.model_selection import train_test_split


with open("tokens.txt", "r") as f:
    token = f.readline().strip()
header = {"Authorization": f"Bearer {token}"}

class Anime:
    id_to_anime = {}

    def __init__(self, name: str, _id):
        self.name = name
        self.url = f"https://myanimelist.net/anime/{_id}/{name.replace(' ', '_')}"
        self.id = _id

    @classmethod
    def get_anime_from_name(cls, name, _id):
        if _id in cls.id_to_anime:
            return cls.id_to_anime[_id]
        anime = cls(name, _id)
        cls.id_to_anime[_id] = anime
        return anime


    def __str__(self):
        return f"Name: {self.name}\nLink: {self.url}\n"

    def get_recommendation(self):
        users = []
        review_page = requests.get(self.url + "/reviews")
        review_soup = BeautifulSoup(review_page.content, "html.parser")
        users_soup = review_soup.findAll("div", {"class": "username"})
        for div in users_soup:
            a = div.find("a")
            user = a.getText()
            user = User(user, False)
            users.append(user)
        return users


class Score:
    def __init__(self, anime, score):
        self.anime = anime
        # self.user = user
        self.score = score
    def __str__(self):
        return str(self.anime)+"\nScore: {self.score}\n"
class User:
    def __init__(self, username: str, load_animes=True):
        self.username = username
        self.animelist = None
        self.scores = {}
        if load_animes:
            self.load_animelist()
    def __str__(self):
        return f"User: {self.username}"
    @property
    def profile_url(self):
        return f"https://myanimelist.net/profile/{self.username}"
    def shared_with(self, other: Self):
        count = 0
        self_set = set(i.anime.id for i in self.get_animelist())
        for i in other.get_animelist():
            if i.anime.id in self_set:
                count += 1
        return count

    @property
    def animelist_url(self):
        return f"https://myanimelist.net/animelist/{self.username}?status=7&order=4&order2=0"
    def load_animelist(self):
        self.animelist = self.get_animelist()
    def get_animelist(self):
        if self.animelist is not None:
            return self.animelist
        self.animelist = []
        response = requests.get(f"https://api.myanimelist.net/v2/users/{self.username}/animelist?fields=list_status&sort=list_score&limit=1000", headers=header)
        # print(response.json())
        if response.status_code != 200:
            return []
        for anime in response.json()["data"]:
            node, list_status = anime["node"], anime["list_status"]
            anime = Anime.get_anime_from_name(node["title"], node["id"])
            self.animelist.append(Score(anime, list_status["score"]))
        for i in self.animelist:
            self.scores[i.anime.id] = i.score
        return self.animelist

def main():
    user = User("Chuuya_727")
    print(user.get_animelist()[0].anime.get_recommendation())

if __name__ == '__main__':
    main()
