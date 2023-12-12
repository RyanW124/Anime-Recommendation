from Util import *
import MF
def main():
    main_user = User(input("Enter your MAL username: "))
    usernames = {main_user.username}
    users = [main_user]
    main_user.load_animelist()
    temp_users = []
    threshold = min(30, len(main_user.get_animelist())//5)
    if len(main_user.get_animelist()) == 0:
        print("Error loading MAL")
        return
    s = 0
    for score in tqdm(random.sample(main_user.get_animelist(), threshold), desc="Going through user anime list"):
        recs = score.anime.get_recommendation()
        for user in recs:
            if user.username in usernames:
                continue
            usernames.add(user.username)
            temp_users.append(user)
    for user in tqdm(temp_users, desc="Looking through users with similar preferences"):
        if user.get_animelist(): s += 1
        if main_user.shared_with(user) >= threshold:
            users.append(user)
        sleep(.5)
    users.append(Anime.id_to_anime)
    users, Anime.id_to_anime = users[:-1], users[-1]
    animes = set()
    for user in users:
        for score in user.get_animelist():
            animes.add(score.anime.id)
    table = []
    animes = list(animes)
    for anime in animes:
        row = []
        for user in users:
            row.append(user.scores[anime] if anime in user.scores else 0)
        table.append(row)

    arr = np.array(table)
    mf = MF.MF(arr, 20, 0.005, 0.001)
    mf.train()
    recommendations = []
    for i, v in enumerate(mf.full_matrix()[:, 0]):
        if v >= 8 and animes[i] not in users[0].scores:
            recommendations.append((Anime.id_to_anime[animes[i]], v))
    recommendations.sort(key=lambda x: x[1], reverse=True)
    for i, v in recommendations:
        print(i, v)


if __name__ == "__main__":
    main()