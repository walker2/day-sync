from exchangelib import Credentials, Account
from prettytable import PrettyTable
from telethon import TelegramClient

import datetime
import argparse



async def send_messages(client, messages, to):
    for message in messages:
        print(message[0])
        await client.send_message(to, message[0])


def main():
    parser = argparse.ArgumentParser(description='Print and send today\'s meetings to your Telegram!')
    parser.add_argument('-e', '--email', help='exchange email', required=True)
    parser.add_argument('-p', '--password', help='exchange password', required=True)
    parser.add_argument('--id', '--api_id', help='API ID from https://my.telegram.org/')
    parser.add_argument('--hash', '--api_hash', help='API Hash from https://my.telegram.org/')

    args = parser.parse_args()

    table = ['Subject','Starts','Ends', "Location"]

    tab = PrettyTable(table)

    credentials = Credentials(args.email, args.password)
    account = Account(args.email, credentials=credentials, autodiscover=True)

    t = datetime.date.today()
    start = datetime.datetime(t.year, t.month, t.day, 8, tzinfo=account.default_timezone)
    print(f'Showing meetings on {t.day}.{t.month}.{t.year}:\n')


    i = 0
    telegram_message = []
    for meeting in account.calendar.view(start=start, end=start + datetime.timedelta(hours=18)):
        i += 1

        s = meeting.start.astimezone(tz=account.default_timezone)
        e = meeting.end.astimezone(tz=account.default_timezone)
        minutes = lambda x: '00' if x == 0 else x

        tab.add_row([meeting.subject, f'{s.hour}:{minutes(s.minute)}', f'{e.hour}:{minutes(e.minute)}', meeting.location])

        telegram_message.append([f'{i}. "{meeting.subject}", starts: {s.hour}:{minutes(s.minute)}, ends: {e.hour}:{minutes(e.minute)}, location: {meeting.location}'])



    tab.add_autoindex()
    tab.align = "l"
    print(tab)

    print()

    if args.id is None:
        print("No Telegram API ID provided, skipping telegram send")
        return

    if args.hash is None:
        print("No Telegram API Hash provided, skipping telegram send")
        return

    print('Sending to telegram...')


    with TelegramClient('anon', args.id, args.hash) as client:
       client.loop.run_until_complete(send_messages(client, telegram_message, 'me'))

    print('All messages sent')

if __name__=="__main__":
    main()
