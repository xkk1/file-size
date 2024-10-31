#! /usr/bin/env python
"""
This file is part of file_size.
Copyright (C) 2024  xkk1

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import datetime
import os
import pathlib
import sys


def get_file_infomation(file_path: str) -> dict:
    """
    获取文件信息
    """
    file_infomation: dict = {
        "code": 0,
        "message": "success",
        "input_path": file_path,
        "type": "unknow",
        "size": 0
    }
    try:
        path = pathlib.Path(file_path)
        # 文件名/目录名
        file_infomation["name"] = path.name
        # 路径
        file_infomation["path"] = str(path)
        # 绝对路径
        file_infomation["absolute_path"] = str(path.absolute())
        # 获取文件信息
        stat_result: os.stat_result = path.stat()
        # 文件大小
        file_infomation["size"] = stat_result.st_size
        # 访问时间
        file_infomation["access_time"] = stat_result.st_atime
        # 修改时间
        file_infomation["modify_time"] = stat_result.st_mtime
        # 创建时间
        try:
            # https://docs.python.org/zh-cn/3/library/os.html#os.stat_result.st_birthtime
            # 该属性并不总是可用的，并可能引发 AttributeError
            # 在 3.12 版本发生变更: 目前 st_birthtime 已在 Windows 上可用
            file_infomation["create_time"] = stat_result.st_birthtime
        except:
            file_infomation["create_time"] = None
    except Exception as e:
        file_infomation["code"] = 1
        file_infomation["msg"] = str(e)
        return file_infomation
    
    if not path.exists():
        file_infomation["code"] = 2
        file_infomation["msg"] = "文件不存在"
        return file_infomation
    
    if path.is_file():
        file_infomation["type"] = "file"  # 文件
        # 扩展名
        file_infomation["extension"] = path.suffix[1:] if path.suffix else ""
        return file_infomation

    if path.is_dir():
        file_infomation["type"] = "dir"  # 目录
        file_infomation["iter_path"] = []
        file_infomation["size"] = 0
        for iter_path in path.iterdir():
            iter_path_infomation: dict = get_file_infomation(iter_path)
            file_infomation["iter_path"].append(iter_path_infomation)
            if iter_path_infomation["code"] == 0:
                file_infomation["size"] += iter_path_infomation["size"]
        return file_infomation

    file_infomation["code"] = -1
    file_infomation["msg"] = "不支持的文件类型"
    return file_infomation

def get_file_size_info(file_size_bytes):
    file_size_info: str = ""

    # IEC KiB    1024 B = 1 KiB
    # 二进制词头 https://zh.wikipedia.org/wiki/%E4%BA%8C%E9%80%B2%E4%BD%8D%E5%89%8D%E7%BD%AE%E8%A9%9E
    # IEC 60027-2 https://zh.wikipedia.org/wiki/IEC_60027-2
    binary_prefix: str = "KMGTPEZYRQ"  # TiB, GiB, MiB, KiB
    # SI kB    1000 B = 1 kB
    # 国际单位制词头 https://zh.wikipedia.org/wiki/%E5%9B%BD%E9%99%85%E5%8D%95%E4%BD%8D%E5%88%B6%E8%AF%8D%E5%A4%B4
    # 十进制前缀 SI https://zh.wikipedia.org/wiki/%E5%9B%BD%E9%99%85%E5%8D%95%E4%BD%8D%E5%88%B6
    metric_prefix: str = "kMGTPEZYRQ"  # TB, GB, MB, kB
    metric_prefix_zh: str = "千兆吉太拍艾泽尧容昆"
    # JEDEC KB    1024 B = 1 KB
    # JEDEC https://en.wikipedia.org/wiki/JEDEC_memory_standards
    jedec_prefix: str = binary_prefix  # TB, GB, MB, KB
    
    # B、KiB、MiB、GiB、TiB
    if file_size_bytes < 1024:
        file_size_info += f"{file_size_bytes} B"
    else:
        for i in range(1, len(binary_prefix)):
            if file_size_bytes < 1024 ** (i + 1):
                file_size_info += f"{file_size_bytes / (1024 ** i):.4f} {binary_prefix[i-1]}iB"
                break
        else:
            file_size_info += f"{file_size_bytes / (1024 ** len(binary_prefix)):.4f}"\
            + f"{binary_prefix[len(binary_prefix)-1]}iB"
    
    # B、KB、MB、GB、TB
    if file_size_bytes < 1000:
        file_size_info += " 字节"
    else:
        file_size_info += "    "
        for i in range(1, len(metric_prefix)):
            if file_size_bytes < 1000 ** (i + 1):
                file_size_info += f"{file_size_bytes / (1000 ** i):.4f} {metric_prefix[i-1]}B {metric_prefix_zh[i-1]}字节"
                break
        else:
            file_size_info += f"{file_size_bytes / (1000 ** len(metric_prefix)):.4f}"\
            + f"{metric_prefix[len(metric_prefix)-1]}B {metric_prefix_zh[len(metric_prefix)-1]}字节"
    
    # B 字节
    if file_size_bytes >= 1000:
        file_size_info += f"\n    {file_size_bytes} B 字节"
    
    # KiB    KB 千字节
    if not (1000 <= file_size_bytes <= 1024 * 1024) and file_size_bytes != 0:
        file_size_info += f"\n    {file_size_bytes / (1024):.4f} KiB"
        file_size_info += f"    {file_size_bytes / (1000):.4f} KB 千字节"
    
    # MiB    MB 兆字节
    if not (1000 * 1000 <= file_size_bytes <= 1024 * 1024 * 1024) and file_size_bytes >= 1000:
        file_size_info += f"\n    {file_size_bytes / (1024 ** 2):.4f} MiB"
        file_size_info += f"    {file_size_bytes / (1000 ** 2):.4f} MB 兆字节"
    
    # GiB    GB 吉字节
    if not (1000 * 1000 * 1000 <= file_size_bytes <= 1024 * 1024 * 1024 * 1024) and file_size_bytes >= 1000 * 1000:
        file_size_info += f"\n    {file_size_bytes / (1024 ** 3):.4f} GiB"
        file_size_info += f"    {file_size_bytes / (1000 ** 3):.4f} GB 吉字节"

    return file_size_info

def timestamp2str(timestamp: float) -> str:
    return datetime.datetime.fromtimestamp(timestamp).strftime(r"%Y-%m-%d %H:%M:%S")\
          + ("." + str(timestamp).split('.')[1]) if len(str(timestamp).split('.')) == 2 else ""

def get_file_infomation_str(file_path: str, return_size: bool=False) -> str:
    file_infomation: dict = get_file_infomation(file_path)
    file_infomation_str: str = ""
    file_infomation_str += f"{file_infomation['input_path']}\n"
    
    if file_infomation["code"] != 0:
        # 出错
        file_infomation_str += f"{file_infomation['msg']}\n"
    elif file_infomation["type"] == "file":
        # 文件
        file_infomation_str += f"文件名: {file_infomation['name']}\n"
        file_infomation_str += f"文件大小: {get_file_size_info(file_infomation['size'])}\n"
        file_infomation_str += f"扩展名: {file_infomation['extension']}\n"
        if file_infomation['path'] != file_infomation['absolute_path']:
            file_infomation_str += f"路径: {file_infomation['path']}\n"
        file_infomation_str += f"绝对路径: {file_infomation['absolute_path']}\n"
        file_infomation_str += f"访问时间: {timestamp2str(file_infomation['access_time'])}\n"
        file_infomation_str += f"修改时间: {timestamp2str(file_infomation['modify_time'])}\n"
        if file_infomation["create_time"]:
            file_infomation_str += f"创建时间: {timestamp2str(file_infomation['create_time'])}\n"
    elif file_infomation["type"] == "dir":
        # 目录
        file_infomation_str += f"目录名: {file_infomation['name']}\n"
        file_infomation_str += f"目录大小: {get_file_size_info(file_infomation['size'])}\n"
        if file_infomation['path'] != file_infomation['absolute_path']:
            file_infomation_str += f"路径: {file_infomation['path']}\n"
        file_infomation_str += f"绝对路径: {file_infomation['absolute_path']}\n"
        file_infomation_str += f"子文件数: {len(file_infomation['iter_path'])}\n"
        for i in range(len(file_infomation['iter_path'])):
            file_infomation_str += f"\n\n"
            file_infomation_str += get_file_infomation_str(file_infomation['iter_path'][i]['path'])
    else:
        pass
    if return_size:
        return file_infomation_str, file_infomation["size"]
    return file_infomation_str

def get_show_information() -> str:
    show_information: str = ""
    if len(sys.argv) == 1:
        show_information += f"""用法：{sys.argv[0] if ' ' not in sys.argv[0] else '"' + sys.argv[0] + '"'} [文件]...
显示文件大小信息

""" + get_file_infomation_str(sys.argv[0])
    elif len(sys.argv) == 2:
        show_information += get_file_infomation_str(sys.argv[1])
    else:
        total_file_size: int = 0
        for i in range(1, len(sys.argv)):
            information, size = get_file_infomation_str(sys.argv[i], return_size=True)
            total_file_size += size
            show_information += f"\n{''.ljust(20, '=')}\n\n"
            show_information += information
        show_information = \
            f"共输入了 {len(sys.argv) - 1} 个文件\n"\
            + f"总大小：{get_file_size_info(total_file_size)}"\
            + show_information
    return show_information

def main():
    print(get_show_information())


if __name__ == "__main__":
    main()
