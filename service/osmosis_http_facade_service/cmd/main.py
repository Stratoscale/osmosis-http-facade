import argparse
import sys
import logging
import daemonocle
import osmosis_http_facade_service.http_service as http_service


class Cmd(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Osmosis http rest api.',
                                         usage='''{} <command> [<args>]
        
        The most commonly used osmosis commands are:
           start        Start the daemon.
           stop         Stop the daemon.
           restart      Restart the daemon
        '''.format(sys.argv[0]))
        parser.add_argument('command', help='Subcommand to run [start stop restart status]')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            logging.info('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        self.command = args.command
        getattr(self, args.command)()
    
    def start(self):
        parser = argparse.ArgumentParser(description='submit')
        parser.add_argument('-a', "--address",
                            dest='address',
                            action='store',
                            default="[::]:8080",
                            required=True,
                            help='the osmosis service address')
        self.args = parser.parse_args(sys.argv[2:])

    def stop(self):
        pass

    def restart(self):
        pass

def cb_shutdown(message, code):
    logging.info('Daemon is stopping')
    logging.debug(message)


CMD_OPTIONS = None


def run():
    logging.info('Daemon is starting')
    import pdb;pdb.set_trace()
    service = http_service.Service(CMD_OPTIONS.args.address)
    service.run()


def main():
    logging.basicConfig(level=logging.DEBUG)
    daemon = daemonocle.Daemon(
        worker=run,
        detach=False,
        shutdown_callback=cb_shutdown,
        pidfile='/tmp/osmosis-http.pid',
        #pidfile='/var/run/osmosis-http.pid',
    )
    global CMD_OPTIONS
    CMD_OPTIONS = Cmd()
    daemon.do_action(CMD_OPTIONS.command)


if __name__ == '__main__':
    main()
