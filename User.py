users = []


def get_user(id):
    return [user for user in users if user["id"] == id][0]


def reset():
    res = ''
    for user in users:
        user["coin"] = 1000
        res += (f'{user["name"]}  {user["coin"]}アスペス\n')
    return res


def set_up(members):
    for member in members:
        if member.bot:
            continue
        users.append({"id": member.discriminator,
                      "name": member.name, "coin": 1000})


def encrypt():
    base = ''
    for user in users:
        print(int(user['id']), int(user['coin']))
        base += chr(int(user['id']) // 100+12353) +\
            chr(int(user['id']) % 100 + 12353) +\
            chr(int(user['coin']//100+12353)) +\
            chr(int(user['coin']) % 100 + 12353)
    return base


def decipher(base):
    res = {}
    for i in range(0, len(base), 4):
        id = (ord(base[i])-12353) * 100 + ord(base[i + 1])-12353
        coin = (ord(base[i+2])-12353) * 100 + ord(base[i + 3])-12353
        res[id] = coin
    return res


def rollback(members, path=''):
    res = ''
    users = []
    if path != '':
        try:
            data = decipher(path)
            for member in members:
                if member.bot:
                    continue
                users.append({"id": member.discriminator,
                              "name": member.name,
                              "coin": data[int(member.discriminator)]})
                res += f'{member.name}  {data[int(member.discriminator)]}\n'
        except Exception:
            res = "無効な入力です"
    return res


if __name__ == "__main__":
    print(decipher(input()))
