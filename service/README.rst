
    $ cat /tmp/source_example.tar.gz | curl -X POST http://localhost:8080/labels/example -T -
    $ curl -X GET http://localhost:8080/labels/example -o /tmp/example.tar.gz

    # test that you got the same thing that you commited
    $ md5sum /tmp/source_example.tar.gz
    $ md5sum /tmp/example.tar.gz
    $ curl -X DELETE http://localhost:8080/labels/example
