#邮件测试文件
#函数测试
import os
from django.core.mail import send_mail, EmailMultiAlternatives,EmailMessage
from email.header import make_header
import uuid
import hashlib
import globals
import filetype
from PIL import Image
import qrcode
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'PNG_backend.settings'#配置环境变量，以在manage外运行django
django.setup()
from activity import models as models_act

def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

#生成二维码图片
def make_qr(str,save):
  qr=qrcode.QRCode(
    version=4, #生成二维码尺寸的大小 1-40 1:21*21（21+(n-1)*4）
    error_correction=qrcode.constants.ERROR_CORRECT_M, #L:7% M:15% Q:25% H:30%
    box_size=10, #每个格子的像素大小
    border=2, #边框的格子宽度大小
  )
  qr.add_data(str)
  qr.make(fit=True)
  image=qr.make_image()
  image.save(save)

def file_mail():
    '''发送附件'''
    email = EmailMessage(
        'Hello',
        'Body goes here',
        '1040214708@qq.com',   # 发件人
        ['213170713@seu.edu.cn'],   # 收件人

        #reply_to=['another@example.com'],  # “回复”标题中使用的收件人地址列表或元组
        #headers={'Message-ID': 'foo'},
    )

    # templates目录下有个a.png的图片
    filepath='D:/FRONTEND/MeetingSystemFrontEnd/user/227af7b8-c7fc-11e9-ba32-887873aca633/qrcode/bbf0b026-cd23-11e9-ba17-a146354fd931.png'

    email.attach_file(filepath, mimetype=None)
    email.send()

def send_mail_with_file(title,contents,target,uuid_user,uuid_act):
    '''发送附件'''
    email = EmailMessage(
        title,
        contents,
        '1040214708@qq.com',   # 发件人
        [target],   # 收件人
    )

    filepath='D:/FRONTEND/MeetingSystemFrontEnd/user/%s/qrcode/%s.png'%(uuid_user,uuid_act)
    email.attach_file(filepath, mimetype=None)
    email.send()


if __name__ == '__main__':
    #uuid = uuid.uuid1()

    #print(uuid)
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

    # save_path = 'C:/Users/hp/Pictures/theqrcode.png'  # 生成后的保存文件
    # str ='这是一个二维码生成的测试'
    # make_qr(str,save_path)

    # try:
    #     activity=models_act.Activity.objects.filter(status_publish='published').order_by('start_time')[:2]
    #
    # except:
    #     print('get()异常')
    # else:
    #     print(activity)

    #带附件的邮件
    title='通知'
    contents = '您已成功报名参加活动 %s !' % '国庆阅兵'
    uuid_user='227af7b8-c7fc-11e9-ba32-887873aca633'
    uuid_act='bbf0b026-cd23-11e9-ba17-a146354fd931'
    target='213170713@qq.com'
    send_mail_with_file(title,contents,target,uuid_user,uuid_act)





