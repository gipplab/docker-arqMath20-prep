from Wikidata.Wikidata import Wikidata

w = Wikidata()
for k, v in w.qid['formulae'].items():
    print(f'{k}:{v}')
    # uncomment to eventually delete
    #  w.delete_formula(k)
