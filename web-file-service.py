# coding=utf-8
import os
import tornado.ioloop
import tornado.httpserver
from tornado import iostream
from operator import itemgetter
from tornado.gen import coroutine
from tornado.options import options
from tornado.web import StaticFileHandler, RequestHandler, Application

from log import Logger
from file_util import file_util

file_log = Logger().get_logger()


class MainHandler(RequestHandler):
    def get(self):
        # import time
        # time.sleep(10)
        self.finish("Hello, world!!")
        return


class DownloadIndexHandler(RequestHandler):
    def get(self):
        path = None
        try:
            path = self.get_argument('file')
        except Exception as e:
            file_log.error(e)
        files_info = []

        # file_log.info(path)
        if path is None or path is "" or not os.path.isdir(path):
            self.render("download/index.html", path=[], files=files_info, disks=file_util.disk())
            # self.finish()
        else:
            download_path = path.replace("/", "\\")
            download_path = download_path.split("\\")

            bread_path = ""
            for i, d_path in enumerate(download_path):
                if d_path is not None and d_path is not "":
                    bread_path = bread_path + d_path
                    download_path[i] = bread_path
                    if i < len(download_path) - 1:
                        bread_path = bread_path + "\\"

            files = os.listdir(path)

            for file in files:
                file_path = os.path.join(path, file)
                file_info = {
                    "name": file,
                    "path": file_path,
                    "size": file_util.get_dir_size(file_path),
                    "is_file": os.path.isfile(file_path),
                }
                files_info.append(file_info)

            files_info = sorted(files_info, key=itemgetter('is_file', "name"))
            self.render("download/index.html", path=download_path, files=files_info, disks=file_util.disk())


class DownloadFileHandler(RequestHandler):
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
            except iostream.StreamClosedError as e:
                file_log.error(e)
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


class MySelfApplication(Application):
    def __init__(self):
        handlers = [  # 路由设置
            (r"/main", MainHandler),
            (r"/upload/index", MainHandler),
            (r"/download/index", DownloadIndexHandler),
            (r"/download/file", DownloadFileHandler),
            # 优化文件路径（不用在url打那么多），设置默认值为index
            (r"/(.*)", StaticFileHandler, {"path": "static/", "default_filename": "index.html"}),
        ]

        self.settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),  # 设置模板路径
            static_path=os.path.join(os.path.dirname(__file__), 'static'),  # 设置静态资源引用路路径
            # static_url_prefix='statics',  # 设置html中静态文件的引用路径，默认为/static/
            debug=True,
        )
        super(MySelfApplication, self).__init__(handlers, **self.settings)


if __name__ == "__main__":
    current_path = os.path.dirname(__file__)

    options.define("port", default="8888", help="run on the port", type=int)  # 设置全局变量port
    options.parse_command_line()  # 启动应用前面的设置项目

    http_server = tornado.httpserver.HTTPServer(MySelfApplication())
    http_server.listen(options.port)  # 在这里应用之前的全局变量port
    os.system(r"cmd /c start http://127.0.0.1:8888")
    tornado.ioloop.IOLoop.instance().start()  # 启动监听
