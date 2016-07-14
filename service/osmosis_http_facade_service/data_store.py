import os
import sys
import tempfile
import tarfile
import shutil
import subprocess
import logging

logger = logging.getLogger(__name__)

class DataStore(object):
    def __init__(self):
        pass

    def add(self, key, value):
        pass

    def remove(self, key):
        pass

    def get(self, key):
        pass


class LocalDataStore(object):
    def __init__(self):
        pass


class OsmosisDataStore(object):
    def __init__(self, address):
        self.address = address

    def add(self, key, value):
        archive = value
        # untar to temp dir
        retval = os.getcwd()
        # Now change the directory
        temp_dir = os.path.dirname(archive)
        logger.debug("archive: %s, temp_dir: %s, label: %s", archive, temp_dir, key)
        os.chdir( temp_dir )
        with tarfile.open(archive) as tar:
            tar.extractall()
        os.chdir(retval)
        os.remove(archive)
        command = "osmosis checkin {path} --objectStores={address} {label}".format(path=temp_dir, address=self.address, label=key)
        logger.debug(command)
        response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        return response

    def remove(self, key):
        try:
            command = "osmosis eraselabel --objectStores={address} {label}".format(address=self.address, label=key)
            response = subprocess.check_output(command, shell=True)
            logger.debug("command %s, returned: %s", command, response)
            return True
        except:
            return False

    def get(self, key):
        try:
            temp_dir = tempfile.mkdtemp(prefix='osmosis_facade_')
            command = "osmosis checkout --objectStores={address} {path} {label}".format(address=self.address, path=temp_dir, label=key)
            response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
            archive_file_name = "{label}.tar.gz".format(label=key)
            archive = os.path.join("/tmp", archive_file_name)
            self.make_tarfile(archive, temp_dir)
            logger.debug("created archive: %s, temp_dir: %s", archive, temp_dir)
        finally:
            shutil.rmtree(temp_dir)
        return archive
   
    @staticmethod
    def make_tarfile(output_filename, source_dir):
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname="")
            #tar.add(source_dir, arcname=os.path.basename(source_dir))
