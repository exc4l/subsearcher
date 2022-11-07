import operator
import subprocess
from datetime import timedelta
from pathlib import Path
from tabnanny import check

import pyperclip
import PySimpleGUI as sg
import srt

import modules.yomichan_parser as yp
from modules.config_helper import (
    check_config_valid,
    check_required_settings,
    config_from_values,
    get_config_parser,
    make_default_config,
    read_config_obj,
    write_config,
)
from modules.text_manipulation import (
    change_suffix_to_mkv,
    clean_txt,
    pretty_path,
    remove_names,
    check_allowed_char,
)
from modules.token_db_parser import load_token_db, make_token_db
from modules.vocab_analyzer import analyze_data

try:
    from sudachipy import Dictionary, SplitMode

    TOKENIZER = True
except ImportError as e:
    TOKENIZER = False

from sys import platform


ICON = b"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"
sg.theme("SystemDefault1")

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

ROOT = Path(__file__).parent.resolve()
# print(ROOT)
HOME = Path.home()
# print(HOME)
CONFNAME = "config.ini"

PROGRESS_BAR_WIDTH = 100

THEME = "vista" if "win32" in platform else "aqua"


def freqdict_helper(freqdict, word):
    txt = freqdict.get(word, "0")
    if txt == "0":
        # print(f"{word=}")
        return "W: 40K F: 1K %: 0.5"
    wtxt, ftxt, ptxt = yp.parse_freq_text(txt)
    return txt


def create_analyze_win(ptw):
    layout = [
        [
            sg.Table(
                values=[],
                headings=["Anime", "Overall Gain", "Vocab List Gain"],
                auto_size_columns=False,
                col_widths=[20, 15, 15],
                display_row_numbers=True,
                justification="center",
                num_rows=30,
                # size=(30, 60),
                # alternating_row_color="lightgrey",
                key="-ANA-",
                # selected_row_colors='red on yellow',
                enable_events=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
            )
        ],
        [sg.Sizegrip()],
    ]
    return sg.Window("PTW", layout, ttk_theme=THEME, icon=ICON, finalize=True)


def create_settings_win(conf):
    srtp, voc, play, know, igno, yomi, ptw = read_config_obj(conf)
    layout = [
        [
            sg.Text("SRT Folder:", size=(12, 1)),
            sg.Input(
                "Required" if str(srtp) == "." else srtp, key="-SRTP-", size=(50, 1)
            ),
            sg.FolderBrowse(initial_folder=HOME),
        ],
        [
            sg.Text("Vocab File:", size=(12, 1)),
            sg.Input("" if str(voc) == "." else voc, k="-VOCP-", size=(50, 1)),
            sg.FileBrowse(initial_folder=HOME),
        ],
        [
            sg.Text("Known File:", size=(12, 1)),
            sg.Input("" if str(know) == "." else know, k="-KP-", size=(50, 1)),
            sg.FileBrowse(initial_folder=HOME),
        ],
        [
            sg.Text("Ignore File:", size=(12, 1)),
            sg.Input("" if str(igno) == "." else igno, k="-IP-", size=(50, 1)),
            sg.FileBrowse(initial_folder=HOME),
        ],
        [
            sg.Text("Yomichan Dictionary:", size=(12, 1)),
            sg.Input("" if str(yomi) == "." else yomi, k="-YP-", size=(50, 1)),
            sg.FileBrowse(initial_folder=HOME),
        ],
        [
            sg.Text("PTW Folder:", size=(12, 1)),
            sg.Input("" if str(ptw) == "." else ptw, k="-PTW-", size=(50, 1)),
            sg.FolderBrowse(initial_folder=HOME),
        ],
        [
            sg.Text("Player Path:", size=(12, 1)),
            sg.Input(
                "Required" if str(play) == "." else play, key="-PP-", size=(50, 1)
            ),
            sg.FileBrowse(
                initial_folder=str(ROOT),
                file_types=(("Executable", "*.exe"), ("All", "*.*")),
            ),
        ],
        [sg.Button("Save"), sg.Button("Exit")],
    ]
    return sg.Window("Settings", layout, ttk_theme=THEME, icon=ICON, finalize=True)


def read_vocabs(vocpath):
    if vocpath.is_file():
        from random import shuffle

        with open(vocpath, "r", encoding="utf-8") as f:
            vocabs = list(set(f.read().split()))
            shuffle(vocabs)
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


def search_word(
    word,
    srts,
    sfdict,
    parsedict,
    winhandle=None,
    tok_mode="Exact Match",
    tagger=None,
    token_db=None,
    freqdict=None,
    tokenize_search_word=False,
):
    """
    searches for a word inside the subtitles. first via checking if the word appears
    inside the whole srt file and then by tokenizing every line in the subtitles
    and checking if the searched for token appears.
    Pretty sure that this function should look different
    """
    tabdata = list()
    fac = (PROGRESS_BAR_WIDTH + 1) / (len(srts) + 1)
    prog = 0
    if tagger and tokenize_search_word:
        tagres = tagger.tokenize(word)[0]
        tokword = tagres.normalized_form()
    else:
        tokword = None
    for sf in srts:
        res = list()
        if tok_mode != "Tokenizer":
            if word in sfdict[sf]:
                for s in parsedict[sf]:
                    text = clean_txt(remove_names(s.content))
                    if word in text and s.content[0] not in ["♬", "♪"]:
                        res.append(s)
                if len(res) > 4:
                    for r in res:
                        idx = r.content.find(word)
                        idxmin = idx - 3 if (idx - 3) > 0 else 0
                        idxmax = idx + 3 + len(word)
                        lowidx = idx - 1 if (idx - 1) > 0 else 0
                        highidx = (
                            idx + 1
                            if (idx + 1) < len(r.content)
                            else len(r.content) - 1
                        )
                        if len(word) == 1 and (
                            check_allowed_char(r.content[lowidx])
                            or check_allowed_char(r.content[highidx])
                        ):
                            continue
                        tabdata.append(
                            [
                                word,
                                sf,
                                r.start,
                                r.content[idxmin:idxmax].replace("\n", " "),
                            ]
                        )
        if tok_mode == "Exact + Tokenizer" or tok_mode == "Tokenizer":
            tres = list()
            for ps in parsedict[sf]:
                content = token_db[str(sf.relative_to(srts[0].parent))][str(ps.index)]
                if tokword:
                    if word in content or tokword in content:
                        tres.append(ps)
                else:
                    if word in content:
                        tres.append(ps)
            if len(tres) > 0:
                for r in tres:
                    if r not in res:
                        tabdata.append([word, sf, r.start])
        prog += 1
        if winhandle and prog % 5:
            winhandle["-PROG-"].update("█" * int(prog * fac))
            winhandle.refresh()
    if tok_mode == "Exact Match":
        prettydata = [
            [i[0], freqdict_helper(freqdict, i[0]), pretty_path(i[1]), i[3], i[2], i[1]]
            for i in tabdata
        ]
    else:
        prettydata = [
            [i[0], freqdict_helper(freqdict, i[0]), pretty_path(i[1]), i[2], i[1]]
            for i in tabdata
        ]
    return prettydata


def get_layout(data, headings):
    if TOKENIZER:
        options = [
            "Exact + Tokenizer",
            "Tokenizer",
            "Exact Match",
        ]
    else:
        options = ["Exact Match"]
    layout = [
        [
            sg.Button("Settings"),
            sg.Button("Analyze PTW"),
        ],
        [
            sg.Text(" " * 50),
            sg.Text("Word Search:", size=(10, 1)),
            sg.Input("", k="-Search-", size=(15, 1)),
            sg.Button("Search", bind_return_key=True),
        ],
        [
            sg.Text(" " * 50),
            sg.Text("Search Mode:", size=(10, 1)),
            sg.Combo(
                options,
                default_value=options[0],
                key="-TOKENIZER-",
                readonly=True,
                auto_size_text=True,
            ),
        ],
        [
            sg.Table(
                values=data,
                headings=headings,
                auto_size_columns=False,
                col_widths=[10, 25, 20, 25] if len(headings) > 3 else [10, 25, 20],
                display_row_numbers=True,
                justification="center",
                num_rows=30,
                font=("NotoSansJP", 16),
                header_font=("Helvetica", 16, "bold"),
                # size=(30, 60),
                background_color="#202020",
                alternating_row_color="#333333",
                selected_row_colors=("#5E81AC", "#5E81AC"),
                key="-TABLE-",
                # selected_row_colors='red on yellow',
                enable_events=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
            )
        ],  # Comment out to not enable header and other clicks
        [
            # sg.Text(
            #     "",
            #     size=(PROGRESS_BAR_WIDTH, 1),
            #     relief="sunken",
            #     font=("Arial", 1),
            #     text_color="blue",
            #     background_color="white",
            #     key="-PROG-",
            #     metadata=0,
            # ),
            sg.ProgressBar(
                max_value=100, orientation="h", size=(40, 5), key="progress"
            ),
            sg.Sizegrip(),
        ],
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


def search_vocab_list(
    freqdict, config, top_100_freq=False, tagger=None, token_db=None, winhandle=None
):
    srtpath, vocpath, playpath, knowpath, ignopath, yomipath, ptwpath = read_config_obj(
        config
    )
    data = list()
    vocabs = read_vocabs(vocpath)
    known = set(read_vocabs(knowpath))
    igno = set(read_vocabs(ignopath))
    search_list = [word for word in vocabs if word not in known and word not in igno]
    srts, sfdict, parsedict = parse_subtitles(srtpath)
    if len(search_list) < 1:
        return srts, sfdict, parsedict, data

    prog = 0

    def parse_perc_text(txt):
        try:
            wtxt, ftxt, ptxt = yp.parse_freq_text(txt)
        except Exception as e:
            print(f"{txt=}")
        return yp._parse_ptxt(ptxt)

    search_freq_list = [
        (word, parse_perc_text(freqdict_helper(freqdict, word)))
        for word in search_list
        if word
    ]
    search_list = [
        w for w, v in sorted(search_freq_list, reverse=True, key=operator.itemgetter(1))
    ]
    if top_100_freq:
        search_list = search_list[:100]

    fac = (PROGRESS_BAR_WIDTH + 1) / len(search_list)
    for word in search_list:
        data.extend(
            search_word(
                word,
                srts,
                sfdict,
                parsedict,
                tagger=tagger,
                token_db=token_db,
                freqdict=freqdict,
                # tok_mode="Exact + Tokenizer",
            )
        )
        prog += 1
        if prog % 20:
            # winhandle["-PROG-"].update("█" * int(prog * fac))
            winhandle["progress"].update_bar(int(prog * fac))
            print(int(prog * fac))
            winhandle.refresh()
    return srts, sfdict, parsedict, data


def main():
    if TOKENIZER:
        tagger = Dictionary(dict="full").create(mode=SplitMode.A)
    else:
        tagger = None

    confpath = Path(ROOT / CONFNAME)
    config = get_config_parser()
    if confpath.is_file():
        config.read(confpath)
    settings_win = None
    ana_win = None
    if not check_config_valid(config):
        config = make_default_config(config)
        settings_win = create_settings_win(config)
        while True:
            event, values = settings_win.read()
            if event in (sg.WINDOW_CLOSED, "Exit"):
                settings_win.close()
                break
            if event == "Save":
                val_dict = {k: v for k, v in values.items() if v}
                if check_required_settings(values):
                    config = config_from_values(config, values)
                    write_config(confpath, config)
                    settings_win.close()
    srtpath, vocpath, playpath, knowpath, ignopath, yomipath, ptwpath = read_config_obj(
        config
    )
    if yomipath.is_file():
        freqdict = yp.read_frequency_dict(yomipath)
    else:
        freqdict = dict()
    if len(freqdict) > 1:
        headings = [
            "Word",
            "Frequency",
            "Anime",
            "Word Occurence",
        ]
    else:
        headings = ["Word", "Anime", "Word Occurence"]
    layout = get_layout([], headings)

    mainwin = sg.Window(
        "Sub Searcher",
        layout,
        ttk_theme=THEME,
        resizable=True,
        icon=ICON,
        finalize=True,
    )
    srts = list(srtpath.rglob("*.srt"))
    token_db = make_token_db(srts, srtpath, tagger)
    srts, sfdict, parsedict, data = search_vocab_list(
        freqdict,
        config,
        top_100_freq=False,
        tagger=tagger,
        token_db=token_db,
        winhandle=mainwin,
    )
    mainwin["-TABLE-"].update(data)

    while True:
        window, event, values = sg.read_all_windows()
        # print(event, values)
        if event == sg.WIN_CLOSED and window == mainwin:
            break
        if (event == sg.WIN_CLOSED or event == "Exit") and window == settings_win:
            settings_win.close()
            settings_win = None
        if event == sg.WIN_CLOSED and window == ana_win:
            ana_win.close()
            ana_win = None
        if event == "Settings":
            settings_win = create_settings_win(config)
        if event == "Analyze PTW":
            ana_win = create_analyze_win(ptwpath)
            ana_data = analyze_data(
                ptwpath=ptwpath,
                freqdict=freqdict,
                token_db=token_db,
                vocab=read_vocabs(vocpath),
                known_words=set(read_vocabs(knowpath)),
            )
            if not ana_data:
                ana_win.close()
            else:
                ana_win["-ANA-"].update(ana_data)
                import csv

                with open("ptw.csv", "w", newline="", encoding="utf-8") as csvfile:
                    csvwriter = csv.writer(
                        csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
                    )
                    for row in ana_data:
                        csvwriter.writerow([str(item) for item in row])
        if event == "Save":
            # print(values)
            if window == settings_win:
                if check_required_settings(values):
                    config = config_from_values(config, values)
                    write_config(confpath, config)
                    settings_win = None
                    window.close()
                    mainwin["-PROG-"].update("█" * 0)
                    mainwin.refresh()
                    srts, sfdict, parsedict, data = search_vocab_list(
                        freqdict,
                        config,
                        tagger=tagger,
                        token_db=token_db,
                        winhandle=mainwin,
                    )
                    (
                        srtpath,
                        vocpath,
                        playpath,
                        knowpath,
                        ignopath,
                        yomipath,
                        ptwpath,
                    ) = read_config_obj(config)
                    if (srtpath / "token_db.json").is_file():
                        token_db = load_token_db(srtpath / "token_db.json")
                    else:
                        token_db = make_token_db(srts, srtpath, tagger)
                    mainwin["-TABLE-"].update(data)
        if event == "Search":
            # print(values)
            # prog+=1
            # window["-PROG-"].update('█'*prog)
            if values.get("-Search-") != "":
                data = search_word(
                    values.get("-Search-"),
                    srts,
                    sfdict,
                    parsedict,
                    tok_mode=values.get("-TOKENIZER-"),
                    tagger=tagger,
                    token_db=token_db,
                    winhandle=window,
                    freqdict=freqdict,
                )
                # print(data)
                mainwin["-TABLE-"].update(data)
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
                    mainwin["-TABLE-"].update(new_table)
                    data = new_table
                    continue
                if event[2][1] == 0:
                    pyperclip.copy(data[int(event[2][0] or 0)][0])
                    continue
                # print(event)
                pyperclip.copy(data[int(event[2][0] or 0)][0])
                # print(f"{data[int(event[2][0] or 0)][0]=}")
                mkvpath = change_suffix_to_mkv(data[int(event[2][0] or 0)][-1])
                # print(f"{data[int(event[2][0] or 0)][-1]=}")
                # print(f"{data[int(event[2][0] or 0)][2]=}")
                subprocess.Popen(
                    [
                        playpath,
                        mkvpath,
                        f"--start={data[int(event[2][0] or 0)][-2] - timedelta(seconds=5)}",
                    ]
                )
    mainwin.close()


if __name__ == "__main__":
    main()
