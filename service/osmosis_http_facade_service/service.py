#!/usr/bin/env python
import os
import tempfile
import shutil
import logging
import asyncio
from aiohttp import web
import osmosis_http_facade_service.data_store as data_store


logger = logging.getLogger(__name__)


def mkdir_p(pathname):
    try:
        (destination) = os.makedirs( pathname, exist_ok=True )
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Service(object):
    def __init__(self, address):
        self.address = address
        self.data_store = data_store.OsmosisDataStore(address="osmosis.dc1:1010")
        self.app = web.Application()
        self._bind()

    def _bind(self):
        self.app.router.add_route('GET', '/labels/{label}', self._get_label)
        self.app.router.add_route('DELETE', '/labels/{label}', self._delete_label)
        self.app.router.add_route('POST', '/labels/{label}', self._create_label)
    
    async def init(self, loop):
        ip, port = self.address.split(':')
        srv = await loop.create_server(
            self.app.make_handler(), ip, port)
        return srv
        
    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init(loop))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

    async def _delete_label(self, request):
        label = request.match_info.get('label', "")
        try:
            response = self.data_store.remove(label)
            resp = web.json_response(status=200) if response else web.json_response(status=404)
            await resp.prepare(request)
            return resp
        except:
            error = {"message": "Error in osmosis server."}
            return web.json_response(status=500, data=error)
    
    async def _get_label(self, request):
        label = request.match_info.get('label', "")
        archive = self.data_store.get(label)
        resp = web.StreamResponse(status=200)
        resp.content_type = 'application/octet-stream'
        # resp.content_length = len(archive)
        await resp.prepare(request)
        with open(archive, "rb") as f:
            resp.write(f.read())
            await resp.drain()
            await resp.write_eof()
        os.remove(archive)
        return resp
    
    async def _create_label(self, request):
        label = request.match_info.get('label', "")
        # should use content disposition
        try:
            temp_dir = tempfile.mkdtemp(prefix='osmosis_facade_')
            archive=os.path.join(temp_dir, label)
            with open(archive, "wb") as f:
                f.write(await request.read())
            self.data_store.add(label, archive)
        finally:
            shutil.rmtree(temp_dir)
        resp = web.json_response(status=202)
        await resp.prepare(request)
        return resp
