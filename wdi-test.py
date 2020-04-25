from wikidataintegrator import wdi_core

mw_url = 'https://arq20.formulasearchengine.com/api.php'
sparql_url = 'https://sparql.arq20.formulasearchengine.com/bigdata/sparql'
wikibase_url = 'https://arq20.formulasearchengine.com'
my_first_wikidata_item = wdi_core.WDItemEngine(mediawiki_api_url=mw_url,
                                               sparql_endpoint_url=sparql_url,
                                               wikibase_url=wikibase_url,
                                               )

query = 'prefix p: <https://arq20.formulasearchengine.com/prop/direct/> SELECT ?x where {?x p:P12 \'B.2\'} LIMIT 10'
result = my_first_wikidata_item.execute_sparql_query(query, endpoint=sparql_url)

# to check successful installation and retrieval of the data, you can print the json representation of the item
# data = my_first_wikidata_item.get_wd_json_representation()
# print(data)
#
# entrez_gene_id = wdi_core.WDString(value='B.2', prop_nr='P12')
# # data goes into a list, because many data objects can be provided to
# data = [entrez_gene_id]
# # Search for and then edit/create new item
 wd_item = wdi_core.WDItemEngine(data=data, mediawiki_api_url='https://arq20.formulasearchengine.com/api.php')
# result = wd_item.write(login_instance)
print(result)
# wdi_core.WDItemEngine()
