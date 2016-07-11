#!/usr/bin/env python
import os
import sys
import argparse
import tempfile
import tarfile
import shutil
import subprocess
from flask import Flask, render_template, request, Response, redirect, url_for, send_file
from werkzeug import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/osmosis_facade/cache"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['tar.gz', "gz"])


class DataStore(object):
    def __init__(self):
        pass


class LocalDataStore(object):
    def __init__(self):
        pass


class OsmosisDataStore(object):
    def __init__(self):
        pass
   

def mkdir_p(pathname):
    try:
        (destination) = os.makedirs( pathname, 0755 )
    except OSError:
        pass


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname="")
        #tar.add(source_dir, arcname=os.path.basename(source_dir))


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/labels/<string:label>', methods=['DELETE'])
def delete_label(label):
    try:
        command = "osmosis eraselabel --objectStores=osmosis.dc1:1010 {label}".format(label=label)
        response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        print command, response
        return Response(response={"status": "deleted"},
                        status=200,
                        mimetype="application/json")
    except:
        error = {"message": "Error in osmosis server.", "command": command}
        return Response(response=error,
                        status=400,
                        mimetype="application/json")

@app.route('/labels/<string:label>', methods=['GET'])
def download_file(label):
    try:
        temp_dir = tempfile.mkdtemp(prefix='osmosis_facade_')
    
        command = "osmosis checkout --objectStores=osmosis.dc1:1010 {path} {label}".format(path=temp_dir, label=label)
        response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        archive_file_name = "{label}.tar.gz".format(label=label)
        archive = os.path.join(temp_dir, archive_file_name)
        make_tarfile(archive, temp_dir)
        print "created archive: ", archive, "temp_dir: ", temp_dir
        res = send_file(archive)
    finally:
        shutil.rmtree(temp_dir)
    return res


@app.route('/labels/<string:label>', methods=['POST'])
def upload_file(label):
    f = request.files['file']
    if f and allowed_file(f.filename):
        try:
            filename = secure_filename(f.filename)
            temp_dir = tempfile.mkdtemp(prefix='osmosis_facade_')
            #archive=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archive=os.path.join(temp_dir, filename)
            f.save(archive)
            # untar to temp dir
            print "archive:", archive, "temp_dir:", temp_dir, label
            retval = os.getcwd()
            print "Current working directory %s" % retval
            # Now change the directory
            os.chdir( temp_dir )
            with tarfile.open(archive) as tar:
                tar.extractall()
            os.chdir(retval)
            os.remove(archive)
            command = "osmosis checkin {path} --objectStores=osmosis.dc1:1010 {label}".format(path=temp_dir, label=label)
            print command
            response = subprocess.check_call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        finally:
            shutil.rmtree(temp_dir)
        # cleanup
        return Response(response=filename,
                        status=202,
                        mimetype="application/json")


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
    mkdir_p(app.config['UPLOAD_FOLDER'])
    app.run(host=ip, port=int(port), debug=True, use_reloader=True)
    
if __name__ == '__main__':
    main()
