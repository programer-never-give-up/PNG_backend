#邮件测试文件
#函数测试
import os
from django.core.mail import send_mail
import uuid
import hashlib
import globals
import filetype
os.environ['DJANGO_SETTINGS_MODULE'] = 'PNG_backend.settings'

def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

if __name__ == '__main__':
    uuid = uuid.uuid1()

    print(uuid)
    # send_mail(
    #     '来自Inderway的测试邮件',
    #     '此为邮件正文',
    #     '1040214708@qq.com',
    #     ['213170713@seu.edu.cn'],
    # )

    # avatar = os.path.join(globals.PATH_AVATAR, "PNG.png")
    #
    # #print(avatar)
    # type=filetype.guess(avatar)
    #print(type.extension)
    # # 分离文件名和目录
    # dirname, filename = os.path.split(avatar)
    # # print(dirname, filename)
    #
    # # 改名
    # new_file = os.path.join(dirname,str(uuid)+'.'+str(type.extension))
    # # print(new_file)
    # os.rename(avatar, new_file)


