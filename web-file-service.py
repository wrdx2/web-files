# coding=utf-8
# import asyncio
import os
import tornado.httpserver
import tornado.ioloop
# import tornado.web
# import tornado.websocket
# from concurrent.futures.thread import ThreadPoolExecutor
from tornado.options import options
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
        files = os.listdir(current_path)
        files_info = []

        for file in files:
            file_path = os.path.join(current_path, file)
            file_info = {
                "name": file,
                "size": file_util.get_dir_size(file_path),
                "is_dir": os.path.isdir(current_path + "/" + file),
            }
            files_info.append(file_info)

        self.render("download/index.html", files=files_info)


# 调用预设位置接口
class CallLocation(RequestHandler):
    def post(self):
        int(self.get_argument('i'))
        self.finish("发送成功")
        return


class Application(Application):
    def __init__(self):
        handlers = [  # 路由设置
            (r"/main", MainHandler),
            (r"/upload/index", MainHandler),
            (r"/download/index", DownloadIndexHandler),
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
