import discord
from discord.ext import tasks
import Ganble
import User
from Setting import token
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tables = list()
tmp_vars = {}
state = ""


@tasks.loop(seconds=1800)
async def loop():
    print(User.encrypt())


@client.event
async def on_ready():
    User.set_up(client.guilds[0].members)


@client.event
async def on_message(message):
    global state
    if message.author.bot:
        return
    contents = message.content.split()
    author = message.author

    if '$start' in contents and state == "":
        tmp_vars["channel"] = message.channel
        state = "setting"
        tmp_vars["count"] = 0
        tmp_vars['author'] = author
        await message.channel.send("テーマは?")

    elif state == "setting" and message.channel == tmp_vars["channel"]:
        if author != tmp_vars["author"]:
            await message.channel.send("権限がありません")
            return
        if tmp_vars["count"] == 0:
            tmp_vars["title"] = message.content
            tmp_vars['count'] = 1
            await message.channel.send("倍率は?")

        elif tmp_vars["count"] == 1:
            try:
                tmp_vars["odds"] = float(contents[0])
                tmp_vars["count"] = 2
                await message.channel.send("上限は?")
            except ValueError:
                await message.channel.send("無効な値です\nもう一度入力して下さい")

        elif tmp_vars["count"] == 2:
            try:
                tmp_vars["upper"] = int(contents[0])
                tables.append(Ganble.Table(
                    tmp_vars["title"], tmp_vars["odds"], tmp_vars["upper"],
                    author.discriminator))
                state = ""
                await message.channel.send(f"テーマ:{tmp_vars['title']}\n"
                                           f"倍率:{tmp_vars['odds']}\n"
                                           f"上限: {'なし' if tmp_vars['upper'] == 0 else tmp_vars['upper']}")
            except ValueError:
                await message.channel.send("無効な値です\nもう一度入力してください")

    elif "$bet" in contents:
        if len(contents) < 4:
            await message.channel.send("無効な入力です")
            return
        try:
            number = int(contents[1])
            bet_price = int(contents[2])
            bet_target = contents[3]
        except ValueError:
            await message.channel.send("無効な入力です")
            return
        if not len(tables) > number:
            await message.channel.send("無効な入力です")
            return
        await message.channel.send(tables[number].bet(author, bet_price,
                                                      bet_target))

    elif "$betlist" in contents:
        try:
            res = ''
            number = int(contents[1])
            for bet in tables[number].bets:
                res += (f'{User.get_user(bet["user"])["name"]}  '
                        f'{bet["target"]}  '
                        f'{bet["coin"]}\n')
            if res == '':
                res = 'no bet'
            await message.channel.send(res)
        except (ValueError, IndexError):
            await message.channel.send("無効な入力です")

    elif "$end" in contents and state == '':
        if len(contents) < 2:
            return
        number = int(contents[1])
        if number >= len(tables):
            return
        if tables[number].owner != message.author.discriminator:
            await message.channel.send("権限がありません")
            return
        state = "settle"
        tmp_vars['number'] = number
        tmp_vars["owner"] = tables[number].owner
        await message.channel.send("勝者を入力してください(メンション、複数可)")

    elif state == 'settle' and \
            message.author.discriminator == tmp_vars['owner']:
        winners = message.mentions
        if winners == []:
            await message.channel.send("勝者を入力してください(メンション、複数可)")
            return
        await message.channel.send(tables[tmp_vars['number']].settle(winners))
        state = ""
        del tables[tmp_vars['number']]

    elif '$tables' in contents:
        res = ''
        for i, table in enumerate(tables):
            res += str(i) + "    " + \
                (f'{table.title}   倍率:{table.odds}   '
                 f'上限: {"free" if table.upper == int(1e9) else table.upper}\n')
        if res == '':
            res = 'No table'
        await message.channel.send(res)

    elif '$list' in contents:
        res = ''
        for user in User.users:
            res += f'{user["name"]} : {user["coin"]}アスペス\n'
        await message.channel.send(res)

    elif '$reset' in contents:
        if 'admin' not in [i.name for i in author.roles]:
            await message.channel.send('権限がありません')
            return
        await message.channel.send(User.reset())

    elif '$give' in contents:
        if len(contents) < 3 or message.mentions == []:
            return
        try:
            price = int(contents[2])
            user = User.get_user(author.discriminator)
            given_user = User.get_user(message.mentions[0].discriminator)
            if user == given_user:
                await message.channel.send("無効な入力です")
                return
            if price > user['coin']-100:
                price = user['coin'] - 100
            res = (f'{user["name"]}  {user["coin"]} ---> {user["coin"]-price}'
                   f'\n{given_user["name"]}  {user["coin"]} ---> '
                   f'{given_user["coin"]+price}')
            given_user["coin"] += price
            user['coin'] -= price
            await message.channel.send(res)
        except ValueError:
            await message.channel.send("無効な入力です")

    elif '$stop' in contents:
        if len(contents) < 2:
            return
        if 'admin' not in [i.name for i in author.roles]:
            await message.channel.send('権限がありません')
            return
        try:
            number = int(contents[1])
            await message.channel.send(tables[number].stop())
            del tables[number]
        except (ValueError, IndexError):
            await message.channel.send('無効な入力です')

    elif '$help' in contents:
        with open('help.txt') as f:
            res = f.read()
        await message.channel.send(res)

    elif '$rollback' in contents and state == '':
        state = 'rollback'
        await message.channel.send('pathを入力してください')

    elif state == 'rollback':
        path = contents[0]
        state = ''
        await message.channel.send(
            User.rollback(client.guilds[0].members, path))

    elif '$path' in contents:
        await message.channel.send(User.encrypt())

if __name__ == "__main__":
    loop.start()
    client.run(token)
