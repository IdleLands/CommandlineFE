import traceback
from idlelands_api import IdleLandsAPI, IdleLandsException
import time


def main():
    idle = IdleLandsAPI.from_config(direct=True)
    while True:
        try:
            idle.login()
            print 'Got token %s' % idle.token

            while True:
                time.sleep(10)  # wait early to ensure we're all good

                start = time.time()
                player = idle.turn()
                print 'Took turn in %.2fs. (%s, %s)' % (time.time() - start, player['x'], player['y'])
        except IdleLandsException, e:
            traceback.print_exc()
        except Exception:
            # probably a timeout error, but we don't stop for no one!
            traceback.print_exc()


if __name__ == '__main__':
    main()