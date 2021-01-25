import os
from os.path import join, getsize
import time


def format_time(longtime):
    '''格式化时间的函数'''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(longtime))


def get_dir_size(file_path):
    size = 0
    if os.path.isdir(file_path):
        for root, dirs, files in os.walk(file_path):
            size += sum([getsize(join(root, name)) for name in files])
    else:
        size = getsize(file_path)
    return format_byte(size)


def format_byte(number):
    '''格式化文件大小的函数'''
    for (scale, label) in [(1024 * 1024 * 1024, "GB"), (1024 * 1024, "MB"), (1024, "KB")]:
        if number >= scale:
            return "%.2f %s" % (number * 1.0 / scale, label)
        elif number == 1:
            return "1字节"
        else:  # 小于1字节
            byte = "%.2f" % (number or 0)

    return (byte[:-3]) if byte.endswith(".00") else byte + "字节"


if __name__ == '__main__':
    pass
