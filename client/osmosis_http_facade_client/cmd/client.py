#!/usr/bin/env python
import os
import sys
import shutil
import tarfile
import tempfile
import subprocess
import argparse


class Osmosis(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='osmosis wrapper.',
                                         usage='''transfer.py <command> [<args>]
        
        The most commonly used osmosis commands are:
           submit     Record changes to the repository
           bring      Download objects and refs from another repository
           bringlabel Download objects and refs from another repository
           eraselabel Deletes a label.
        ''')
        parser.add_argument('command', help='Subcommand to run [bring, submit]')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print 'Unrecognized command'
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()
        self.command = args.command
    
    def submit(self):
        parser = argparse.ArgumentParser(description='submit')
        parser.add_argument('-s', '--source', dest='source', action='store', required=True,
                            help='directory/file name to send')
        parser.add_argument('-p', '--product', dest='product', action='store', default='rpms',
                            help='The product name')
        parser.add_argument('-b', '--base_repo', dest='base_repo', action='store', required=True,
                            help='The repository name.')
        parser.add_argument('-q', '--quality', dest='quality', action='store', required=True,
                            help='clean/dirty etc...')
        parser.add_argument('-a', "--address", dest='address', action='store', default="osmosis.dc1:8080",
                            help='the osmosis wrapper service address')
        self.args = parser.parse_args(sys.argv[2:])
    
    def bring(self):
        parser = argparse.ArgumentParser(description='bring')
        parser.add_argument('-d', '--dest', dest='dest', action='store', required=True,
                            help='output directory')
        parser.add_argument('-p', '--product', dest='product', action='store', required=True,
                            help='The product name [targz, rootfs, rpm, rpms]')
        parser.add_argument('-b', '--base_repo', dest='base_repo', action='store', required=True,
                            help='The repository name.')
        parser.add_argument('-q', '--quality', dest='quality', action='store', required=True,
                            help='clean/dirty etc...')
        parser.add_argument('-a', "--address", dest='address', action='store', default="osmosis.dc1:8080",
                            help='the osmosis wrapper service address.')
        self.args = parser.parse_args(sys.argv[2:])

    def bringlabel(self):
        parser = argparse.ArgumentParser(description='bringlabel')
        parser.add_argument('-d', '--dest', dest='dest', action='store', required=True,
                            help='output directory')
        parser.add_argument('-l', '--label', dest='label', action='store', required=True,
                            help='the label to store/retrive.')
        parser.add_argument('-a', "--address", dest='address', action='store', default="osmosis.dc1:8080",
                            help='the osmosis wrapper service address.')
        self.args = parser.parse_args(sys.argv[2:])

    def eraselabel(self):
        parser = argparse.ArgumentParser(description='eraselabel')
        parser.add_argument('-l', '--label', dest='label', action='store', required=True,
                            help='the label to store/retrive.')
        parser.add_argument('-a', "--address", dest='address', action='store', default="osmosis.dc1:8080",
                            help='the osmosis wrapper service address.')
        self.args = parser.parse_args(sys.argv[2:])



class Client():
    def __init__(self, options):
        self.options = options

    @staticmethod
    def _mkdir_p(pathname):
        try:
            (destination) = os.makedirs( pathname, 0755 )
        except OSError:
            pass

    @staticmethod
    def _create_label(base_repo, product, quality):
        command = "git rev-parse HEAD"
        sha = subprocess.check_output(command, shell=True)
        label = "solvent__{base_repo}__{product}__{sha}__{quality}".format(
            base_repo=base_repo,
            product=product,
            sha=sha.rstrip(),
            quality=quality)
        label = label.replace("-", "_")
        return label

    @staticmethod
    def make_tarfile(output_filename, source_dir):
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname="")
            #tar.add(source_dir, arcname=os.path.basename(source_dir))

    def submit(self, args):
        label = Client._create_label(base_repo=args.base_repo,
                    product=args.product,
                    quality=args.quality)
        self._submit(label, args.source, args.address)

    def bring(self, args):
        label = Client._create_label(base_repo=args.base_repo,
                    product=args.product,
                    quality=args.quality)
        self._bring(label, args.dest, args.address)

    def bringlabel(self, args):
        self._bring(args.label, args.dest, args.address)

    def eraselabel(self, args):
        command = "curl --silent -X DELETE http://{address}/labels/{label}".format(address=args.address,
                                                                                 label=args.label)
        response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
 
    def _submit(self, label, input_directory, address):
        temp_dir = tempfile.mkdtemp(prefix='osmosis_facade_client_')
        archive = os.path.join(temp_dir, "{}.tar.gz".format(label))
        try:
            Client.make_tarfile(archive, input_directory)
            command = "curl --silent -X POST http://{address}/labels/{label} -F file=@{archive}".format(address=address,
                                                                                                        label=label,
                                                                                                        archive=archive)
            response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        finally:
            shutil.rmtree(temp_dir)
    
    def _bring(self, label, output_directory, address):
        Client._mkdir_p(output_directory)
        command = "curl --silent http://{address}/labels/{label} | tar xzvf - -C {path}".format(
            address=address,
            label=label,
            path=output_directory)
        response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)


def main():
    """
        ./transfer.py submit -b migration-tool -q dirty -p rpms -s /path/to_send/ -a localhost:8080
        ./transfer.py bring -b migration-tool -q dirty -s /path/to_send/ -a localhost:8080
        ./transfer.py bringlabel -l solvent__migration-tool__rpms__720d55224cc0cbf3b1b6e2cd8eac9918022f5b0f__dirty -d /tmp/test1/my-northbound -a localhost:8080
        ./transfer.py eraselabel -l solvent__yogev__dirty__1111__dirty -a localhost:8080
    """
    osmosis_options = Osmosis()
    client = Client(osmosis_options)

    if osmosis_options.command == 'bring':
        client.bring(osmosis_options.args)
    elif osmosis_options.command == 'bringlabel':
        client.bringlabel(osmosis_options.args)
    elif osmosis_options.command == 'eraselabel':
        client.eraselabel(osmosis_options.args)
    elif osmosis_options.command == 'submit':
        client.submit(osmosis_options.args)


if __name__ == "__main__":
    main()
