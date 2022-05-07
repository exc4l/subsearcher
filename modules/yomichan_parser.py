# parse yomichan frequency dicts for further usage
import zipfile
import json
from pathlib import Path


def read_frequency_dict(fpath):
    with zipfile.ZipFile(fpath) as myzip:
        filenames = myzip.namelist()
        with myzip.open(filenames[1]) as f:
            dictstr = f.read().decode("utf-8")
    d = json.loads(dictstr)
    fqdict = {ele[0]: ele[2] for ele in d}
    return fqdict


def parse_freq_text(txt):
    wtxt = txt.split(":")[1][1:-2]
    ftxt = txt.split(":")[2][1:-2]
    ptxt = txt.split(":")[-1][1:]
    return wtxt, ftxt, ptxt


def suffix_numbers(number):
    if number > 1e6 - 1:
        return f"{int(number/1e6)}M"
    if number > 1e3 - 1:
        return f"{int(number/1e3)}K"
    return f"{number}"


def _parse_ftxt(ftxt):
    if ftxt[-1] in "KM":
        pre = int(ftxt[:-1])
        if ftxt[-1] == "M":
            fac = 1e6
        else:
            fac = 1e3
        return pre * fac
    return int(ftxt)


def _parse_ptxt(ptxt):
    return float(ptxt) / 100


# print(read_frequency_dict("PHCore.zip"))
# yomipath = Path(r"C:\Users\excal\python_projects\yomidict\dictionaries")
# with zipfile.ZipFile("PHCore.zip") as myzip:
#     filenames = myzip.namelist()
#     print(myzip.namelist())
#     with myzip.open(filenames[1]) as f:
#         dictstr = f.read().decode("utf-8")
# d = json.loads(dictstr)
# print(d)
# phcore = [ele[0] for ele in d]
# uniqw = set(phcore)
# all_kanji_set = set(chr(uni) for uni in range(ord("一"), ord("龯") + 1)) | set("〆々")


# def _clean(uctext):
#     return "".join(filter(all_kanji_set.__contains__, uctext))


# kanjistr = _clean("".join(uniqw))
# print("Unique Kanji in Vocab: ", len(set(kanjistr)))
