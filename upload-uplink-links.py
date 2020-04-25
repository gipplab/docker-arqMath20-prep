import asyncio
import csv

from Wikidata.Wikidata import Wikidata

tasks = []

with open('/data/uplink.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        id = row['id']
        post = row['mo']
        wd = Wikidata()
        tasks.append((wd.insert_uplink(f'A.{id}', post)))
        tasks.append((wd.insert_uplink(f'B.{id}', post)))
        print(f'importing {id} with post {post}')


async def update():
    for t in tasks:
        print(await t)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update())
