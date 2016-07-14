import argparse
import logging
import osmosis_http_facade_service.http_service as http_service


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-a', "--address",
                    dest='address',
                    action='store',
                    default="[::]:8080",
                    required=True,
                    help='the osmosis service address')
args = parser.parse_args()


def main():
    ip, port = args.address.split(':')
    logging.basicConfig(level=logging.DEBUG)
    http_service.app.run(host=ip, port=int(port), debug=True, use_reloader=True)
    

if __name__ == '__main__':
    main()
