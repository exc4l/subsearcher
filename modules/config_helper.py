from configparser import ConfigParser
from pathlib import Path


def get_config_parser():
    return ConfigParser()


def read_config_obj(config):
    return (
        Path(config["Paths"]["SrtPath"]),
        Path(config["Paths"]["VocabPath"]),
        Path(config["Paths"]["PlayerPath"]),
        Path(config["Paths"]["KnownPath"]),
        Path(config["Paths"]["IgnorePath"]),
        Path(config["Paths"]["YomiPath"]),
        Path(config["Paths"]["PTWPath"]),
    )


def check_config_valid(conf):
    """
    Check if the config contains the minimal needed path to run the script
    srt path and player path
    """
    try:
        srtpath = Path(conf["Paths"]["SrtPath"])
        # print(srtpath)
        if str(srtpath) == ".":
            return False
        playerpath = Path(conf["Paths"]["PlayerPath"])
        return True
    except KeyError as e:
        return False


def make_default_config(conf):
    """
    fill config with default keys
    """
    pathkeys = [
        "SrtPath",
        "VocabPath",
        "KnownPath",
        "IgnorePath",
        "YomiPath",
        "PlayerPath",
        "PTWPath",
    ]
    if not conf.has_section("Paths"):
        conf["Paths"] = dict()
    for k in pathkeys:
        if k not in conf["Paths"]:
            conf["Paths"][k] = ""
    return conf


def check_required_settings(vals):
    if vals.get("-SRTP-") == "Required" or vals.get("-PP-") == "Required":
        return False
    return True


def config_from_values(conf, vals):
    pathkeys = [
        "SrtPath",
        "VocabPath",
        "KnownPath",
        "IgnorePath",
        "YomiPath",
        "PTWPath",
        "PlayerPath",
    ]
    valkeys = ["-SRTP-", "-VOCP-", "-KP-", "-IP-", "-YP-", "-PTW-", "-PP-"]
    for p, v in zip(pathkeys, valkeys):
        conf["Paths"][p] = vals[v]
    return conf


def write_config(confp, conf):
    with open(confp, "w") as configfile:
        conf.write(configfile)
