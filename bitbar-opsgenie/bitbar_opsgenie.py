#!/usr/bin/env python
# -*- coding: utf-8 -*-

# <bitbar.title>Bitbar opsgenie</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Paul Kremer</bitbar.author>
# <bitbar.author.github>infothrill</bitbar.author.github>
# <bitbar.desc>Show status of opsgenie alerts.</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python, virtualenv</bitbar.dependencies>
# <bitbar.abouturl>http://url-to-about.com/</bitbar.abouturl>

import sys

from operator import attrgetter

from backports import configparser  # https://pypi.python.org/pypi/configparser
import requests


class MyConfigParser(configparser.ConfigParser):
    def getlist(self, section, option, fallback=None):
        value = self.get(section, option, fallback=fallback)
        return list(filter(None, (x.strip() for x in value.split())))


def main():
    config = MyConfigParser()
    config.read('bitbar_opsgenie.conf')

    icons = {
        'blue': config.get('icons', 'blue'),
        'black': config.get('icons', 'black'),
    }

    api = config.get('opsgenie.com', 'api')
    apikey = config.get('opsgenie.com', 'apikey')
    headers = {'Authorization': 'GenieKey %s' % apikey}
    alerts_api = '%s/v2/alerts' % api

    payload = {'query': 'status:open AND teams:"DevOps"', 'limit': '20', 'sort': 'createdAt', 'order': 'desc'}
    r = requests.get(alerts_api, headers=headers, params=payload)
    response = r.json()
    alerts = response['data']

    print('|image=%s' % (icons['black']))
    print('---')
    # print('open/unacked: TODO|color=black href=https://app.opsgenie.com/alert')
    for alert in alerts:
        if alert['acknowledged']:
            color = 'blue'
        else:
            color = 'red'
        print('%s | color=%s href=%s' % (alert['message'], color, 'https://app.opsgenie.com/alert#/show/%s/details' % alert['id']))
        print('--Details')
        print('--%s' % alert['createdAt'])
        print('--%s' % alert['status'])
        print('--%s' % alert['owner'])
        print('--%s' % alert['priority'])
        
    print('Refresh... | refresh=true')


if __name__ == '__main__':
    sys.exit(main())
