#邮件测试文件
import os
from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE'] = 'PNG_backend.settings'

if __name__ == '__main__':

    send_mail(
        '来自Inderway的测试邮件',
        '此为邮件正文',
        '1040214708@qq.com',
        ['213170713@seu.edu.cn'],
    )