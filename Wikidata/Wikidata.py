import logging
from os import getenv
from signal import *
from typing import Optional

import pywikibot
import pywikibot.flow
from pywikibot import Claim
from pywikibot.site import APISite

from main import pkl_read, pkl_write


class Wikidata:
    logger = None
    data_repo = None
    site = None
    qid = {
        'users': {},
        'posts': {},
        'formulae': {},
        'tags': {},
    }

    def delete_formula(self, fid):
        q = self.get_formula(fid)
        item = pywikibot.ItemPage(self.get_data_repo(), q)
        item.delete('created by accident', prompt=False)

    def get_formula(self, fid) -> Optional[str]:
        return self.qid['formulae'].get(fid)

    def add_formula(self, fid, formula="") -> str:

        if self.get_formula(fid):
            f_item = pywikibot.ItemPage(self.get_data_repo(), self.get_formula(fid))
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
            if f_item.claims and 'P1' in f_item.claims:
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
