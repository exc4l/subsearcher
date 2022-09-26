import json
import srt
from .text_manipulation import (
    clean_txt,
    remove_names,
    check_allowed_char,
)


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def load_token_db(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    for key in data.keys():
        for k, v in data[key].items():
            data[key][k] = set(v)
    return data


def make_token_db(srts, srtpath, tagger):
    if (srtpath / "token_db.json").is_file():
        token_db = load_token_db(srtpath / "token_db.json")
        cur_keys = token_db.keys()
    else:
        token_db = dict()
        cur_keys = ""
    if set([str(s.relative_to(srtpath).as_posix()) for s in srts]).issubset(cur_keys):
        return token_db
    sfdict = dict()
    for sf in srts:
        with open(sf, "r", encoding="utf-8") as f:
            sfdict[sf] = f.read()
    parsedict = dict()
    for sf in srts:
        if sf.relative_to(srtpath).as_posix() in cur_keys:
            continue
        tempdict = dict()
        for s in list(srt.parse(sfdict[sf])):
            text = clean_txt(remove_names(s.content))
            toks = [w.normalized_form() for w in tagger.tokenize(text)]
            toks = [w for w in toks if check_allowed_char(w)]
            tempdict[str(s.index)] = toks
        parsedict[str(sf.relative_to(srtpath).as_posix())] = tempdict

    token_db.update(parsedict)
    with open(srtpath / "token_db.json", "w", encoding="utf-8") as wr:
        # print(token_db)
        json.dump(token_db, wr, cls=SetEncoder)
    return token_db
