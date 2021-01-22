import User


class Table:
    def __init__(self, title, odds, upper, owner):
        self.title = title
        self.odds = int(odds)
        self.upper = int(int(1e9) if int(upper) == 0 else int(upper))
        self.owner = owner
        self.bets = []

    def bet(self, user, coin, target):
        if user.discriminator in [i["user"] for i in self.bets]:
            return "すでにベットは完了しています"
        user = User.get_user(user.discriminator)
        if coin > user['coin']:
            coin = user['coin']
        if coin > self.upper:
            coin = self.upper
        self.bets.append({"user": user["id"], "coin": coin, "target": target})
        user['coin'] -= coin
        return f"{coin}アスペスのベット、受け取りました"

    def settle(self, winners):
        res = ""
        winners = [winner.discriminator for winner in winners]
        cash = sum([i["coin"] for i in self.bets if i["user"] not in winners])
        for user in User.users:
            try:
                bet_price = [i['coin']
                             for i in self.bets if i['user'] == user["id"]][0]
            except IndexError:
                continue
            old_coin = user['coin']+bet_price
            if user["id"] in winners:
                user['coin'] += int((bet_price + cash //
                                     len(winners)) * self.odds)
            if user['coin'] == 0:
                res += f'{user["name"]}  '\
                    f'{old_coin} ---> {user["coin"]} ---> 100'+'\n'
                user["coin"] = 100
            else:
                res += f'{user["name"]}  '\
                    f'{old_coin} ---> {user["coin"]}' + '\n'
        if res == '':
            res = 'No bet'
        return res

    def stop(self):
        res = ''
        for bet in self.bets:
            user = User.get_user(bet['user'])
            res = f'{user["name"]}  {user["coin"]} ---> ' + \
                f'{user["coin"]+bet["coin"]}\n'
            user['coin'] += bet['coin']
        if res == '':
            res = 'No bet'
        else:
            res += '返金されました'
        return res
