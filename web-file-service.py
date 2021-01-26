# coding=utf-8
# import asyncio
import os
import tornado.httpserver
import tornado.ioloop
# import tornado.web
# import tornado.websocket
# from concurrent.futures.thread import ThreadPoolExecutor
from tornado import iostream
from tornado.options import options
from tornado.gen import coroutine
from tornado.web import StaticFileHandler, RequestHandler, Application
from file_util import file_util

from log import Logger

file_log = Logger().get_logger()


class MainHandler(RequestHandler):
    def get(self):
        # import time
        # time.sleep(10)
        self.finish("Hello, world!!")
        return


class DownloadIndexHandler(RequestHandler):
    def get(self):
        download_path = "D:/迅雷下载"
        files = os.listdir(download_path)
        files_info = []

        for file in files:
            file_path = os.path.join(download_path, file)
            file_info = {
                "name": file,
                "path": file_path,
                "size": file_util.get_dir_size(file_path),
                "is_dir": os.path.isdir(file_path),
            }
            files_info.append(file_info)

        self.render("download/index.html", files=files_info)


class DownloadFileHandler(RequestHandler):
    # def get(self):
    #     file = self.get_argument('file')
    #     self.set_header('Content-Type', 'application/octet-stream')
    #     self.set_header('Content-Disposition', 'attachment; filename=' + file_util.get_path_file_name(file))
    #     buf_size = 4096
    #     with open(file, 'rb') as f:
    #         while True:
    #             data = f.read(buf_size)
    #             if not data:
    #                 break
    #             self.write(data)
    #     self.finish()
    @tornado.gen.coroutine
    def get(self):
        file_path = self.get_argument('file')
        content_length = file_util.getsize(file_path)
        self.set_header("Content-Length", content_length)
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition",
                        ("attachment;filename=%s" % file_util.get_path_file_name(file_path)).encode("utf8"))
        content = self.get_content(file_path)
        if isinstance(content, bytes):
            content = [content]
        for chunk in content:
            try:
                self.write(chunk)
                yield self.flush()
            except iostream.StreamClosedError:
                break
        return

    # 使用python自带的对于yield的应用对文件进行切片，for循环每运用一次就调用一次
    def get_content(self, file_path):
        start = None
        end = None
        with open(file_path, "rb") as file:
            if start is not None:
                file.seek(start)
            if end is not None:
                remaining = end - (start or 0)
            else:
                remaining = None
            while True:
                chunk_size = 64 * 1024  # 每片的大小是64K
                if remaining is not None and remaining < chunk_size:
                    chunk_size = remaining
                chunk = file.read(chunk_size)
                if chunk:
                    if remaining is not None:
                        remaining -= len(chunk)
                    yield chunk
                else:
                    if remaining is not None:
                        assert remaining == 0
                    return


class Application(Application):
    def __init__(self):
        handlers = [  # 路由设置
            (r"/main", MainHandler),
            (r"/upload/index", MainHandler),
            (r"/download/index", DownloadIndexHandler),
            (r"/download/file", DownloadFileHandler),
            # 优化文件路径（不用在url打那么多），设置默认值为index
            (r"/(.*)", StaticFileHandler,
             {"path": "static/", "default_filename": "index.html"}),
        ]

        self.settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),  # 设置模板路径
            static_path=os.path.join(os.path.dirname(__file__), 'static'),  # 设置静态资源引用路路径
            # static_url_prefix='statics',  # 设置html中静态文件的引用路径，默认为/static/
            debug=True,
        )
        super(Application, self).__init__(handlers, **self.settings)


if __name__ == "__main__":
    current_path = os.path.dirname(__file__)

    # thread_pool = ThreadPoolExecutor(10)

    # tornado 5 中引入asyncio.set_event_loop即可
    # asyncio.set_event_loop(asyncio.new_event_loop())

    options.define("port", default="8888", help="run on the port", type=int)  # 设置全局变量port
    # options.define("logging", default=file_log)
    options.parse_command_line()  # 启动应用前面的设置项目
    # [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)  # 在这里应用之前的全局变量port
    tornado.ioloop.IOLoop.instance().start()  # 启动监听
