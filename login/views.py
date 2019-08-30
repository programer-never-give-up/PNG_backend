from django.http import HttpResponse
from django.http import JsonResponse
from . import models
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import datetime
import hashlib
import uuid
from django.core.mail import send_mail
from django.core.files.storage import default_storage
import globals
from django.core.files.base import ContentFile
import os
import filetype


# Create your views here.

def index(request):
    return HttpResponse("This is index")


@csrf_exempt
def login(request):
    data = {
        "status": True,
        "message": ''
    }  # 登录信息
    if request.method == 'POST':
        # login_form = forms.UserForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        message = '请检查填写的内容！'
        if username.strip() and password:
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            # #if login_form.is_valid():
            #     username = login_form.cleaned_data.get('username')#获取表单值
            #     password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(username=username)
            except:
                message = '用户不存在！'
                data['message'] = message
                data['status'] = False
                return JsonResponse(data)

            if user.password == password:
                # 在session字典加入用户状态

                request.session['is_login'] = True
                # request.session['user_uuid'] = str(user.uuid)
                request.session['username'] = user.username

                request.session['uuid']=str(user.uuid)
                request.session.set_expiry(0)#关闭浏览器过期



                print(username, password)
                data['status'] = True
                data['message'] = '登录成功！'
                return JsonResponse(data)
        else:
            message = '密码不正确！'
            data['message'] = message
            data['status'] = False
            return JsonResponse(data)

    else:
        data['status'] = False
        return JsonResponse(data)  # 若验证不通过


    # login_form=forms.UserForm    #空表单
    data['status'] = False
    data['message'] = '空表单'
    return JsonResponse(data)


@csrf_exempt
def check(request):  # 判断是否登录
    data = {
        "status": True,
        'message': ''
    }
    if request.session.get('is_login', None):  # 不允许重复登录
        data['message'] = '您已登录！'
        return JsonResponse(data)
    else:
        data['status'] = False
        data['message'] = "您还未登录！"
        return JsonResponse(data)


@csrf_exempt
def logout(request):
    data = {
        'status': True,
        'message': ''
    }
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        data['message'] = '您未登录！'
        data['status'] = False
        return JsonResponse(data)
    request.session.flush()  # 删除会话
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    data['message'] = '退出！'
    return JsonResponse(data)


@csrf_exempt
def sendMail(request):
    data = {
        'isSended': False,
        'status_email': False,  # 邮箱的注册状态，False为未注册
        'message': '',
    }
    if request.method == 'POST':
        email = request.POST.get('email')

        if email:
            same_email_user = models.User.objects.filter(email=email)  # 确认邮箱是否重复
            if same_email_user:
                data['message'] = '此邮箱已被注册！'
                data['status_email'] = True
                return JsonResponse(data)
            code = get_random_str()  # 生成验证码
            send_mail(
                '会议系统验证码',
                "您的验证码为 " + code,
                '1040214708@qq.com',
                [email],
            )  # 发送邮件
            request.session['code'] = code
            request.session.set_expiry(120)  # 120秒过期
            data['isSended'] = True
            data['message'] = '邮件已发送！'
            return JsonResponse(data)
        else:
            data['message']='邮箱为空！'
            return JsonResponse(data)

@csrf_exempt
def checkMail(request):
    data = {
        'status_check': False,  # 是否验证成功
        'message': '',
    }
    if request.method == 'POST':
        code = request.POST.get('code')  # 获取用户输入的验证码
        if code:
            if code == request.session.get('code'):
                data['status_check'] = True
                data['message'] = '验证成功！'
                return JsonResponse(data)
            else:
                data['status_check'] = False
                data['message'] = '验证失败！'
                return JsonResponse(data)


@csrf_exempt
def register(request):
    data = {
        'status': False,  # 注册状态，true为数据填入成功
        'status_username': False,  # False为用户名不重复
        'message': '',
    }

    if request.method == 'POST':
        username = request.POST.get('username', None)
        if username:
            same_name_user = models.User.objects.filter(username=username)  # 确认用户名是否重复
            if same_name_user:
                data['message'] = '此用户名已被注册！'
                data['status_username'] = True
                return JsonResponse(data)
        # 开始注册
        new_user = models.User()  # 创建new_user,默认创建uuid

        avatar = request.FILES.get('avatar', None)
        #新建avatar路径
        path = globals.PATH_USER + str(new_user.uuid) + '/'
        isExists = os.path.exists(path)
        # 判断路径是否存在
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
        # 如果未上传avatar，设置默认avatar，default.jpg
        if avatar is None:
            new_user.avatar = path.strip('D:/FRONTEND/MeetingSystemFrontEnd/') + '/default.jpg'
            # 写入avatar文件
            path = path + 'default.jpg'
            default = open(globals.PATH_DEFAULT, 'rb+')
            avatar = open(path, 'wb+')
            avatar.write(default.read())
            default.close()
            avatar.close()
        # 如果上传了avatar，将avatar保存到本地
        else:
            new_user.avatar = path.strip('D:/FRONTEND/MeetingSystemFrontEnd/') + '/' + avatar.name

            destination = open(os.path.join(path, avatar.name), 'wb+')
            for chunk in avatar.chunks():
                destination.write(chunk)
            destination.close()

        # 获取其他数据
        type = request.POST.get('type', None)
        address = request.POST.get('address', None)
        profession = request.POST.get('profession', None)
        company = request.POST.get('company', None)
        email = request.POST.get('email', None)
        gender = request.POST.get('gender', None)

        phone_number = request.POST.get('phone_number', None)
        # introduction = request.POST.get('introduction', None)
        password = request.POST.get('password', None)
        # 填入数据
        new_user.username = username
        new_user.password = password
        new_user.type = type
        new_user.address = address
        new_user.profession = profession
        new_user.company = company
        new_user.email = email
        new_user.gender = gender
        new_user.phone_number = phone_number
        # new_user.introduction=introduction
        new_user.save()
        data['status'] = True
        data['message'] = '注册成功！'
        return JsonResponse(data)
    return JsonResponse(data)
    # 内容： request{ avatar, username, password, phoneNumber, company, profession, address, introduction}


def findPassword(request):
    data = {
        'message': '',
        'status': False,  # 修改密码状态 成功or失败
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        try:
            user = models.User.objects.filter(username=username)
        except:
            message = '用户不存在！'
            data['message'] = message
            return JsonResponse(data)
        if new_password:

            user.password = new_password
            user.update(password=new_password)
            data['status'] = True
            data['message'] = '修改密码成功！请用新密码登陆！'
            return JsonResponse(data)
        else:
            data['message'] = '新密码不能为空！'
            return JsonResponse(data)

    data['message'] = '空表单'
    return JsonResponse(data)


# 生成验证码
def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()
