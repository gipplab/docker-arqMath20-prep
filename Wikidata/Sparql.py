import asyncio
from typing import AsyncGenerator

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
    timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None, sock_read=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(sparql_url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise NotImplementedError('SPARQL error handling not implemented')
            return await resp.json()


async def get_qids_from_property(prop: int, value: str, limit: int = 0) -> AsyncGenerator[str, None]:
    q = 'prefix p: <https://arq20.formulasearchengine.com/prop/direct/> '
    limit_clause = ''
    if limit > 0:
        limit_clause = f' LIMIT {limit}'
    q += f'SELECT ?x where {{?x p:P{prop} "{value}"}}{limit_clause}'
    res = await query(q)
    try:
        for x in res['results']['bindings']:
            val: str = x['x']['value']
            yield val[prefix_length:]
    except KeyError:
        return


async def get_qid_from_property(prop: int, value: str):
    values = get_qids_from_property(prop, value, 1)
    async for v in values:
        return v
    return ''


async def print_qid(prop: int, value: str):
    v = await get_qid_from_property(prop, value)
    print(v)


async def print_qids(prop: int, value: str):
    strings = get_qids_from_property(prop, value)
    async for s in strings:
        print(s)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_qid(12, 'B.2'))
