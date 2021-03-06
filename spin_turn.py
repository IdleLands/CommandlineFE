import traceback
from idlelands_api import IdleLandsAPI, IdleLandsException
import time


def main():
    latest_event = time.time()

    idle = IdleLandsAPI.from_config(direct=True)
    while True:
        try:
            if not idle.token:
                idle.login()
                print 'Got token %s' % idle.token

            while True:
                time.sleep(10)  # wait early to ensure we're all good

                start = time.time()
                player = idle.turn()
                print 'Took turn in %.2fs. (%s, %s)' % (time.time() - start, player['x'], player['y'])

                for event in player.retrieve_events(since=latest_event):
                    latest_event = event['_time']

                    print event['message']
        except IdleLandsException, e:
            if e.message == u'Token validation failed.':
                idle.token = None  # trigger relogin

            traceback.print_exc()
        except Exception:
            # probably a timeout error, but we don't stop for no one!
            traceback.print_exc()

        time.sleep(3)


if __name__ == '__main__':
    main()