# AvalonXmlTools

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/joshuaavalon/AvalonXmlTools/blob/master/LICENSE)

This is the common tools that I used for [AvalonXmlAgent.bundle](https://github.com/joshuaavalon/AvalonXmlAgent.bundle).

## Install

```bash
pip install -r requirements.txt
```

It is recommend to install it in virtualenv.

## Usage

There currently two type of usage. Run it in command line and enter the options.

```bash
python tool.py
```

Or run it with argument

```bash
python tool.py thumb
```

## Features

> You can always use `-h` or `--help` to see the usage.

### Create

```bash
python tool.py create <name> [options]
```

This generates a batch of episode xml base on options. Generated file name will be liked `<name> - s01e01.xml`

### Thumb

```bash
python tool.py thumb [options]
```

This scans the current directory for TV XML and movie XML and update the thumb entries of the actor base on a JSON file created by `cast`.
This format is simply actor name to thumb path. Example
```json
{
  "Alice": "https://example.com/aclice.png"
}
```

### Cast
```bash
python tool.py cast [options]
```

This generates a `cast.json` for `thumb`. It is useful if you host a static server which allow your Plex to actor thumbnail from it.

### Normalize

```bash
python tool.py normalize [options]
```

Normalize files base on **MY** standard.


### Youtube

```bash
python tool.py youtube [options]
```

Use [youtube-dl](https://github.com/rg3/youtube-dl) to download video or playlist from Youtube and pip the metadata to XML files.

You can also use `plexy.py` to write your only script.
