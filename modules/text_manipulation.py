import re
from pathlib import Path

HIRAGANA = set(
    "あえいおうかけきこくさしすせそたちつてとなにぬねのはひふへほ"
    "まみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづ"
    "でどばびぶべぼぱぴぷぺぽゃょゅっぁぃぉぅぇゎゝゐゑゔ"
)

KATAKANA = set(
    "アエイオウカケキコクサシスセソタチツテトナニヌネノハヒフヘホ"
    "マミムメモヤユヨラリルレロワヲウンガギグゲゴザジズゼゾダヂヅ"
    "デドバビブベボパピプペポょャュィョェァォッーゥヮヴヵヶﾘｫｶｯｮｼｵﾌｷﾏﾉﾀ"
)
NUMBERS = set("0123456789０１２３４５６７８９")
SENTENCEMARKER = set("。、!！？」「』『（）〝〟)(\n")
ALLKANJI = set(chr(uni) for uni in range(ord("一"), ord("龯") + 1)) | set("〆々")
ALLOWED = ALLKANJI | SENTENCEMARKER | KATAKANA | HIRAGANA | NUMBERS


def remove_names(text):
    return re.sub(r"\（(.*?)\）", "", text)


def clean_txt(text):
    text = "".join(filter(ALLOWED.__contains__, text))
    text = re.sub(r"\n+", "\n", text)
    return text


def check_allowed_char(w):
    if (
        w in HIRAGANA
        or w in KATAKANA
        or w in SENTENCEMARKER
        or w in NUMBERS
        or w.isnumeric()
    ):
        return False
    return True


def pretty_path(fpath):
    pattern = r"\[.*?\]"
    pattern2 = r"\(.*?\)"
    return (
        (re.sub(pattern2, "", re.sub(pattern, "", fpath.stem)))
        .replace(".jp", "")
        .replace("_", " ")
        .strip()
    )


def change_suffix_to_mkv(fpath):
    # while fpath.suffix in (".jp", ".srt"):
    #     fpath = fpath.with_suffix("")
    fpath = str(fpath).replace(".jp.srt", "").replace(".srt", "")
    fpath = Path(fpath + ".mkv")
    return fpath
