
Build client:
-------------

.. code-block:: bash

    $ cd client
    $ make
    $ make install
    $ make pip-upload


Build service:
--------------

.. code-block:: bash

    $ cd service
    $ make
    $ make install
    $ make pip-upload

Install from pypi:
------------------

.. code-block:: bash

    $ pip install --trusted-host=rackattack-nas.dc1 -i http://rackattack-nas.dc1:5001 osmosis-http-facade-client

    $ pip install --trusted-host=rackattack-nas.dc1 -i http://rackattack-nas.dc1:5001 osmosis-http-facade-service
