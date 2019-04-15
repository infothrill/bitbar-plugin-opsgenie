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

from backports import configparser  # https://pypi.python.org/pypi/configparser
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


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
    schedule_api = '%s/v2/schedules' % api
    user_api = '%s/v2/users' % api

    # setup a requests session object:
    s = requests.Session()
    # with authentication built-in:
    s.headers.update(headers)
    # and with retry logic:
    s = requests_retry_session(session=s)

    print('|image=%s' % (icons['black']))
    print('---')

    # fetch all schedules
    payload = {'expand': 'false'}
    r = s.get(schedule_api, params=payload, timeout=(3.05, 12))
    response = r.json()
    schedules = response['data']

    # for each schedule, find team, current on-call users and open alerts
    user = {}  # internal lookup for person/user details
    for schedule in schedules:
        schedule_id = schedule.get('id')
        schedule_team = schedule.get('ownerTeam').get('name')

        payload = {'flat': 'true', 'scheduleIdentifierType': 'id'}
        r = s.get(schedule_api + '/%s/on-calls' % schedule_id, params=payload, timeout=(3.05, 12))
        response = r.json()
        whosoncall = response['data']['onCallRecipients']
        for person in whosoncall:
            if person not in user:
                payload = {'expand': 'contact'}
                r = s.get(user_api + '/' + person, params=payload, timeout=(3.05, 12))
                response = r.json()
                user[person] = response['data']

        for person in whosoncall:
            print('%s %s: %s' % (schedule_team, schedule.get('name'), user[person]['fullName']))
            for usercontact in (x for x in user[person]['userContacts'] if x['enabled'] is True):
                print('--%s : %s' % (usercontact['contactMethod'], usercontact['to']))

        # fetch current alerts for this schedule / team
        payload = {
            'query': 'status:open AND teams:"%s"' % schedule.get('ownerTeam').get('name'),
            'limit': '20', 'sort': 'createdAt', 'order': 'desc'
        }
        r = s.get(alerts_api, params=payload, timeout=(3.05, 12))
        response = r.json()
        alerts = response['data']

        for alert in alerts:
            if alert['acknowledged']:
                color = 'blue'
            else:
                color = 'red'
            print('%s | color=%s href=%s' % (
                alert['message'],
                color,
                'https://app.opsgenie.com/alert#/show/%s/details' % alert['id']
            )
            )
            print('--Details')
            print('--%s' % alert['createdAt'])
            print('--%s' % alert['status'])
            print('--%s' % alert['owner'])
            print('--%s' % alert['priority'])

    print('Refresh... | refresh=true')


if __name__ == '__main__':
    sys.exit(main())
