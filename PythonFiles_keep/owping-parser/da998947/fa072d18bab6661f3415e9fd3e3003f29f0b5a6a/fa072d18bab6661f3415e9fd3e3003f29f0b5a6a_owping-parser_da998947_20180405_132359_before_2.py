import socket
from math import isnan


class Parser(object):
    def parse_owping(self, owping):
        from_client = None
        line_nr = 1
        result = OWPingResult()
        for line in owping.splitlines():
            print('reading Line {}'.format(line_nr))
            line_nr += 1
            if '--- owping statistics from' in line:
                if 'from [{}'.format(socket.gethostname()) in line:
                    from_client = True
                    print('to_server')
                elif 'to [{}'.format(socket.gethostname()) in line:
                    from_client = False
                    print('from_server')
                else:
                    raise WrongHostnameException(
                        'It seems like the hostname of the Test is not the hostname of your System')
            elif not (from_client is None):
                if line.startswith('SID:'):
                    sid = line.split('\t')[1]
                    if from_client:
                        result.from_client['sid'] = sid
                    else:
                        result.from_server['sid'] = sid
                elif line.startswith('first:'):
                    first = line.rsplit('\t', maxsplit=1)[-1]
                    if from_client:
                        result.from_client['first'] = first
                    else:
                        result.from_server['first'] = first
                elif line.startswith('last:'):
                    last = line.rsplit('\t', maxsplit=1)[-1]
                    if from_client:
                        result.from_client['last'] = last
                    else:
                        result.from_server['last'] = last
                elif 'sent' and 'lost' and 'duplicates' in line:
                    stats = line.split(',')
                    sent = stats[0].strip().split(' ')[0]
                    lost = stats[1].strip().split(' ')[0]
                    duplicates = stats[2].strip().split(' ')[0]
                    if from_client:
                        result.from_client['sent'] = sent
                        result.from_client['lost'] = lost
                        result.from_client['duplicates'] = duplicates
                    else:
                        result.from_server['sent'] = int(sent)
                        result.from_server['lost'] = int(lost)
                        result.from_server['duplicates'] = int(duplicates)
                elif line.startswith('one-way delay min/median/max'):
                    delay = line.split(',')[0].split('=')[1].strip().split(' ')[0].split('/')
                    try:
                        min = float(delay[0])
                        if isnan(min):
                            min = None
                    except ValueError:
                        min = None
                    try:
                        median = float(delay[1])
                        if isnan(median):
                            median = None
                    except ValueError:
                        median = None
                    try:
                        max = float(delay[2])
                        if isnan(max):
                            max = None
                    except ValueError:
                        max = None
                    if from_client:
                        result.from_client['delay']['min'] = min
                        result.from_client['delay']['median'] = median
                        result.from_client['delay']['max'] = max
                    else:
                        result.from_server['delay']['min'] = min
                        result.from_server['delay']['median'] = median
                        result.from_server['delay']['max'] = max
                elif line.startswith('one-way jitter ='):
                    try:
                        jitter = float(line.split('=')[1].strip().split(' ')[0])
                        if isnan(jitter):
                            jitter = None
                    except ValueError:
                        jitter = None
                    if from_client:
                        result.from_client['jitter'] = jitter
                    else:
                        result.from_server['jitter'] = jitter
                elif line.startswith('Hops ='):
                    try:
                        hops = int(line.split('=')[1].strip().split()[0])
                    except ValueError:
                        hops = None
                    if from_client:
                        result.from_client['hops'] = hops
                    else:
                        result.from_server['hops'] = hops
        return result


class OWPingResult(object):
    def __init__(self):
        self.from_client = dict.fromkeys(['sid', 'first', 'last', 'sent', 'lost', 'duplicates', 'jitter', 'hops'])
        self.from_client['delay'] = {'min': None, 'max': None, 'median': None}
        self.from_server = dict.fromkeys(['sid', 'first', 'last', 'sent', 'lost', 'duplicates',  'jitter', 'hops'])
        self.from_server['delay'] = {'min': None, 'max': None, 'median': None}


class WrongHostnameException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
