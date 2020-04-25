import logging
from os import getenv
from signal import *
from typing import Optional

import pywikibot
import pywikibot.flow
from pywikibot import Claim
from pywikibot.site import APISite
from wikidataintegrator import wdi_core, wdi_login

from Wikidata.Sparql import get_qid_from_property
from main import pkl_read, pkl_write


def q_from_csv():
    """
    Reinsert formula IDs to cache.
    :return:
    """
    import csv
    with open('/data/qformulae.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        wd = Wikidata()
        for row in reader:
            wd.qid['formulae'][row['y']] = row['item']
        wd.save_qid()


class Wikidata:
    MW_URL = 'https://arq20.formulasearchengine.com/api.php'
    SPARQL_URL = 'https://sparql.arq20.formulasearchengine.com/bigdata/sparql'
    WIKIBASE_URL = 'https://arq20.formulasearchengine.com'
    PROP_TOPIC = 'P12'
    PROP_CATEGORY = 'P10'
    PROP_FID = 'P8'
    PROP_POST_TYPE = 'P9'
    PROP_POST_ID = 'P5'
    fastmode = True

    logger = None
    data_repo = None
    site = None
    login = None
    qid = {
        'users': {},
        'posts': {},
        'formulae': {},
        'tags': {},
    }

    def get_login(self):
        if not self.login:
            self.login = wdi_login.WDLogin(user='SchuBot', pwd=getenv('WIKI_PASS'),
                                           mediawiki_api_url=self.MW_URL)
        return self.login

    async def insert_uplink(self, topic_id, uplink):
        cur_id = await get_qid_from_property(12, topic_id)
        data = [wdi_core.WDExternalID(value=uplink, prop_nr=self.PROP_POST_ID)]
        wd_item = wdi_core.WDItemEngine(wd_item_id=cur_id, data=data, mediawiki_api_url=self.MW_URL)
        return wd_item.write(self.get_login())

    async def add_topic(self, topic_id: str, categories: [str], fid=None) -> str:
        data = [wdi_core.WDExternalID(value=topic_id, prop_nr=self.PROP_TOPIC),
                wdi_core.WDItemID('Q887', prop_nr=self.PROP_POST_TYPE)]
        for c in categories:
            data.append(wdi_core.WDExternalID(value=c, prop_nr=self.PROP_CATEGORY))
        if fid:
            data.append(wdi_core.WDExternalID(value=fid, prop_nr=self.PROP_FID))
        cur_id = await get_qid_from_property(12, topic_id)
        wd_item = wdi_core.WDItemEngine(wd_item_id=cur_id, data=data, mediawiki_api_url=self.MW_URL)
        return wd_item.write(self.get_login())

    def delete_formula(self, fid):
        q = self.get_formula(fid)
        item = pywikibot.ItemPage(self.get_data_repo(), q)
        item.delete('created by accident', prompt=False)

    def get_formula(self, fid) -> Optional[str]:
        return self.qid['formulae'].get(fid)

    def add_formula(self, fid, formula="") -> str:

        if self.get_formula(fid):
            f_item = pywikibot.ItemPage(self.get_data_repo(), self.get_formula(fid))
            if self.fastmode:
                return self.get_formula(fid)
        else:
            f_item = pywikibot.ItemPage(self.get_data_repo())
            f_item.editLabels(labels={"en": f"Formula {fid}"})
            p8 = pywikibot.Claim(self.get_data_repo(), u'P8')
            p8.setTarget(fid)
            f_item.addClaim(p8)
            new_id = f_item.getID()
            self.qid['formulae'][fid] = new_id
            # TODO: remove immediately save option after debugging is complete
            pkl_write('/data/qid.pickle', self.qid)
        if formula:
            self.logger.debug(f'Item {f_item.getID()} for formula {fid}.')
            f_item.get()  # initialize claims field
            if 'P1' in f_item.claims:
                claim: Claim = f_item.claims['P1'][0]
                if claim.target != formula:
                    claim.changeTarget(formula)
            else:
                p1 = pywikibot.Claim(self.get_data_repo(), u'P1')
                p1.setTarget(formula)
                f_item.addClaim(p1)
        return self.get_formula(fid)

    def get_data_repo(self) -> APISite:
        if not self.data_repo:
            self.site = self.get_site()
            self.data_repo = self.site.data_repository()
        return self.data_repo

    def get_site(self):
        if not self.site:
            self.site = pywikibot.Site('fse', 'fse')  # The site we want to run our bot on
            if getenv('WIKI_PASS'):
                self.patch_wiki()
            self.site.login()
        return self.site

    # TODO: https://www.mediawiki.org/wiki/Manual:Pywikibot/OAuth
    @staticmethod
    def patch_wiki():
        def new_input(question, password=False, default='', force=False):
            if password:
                return getenv('WIKI_PASS')
            return original(question, password, default, force)

        original = pywikibot.input
        pywikibot.input = new_input

    def load_qid(self):
        self.qid = pkl_read('/data/qid.pickle', lambda: self.qid)

    def save_qid(self):
        pkl_write('/data/qid.pickle', self.qid)

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.ERROR)
        self.logger.setLevel(level=logging.DEBUG)
        for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
            signal(sig, self.save_qid)
        self.load_qid()


if __name__ == "__main__":
    q_from_csv()
