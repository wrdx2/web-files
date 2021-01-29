import os
import time
import wmi
from os.path import join, getsize


def disk():
    c = wmi.WMI()
    # 获取硬盘分区
    i = 0
    disk_info = []
    partition_info = []
    for physical_disk in c.Win32_DiskDrive():
        disk_free = 0
        for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                disk_free += int(logical_disk.FreeSpace)
                partition_info.append({
                    "name": logical_disk.Name,
                    "size": logical_disk.Size,
                    "freeSize": logical_disk.FreeSpace,
                })

        disk_info.append({
            "name": physical_disk.Caption,
            "size": physical_disk.Size,
            "freeSize": disk_free,
            "par_info": partition_info,
        })
    # draw.text((10, 420), image_str, font=font, fill=(0, 0, 0))
    return disk_info


def format_time(longtime):
    '''格式化时间的函数'''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(longtime))


def get_path_file_name(path):
    return path.split("\\")[-1]


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
    # print(disk())
    for di in disk():
        print(di["name"])
        print("%0.2f" % (float(di["freeSize"]) / float(di["size"])))
        for p in di["par_info"]:
            print(p)
            print("%0.2f" % (float(p["freeSize"]) / float(p["size"])))
    pass
