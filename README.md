# `ecessemail`

Tools for handling ECESS email setup and maintenance

## Setup

```bash
# Both python2 and python3 should work; if they don't, file a bug
pip install -r requirements.txt
```

## Usage

### `forwarder_tools.py`

```bash
$ ./forwarder_tools.py --help
Usage: forwarder_tools.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  diff_forwarders  Print list of extra forwarders in current...
  draw_graph       Draw a directed graph of forwarding
  existing_fwd     Print existing forwarders as per...
  recipients       Prints final recipients for a mail that gets...
  write_csv        Write CSV of desired entries
```
