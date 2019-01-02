# bitbar-plugin-opsgenie

This is a plugin for [Bitbar](https://github.com/matryer/bitbar) that hooks up
with the API of [Opsgenie](https://opsgenie.com) to show a summary of currently
open alerts.

## Installation

Since this is a python script with some dependencies, a convenience shell
script wrapper is provided:

```bash
git clone https://github.com/infothrill/bitbar-plugin-opsgenie.git

cd YOUR_BITBAR_PLUGIN_FOLDER

ln -s YOUR_CLONE/bitbar-opsgenie.60s.sh .
```

This wrapper will install dependencies into a virtual environment inside the
cloned repository.

## Configuration

Copy the example config `bitbar_opsgenie_sample.conf` to `bitbar_opsgenie.conf`
and fill in your credentials.
