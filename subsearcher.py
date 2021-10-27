import argparse
import operator
import random
import re
import string
import subprocess
from configparser import ConfigParser
from datetime import datetime, timedelta
from pathlib import Path

import pyperclip
import PySimpleGUI as sg
import srt

try:
    import fugashi
    TOKENIZER = True
except ImportError as e:
    TOKENIZER = False


CONFNAME = "config.ini"
ICON = b"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"
sg.theme("Reddit")

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
SENTENCEMARKER = set("。、!！？」「』『（）〝〟)(\n")
ALLKANJI = set(
    chr(uni) for uni in range(ord("一"), ord("龯") + 1)
) | set("〆々")
ALLOWED = (
    ALLKANJI | SENTENCEMARKER | KATAKANA | HIRAGANA
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--srtpath",
        type=Path,
        help="path to the srt and corresponding media files. Required",
    )
    parser.add_argument("--knownpath", type=Path, help="path to known words file.")
    parser.add_argument("--vocabpath", type=Path, help="path to desired vocab file.")
    parser.add_argument(
        "--playerpath", type=Path, help="path to player application. Required"
    )
    parser.add_argument(
        "--ignorepath", type=Path, help="path to words which will be ignored."
    )
    args = parser.parse_args()
    return args


def handle_not_given(conf, seckey, key, argument):
    if argument is not None:
        if argument.is_file():
            pdict = {key: argument}
        else:
            pdict = {key: ""}
    elif conf[seckey].get(key) is None:
        pdict = {key: ""}
    else:
        pdict = dict()
    return pdict


def handle_config(inputs):
    confpath = Path(CONFNAME)
    config = ConfigParser()
    pathdict = dict()
    if confpath.is_file():
        config.read(confpath)
    if not config.has_section("Paths"):
        config["Paths"] = dict()
    if inputs.srtpath is not None:
        pathdict.update({"SrtPath": inputs.srtpath})
    pathdict.update(handle_not_given(config, "Paths", "VocabPath", inputs.vocabpath))
    pathdict.update(handle_not_given(config, "Paths", "KnownPath", inputs.knownpath))
    pathdict.update(handle_not_given(config, "Paths", "IgnorePath", inputs.ignorepath))
    if inputs.playerpath is not None:
        pathdict.update({"PlayerPath": inputs.playerpath})
    for k, v in pathdict.items():
        config["Paths"][k] = str(v)
    with open(confpath, "w") as configfile:
        config.write(configfile)
    return config


def read_vocabs(vocpath):
    if vocpath.is_file():
        with open(vocpath, "r", encoding="utf-8") as f:
            vocabs = f.read().split()
    else:
        vocabs = [""]
    return vocabs


def parse_subtitles(srtpath):
    srts = list(srtpath.rglob("*.srt"))
    sfdict = dict()
    for sf in srts:
        with open(sf, "r", encoding="utf-8") as f:
            sfdict[sf] = f.read()
    parsedict = {sf: list(srt.parse(sfdict[sf])) for sf in srts}
    return srts, sfdict, parsedict


def pretty_path(fpath):
    pattern = r"\[.*?\]"
    pattern2 = r"\(.*?\)"
    return (
        (re.sub(pattern2, "", re.sub(pattern, "", fpath.stem)))
        .replace(".jp", "")
        .replace("_", " ")
        .strip()
    )

def remove_names(text):
    return re.sub(r"\（(.*?)\）", "", text)

def clean_txt(text):
    text = "".join(filter(ALLOWED.__contains__, text))
    text = re.sub(r"\n+", "\n", text)
    return text

def search_word(word, srts, sfdict, parsedict, winhandle=None, tok_mode="Exact Match", tagger=None):
    tabdata = list()
    fac = 51/len(srts)
    prog=0
    for sf in srts:
        if word in sfdict[sf]:
            res = list()
            for s in parsedict[sf]:
                if word in s.content and "♬" != s.content[0]:
                    res.append(s)
            if len(res) > 0:
                for r in res:
                    tabdata.append([word, sf, r.start])
        if tok_mode=="Exact + Tokenizer":
            tres = list()
            for s in parsedict[sf]:
                text = clean_txt(remove_names(s.content))
                for sen in text.split("\n"):
                    sen_tokens = [
                        w.feature.lemma.split("-")[0] if w.feature.lemma else w.surface
                        for w in tagger(sen)
                    ]
                    sen_tokens = [
                        w
                        for w in sen_tokens
                        if not (
                            w in HIRAGANA
                            or w in KATAKANA
                            or w in SENTENCEMARKER
                        )
                    ]
                    if word in sen_tokens:
                        tres.append(s)
            if len(tres) > 0:
                for r in tres:
                    if r not in res:
                        tabdata.append([word, sf, r.start])
        prog+=1
        if winhandle and prog % 5:
            winhandle["-PROG-"].update('█'*int(prog*fac))
            winhandle.refresh()
    prettydata = [[i[0], pretty_path(i[1]), i[2], i[1]] for i in tabdata]
    return prettydata


def change_suffixex_to_mkv(fpath):
    # while fpath.suffix in (".jp", ".srt"):
    #     fpath = fpath.with_suffix("")
    fpath = str(fpath).replace(".jp.srt", "").replace(".srt", "")
    fpath = Path(fpath + ".mkv")
    return fpath


def get_layout(data, headings):
    if TOKENIZER:
        options = ['Exact Match','Exact + Tokenizer']
    else:
        options = ['Exact Match']
    layout = [
        [
            sg.Text(" " * 50),
            sg.Text("Word Search:", size=(10, 1)),
            sg.Input("", k="-Search-", size=(15, 1)),
            sg.Button("Search", bind_return_key=True),
        ],
        [
            sg.Text(" " * 50),
            sg.Text("Search Mode:", size=(10, 1)),
            sg.Combo(options,default_value='Exact Match',key='-TOKENIZER-', readonly=True, auto_size_text=True),
        ],
        [
            sg.Table(
                values=data,
                headings=headings,
                auto_size_columns=False,
                col_widths=[10, 25, 20],
                display_row_numbers=True,
                justification="center",
                num_rows=30,
                # size=(30, 60),
                alternating_row_color="lightgrey",
                key="-TABLE-",
                # selected_row_colors='red on yellow',
                enable_events=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
            )
        ],  # Comment out to not enable header and other clicks
        [sg.Text('', size=(50, 1), relief='sunken', font=('Courier', 2),
                   text_color='blue', background_color='white',key='-PROG-', metadata=0),sg.Sizegrip()],
        # [sg.ProgressBar(1, orientation='h', size=(20, 2), key='progress')],
    ]
    return layout


def sort_table(table, cols):
    """sort a table by multiple columns
    table: a list of lists (or tuple of tuples) where each inner list
           represents a row
    cols:  a list (or tuple) specifying the column numbers to sort by
           e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        try:
            table = sorted(table, key=operator.itemgetter(col))
        except Exception as e:
            sg.popup_error("Error in sort_table", "Exception in sort_table", e)
    return table


def main():
    if TOKENIZER:
        try:
            tagger = fugashi.Tagger()
        except:
            raise ImportError("Please execute 'python -m unidic download' inside your venv. Fugashi doesn't find the dictionary file")
        if tagger.dictionary_info[0]["size"] < 872000:
            raise ImportError("Please execute 'python -m unidic download' inside your venv. Fugashi seems to use the small dictionary")
    else:
        tagger = None
    inputs = parse_args()
    config = handle_config(inputs)
    srtpath = Path(config["Paths"]["SrtPath"])
    vocpath = Path(config["Paths"]["VocabPath"])
    playerpath = Path(config["Paths"]["PlayerPath"])
    knownpath = Path(config["Paths"]["KnownPath"])
    ignopath = Path(config["Paths"]["IgnorePath"])
    vocabs = read_vocabs(vocpath)
    known = set(read_vocabs(knownpath))
    igno = set(read_vocabs(ignopath))
    search_list = [word for word in vocabs if word not in known and word not in igno]
    srts, sfdict, parsedict = parse_subtitles(srtpath)

    data = list()
    for word in search_list:
        data.extend(search_word(word, srts, sfdict, parsedict))
    headings = ["Word", "Anime", "Word Occurence"]
    layout = get_layout(data, headings)

    window = sg.Window(
        "Sub Searcher", layout, ttk_theme="vista", resizable=True, icon=ICON
    )
    while True:
        event, values = window.read()
        # print(event, values)
        if event == sg.WIN_CLOSED:
            break
        if event == "Search":
            # print(values)
            # prog+=1
            # window["-PROG-"].update('█'*prog)
            if values.get("-Search-") != "":
                data = search_word(values.get("-Search-"), srts, sfdict, parsedict, tok_mode=values.get("-TOKENIZER-"), tagger=tagger, winhandle=window)
                # print(data)
                window["-TABLE-"].update(data)
        if isinstance(event, tuple):
            # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
            # print(event)
            if event[0] == "-TABLE-":
                if event[2][0] is None or event[2][1] == -1:
                    continue
                if (
                    event[2][0] == -1 and event[2][1] != -1
                ):  # Header was clicked and wasn't the "row" column
                    col_num_clicked = event[2][1]
                    new_table = sort_table(data, (col_num_clicked, 0))
                    window["-TABLE-"].update(new_table)
                    data = new_table
                    continue
                if event[2][1] == 0:
                    pyperclip.copy(data[int(event[2][0] or 0)][0])
                    continue
                pyperclip.copy(data[int(event[2][0] or 0)][0])
                mkvpath = change_suffixex_to_mkv(data[int(event[2][0] or 0)][-1])
                subprocess.Popen(
                    [
                        "mpv",
                        mkvpath,
                        f"--start={data[int(event[2][0] or 0)][-2] - timedelta(seconds=5)}",
                    ]
                )
    window.close()


if __name__ == "__main__":
    main()
