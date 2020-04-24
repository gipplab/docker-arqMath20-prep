import asyncio

import aiohttp

sparql_url = 'https://sparql.arq20.formulasearchengine.com/bigdata/sparql'
test_query = 'prefix p: <https://arq20.formulasearchengine.com/prop/direct/>' \
             'SELECT ?x where {?x p:P12 \'B.2\'} LIMIT 10'
prefix_length = len('https://arq20.formulasearchengine.com/entity/')


async def query(q=test_query):
    params = {
        'query': q,
        'format': 'json'
    }
    headers = {
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'moritz'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(sparql_url, params=params, headers=headers) as resp:
            print(resp.status)
            return await resp.json()


async def get_qids_from_property(property: int, value: str):
    q = 'prefix p: <https://arq20.formulasearchengine.com/prop/direct/> '
    q += f'SELECT ?x where {{?x p:P{property} "{value}"}} LIMIT 10'
    res = await query(q)
    try:
        for x in res['results']['bindings']:
            yield (x['x']['value'][prefix_length:])
    except KeyError:
        pass


async def print_qids(property: int, value: str):
    strings = get_qids_from_property(property, value)
    async for s in strings:
        print(s)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_qids(15, 'B.2'))
