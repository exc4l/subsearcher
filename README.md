# subsearcher
Simple Application to search for words in subtitle files.


Currently the app needs to be started with some cli arguments to be able to write them into a config file which can be used on subsequent runs.

```python
python subsearcher.py --srtpath "PATH/SRT" --playerpath "PATH/MPV"
```

The video player is called via 
```python
subprocess.Popen(
                [
                    "mpv",
                    mkvpath,
                    f"--start={data[int(event[2][0] or 0)][-2] - timedelta(seconds=5)}",
                ]
            )
```
which might not work with other players than mpv.



To install dependencies:
```python
python -m pip install .
or
poetry install
```

The app features a simple word search that can make use of fugashi to tokenize the subtitle lines. To install:
```python
poetry install -E fugashi
```

This will install the packages fugashi and unidic. Afterwards 
```python
python -m unidic download
```
needs to be executed to download the dictionary for fugashi to use.


![](https://github.com/exc4l/subsearcher/blog/main/demo.gif)
