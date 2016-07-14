
Install:
--------

    $ sudo dnf install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel
    $ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
    $ git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
    $ echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile
    $ exec "$SHELL"
    $ pyenv install 3.5.2
    $ pyenv virtualenv 3.5.2 osmosis-http-api-venv
    $ pyenv activate osmosis-http-api-venv
    $ pip install osmosis-http-facade -r local

Run:
----

- Runs in debug mode:

    $ osmosis-http-service start --address=0.0.0.0:8080 --debug=True

- Runs as a service:

    $ osmosis-http-service start --address=0.0.0.0:8080

Usage:
------

    $ cat /tmp/source_example.tar.gz | curl -X POST http://localhost:8080/labels/example -T -
    $ curl -X GET http://localhost:8080/labels/example -o /tmp/example.tar.gz

    # test that you got the same thing that you commited
    $ md5sum /tmp/source_example.tar.gz
    $ md5sum /tmp/example.tar.gz
    $ curl -X DELETE http://localhost:8080/labels/example
