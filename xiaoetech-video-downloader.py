import re
import threading
import time

import requests
from Crypto.Cipher import AES

# ------------------------------------配置区----------------------------------------
m3u8_File = r'C:\Users\Administrator\Desktop\***.m3u8'  # m3u8源文件

key_url = "https://app.xiaoe-tech.com/xe.basic-platform.material-center.distribute.vod.pri.get/1.0.0?app_id=***&mid=***&urld=***"  # 密钥获取链接

params = {"sign": "***",
          "t": "***", "us": "***"}  # ts服务器请求附加参数

ts_url = "https://encrypt-k-vod.xet.tech/***/***/drm/"  # ts文件服务器路径

user_id = "***"  # 用户ID

thread_num = 8  # 线程池最大量

header = {
    "Accept": "*/*",
    "Host": "encryptk-vod.xet.tech",
    "Origin": "https://***.h5.xiaoeknow.com",
    "Referer": "https://***.h5.xiaoeknow.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
}

video_output_dir = r"C:\Users\Administartor\Desktop\video"  # 视频输出目录
# ---------------------------------------------------------------------------------


def get_key_from_url(url: str, userid: str) -> str:
    # url拼接uid参数
    url += f'&uid={userid}'
    # 发送get请求
    rsp = requests.get(url=url)
    rsp_data = rsp.content
    if len(rsp_data) == 16:
        userid_bytes = bytes(userid.encode(encoding='utf-8'))
        result_list = []
        for index in range(0, len(rsp_data)):
            result_list.append(
                rsp_data[index] ^ userid_bytes[index])
        # return base64.b64encode(bytes(result_list)).decode()
        return bytes(result_list)
    else:
        print(f"获取异常，请求返回值：{rsp.text}")
        return ''


def doTask(url, i):
    content = requests.get(url, params, timeout=30)
    cryptor = AES.new(get_key_from_url(key_url, user_id), AES.MODE_CBC)
    open(video_output_dir+'\%s.ts' %
         ('%05d' % i), 'wb').write(cryptor.decrypt(content.content))


def startDownloadVideo():
    threading_list = []  # 线程池
    with open(m3u8_File, 'r', encoding='utf-8') as f:
        ts_files_list = re.findall(re.compile(
            "\nv.f421220_0.ts?(\S*)"), f.read())
        print(f"共发现{len(ts_files_list)}条片段")
        i = 1
        start = time.time()
        for ts_file in ts_files_list:
            url = ts_url + "v.f421220_0.ts" + ts_file
            url = url.rstrip()
            t = threading.Thread(target=doTask, args=(url, i))  # 创建线程
            threading_list.append(t)  # 加入线程池
            t.start()  # 启动线程
            i = i+1
            print(f"\rdownloading... {i}/{len(ts_files_list)}", end="")
            while len(threading_list) > thread_num:  # 线程池满，开始等待

                threading_list = [x for x in threading_list if x.is_alive()]
                time.sleep(1)
        sec = int(time.time() - start)
        t_m, t_s = divmod(sec, 60)
        t_h, t_m = divmod(t_m, 60)
        r_t = str(int(t_h)).zfill(2)+":"+str(int(t_m)
                                             ).zfill(2)+":"+str(int(t_s)).zfill(2)
        print("\n总耗时: "+r_t)


if __name__ == "__main__":
    startDownloadVideo()
