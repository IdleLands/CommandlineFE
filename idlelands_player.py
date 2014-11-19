import calendar
import time


class IdleLandsPlayer(object):
    def __init__(self, player):
        super(IdleLandsPlayer, self).__init__()
        self.data = player

    def __getitem__(self, item):  # backwards compatibility
        return self.data.__getitem__(item)

    @staticmethod
    def _parse_timestamp(timestamp):
        return calendar.timegm(time.strptime(timestamp[:-5], '%Y-%m-%dT%H:%M:%S'))

    def retrieve_events(self, since=0):
        events = []

        for event in self.data['recentEvents']:
            timestamp = self._parse_timestamp(event['createdAt'])
            if timestamp > since:
                event['_time'] = timestamp
                events.append(event)

        return events