from operator import itemgetter
from sudachipy import Dictionary, SplitMode
from .yomichan_parser import parse_freq_text, _parse_ftxt, _parse_ptxt
from .text_manipulation import clean_txt, remove_names, check_allowed_char, pretty_path
import srt
from collections import Counter


def _calc_score(vocs, reference):
    total = 0
    for v in vocs:
        if v in reference:
            try:
                _, ftxt, ptxt = parse_freq_text(reference[v])
                ftxt = _parse_ftxt(ftxt)
                ptxt = _parse_ptxt(ptxt)
                total += ftxt * ptxt
            except Exception as e:
                print(v)
                print(reference[v])
    return int(total)


def analyze_data(
    ptwpath=None,
    freqdict=None,
    token_db=None,
    vocab=None,
    known_words=None,
):
    if not ptwpath or not freqdict or not token_db:
        print("Nothing to do")
        return None
    tagger = Dictionary(dict="full").create(mode=SplitMode.A)
    folders = [p for p in list(ptwpath.glob("*/")) if p.is_dir()]
    tC = Counter()
    for vals in token_db.values():
        for v in vals.values():
            tC.update(v)
    freqdict = freqdict.copy()
    if known_words:
        for k in known_words:
            freqdict.pop(k, 0)
    for k in tC.keys():
        freqdict.pop(k, 0)
    if vocab:
        vocfreq = {v: freqdict.get(v, "W: 40K F: 1K %: 0.5") for v in vocab}
    else:
        vocfreq = dict()
    resdata = list()
    for fol in folders:
        folsrts = list(fol.rglob("*.srt"))
        sfdict = dict()
        for sf in folsrts:
            with open(sf, "r", encoding="utf-8-sig") as f:
                sfdict[sf] = f.read()
        vocset = set()
        for sf in folsrts:
            try:
                for s in list(srt.parse(sfdict[sf])):
                    text = clean_txt(remove_names(s.content))
                    toks = [w.normalized_form() for w in tagger.tokenize(text)]
                    toks = [w for w in toks if check_allowed_char(w)]
                    vocset.update(toks)
            except Exception as e:
                print(sf)
                raise e
        if _calc_score(list(vocset), freqdict) > 1:
            resdata.append(
                [
                    pretty_path(fol),
                    _calc_score(list(vocset), freqdict) // len(folsrts),
                    _calc_score(list(vocset), vocfreq) // len(folsrts),
                ]
            )
    # print(resdata)
    return sorted(resdata, key=itemgetter(1), reverse=True)
