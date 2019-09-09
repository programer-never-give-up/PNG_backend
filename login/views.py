from django.http import HttpResponse
from django.http import JsonResponse
from . import models
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import hashlib
import uuid
from django.core.mail import send_mail
import globals
import os
import random



# Create your views here.

def index(request):
    return HttpResponse("This is index")


@csrf_exempt
def login(request):
    data = {
        "status": True,
        'isAdmin':False,#判断是否为管理员登录
        "message": ''
    }  # 登录信息
    if request.method == 'POST':
        # login_form = forms.UserForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        message = '请检查填写的内容！'
        if username and password:
            #如果用户为管理员
            if username=='admin':
                try:
                    admin=models.Admin.objects.get(username='admin')
                    print('取得admin')
                except:
                    data['message']='管理员不存在'
                    data['status']='False'
                    print(data['message'])
                    return JsonResponse(data)
                if admin.password==password:
                    request.session['is_login'] = True
                    # request.session['user_uuid'] = str(user.uuid)
                    request.session['username'] = admin.username

                    request.session['uuid'] = 'admin'
                    request.session['isAdmin']=True
                    request.session.set_expiry(0)  # 关闭浏览器过期

                    print(username, password)
                    data['status'] = True
                    data['message'] = '管理员登录成功！'
                    data['isAdmin']=True
                    return JsonResponse(data)
                else:
                    message = '密码不正确！'
                    data['message'] = message
                    data['status'] = False
                    return JsonResponse(data)
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

                request.session['uuid']=user.uuid
                request.session.set_expiry(0)#关闭浏览器过期



                print(username, password)
                data['status'] = True
                data['message'] = '登录成功！'
                return JsonResponse(data)
        else:
            message = '用户名或密码为空！'
            data['message'] = message
            data['status'] = False
            return JsonResponse(data)

    else:
        data['status'] = False
        data['message']='未获得post'
        return JsonResponse(data)  # 若验证不通过



@csrf_exempt
def check(request):  # 判断是否登录
    data = {
        "status": True,
        'message': '',
        'type':0,#个人用户为0,企业用户为1，管理员为2
    }
    print('调用了check')
    if request.session.get('is_login', None):  # 不允许重复登录
        username=request.session.get('username',None)
        print('username')
        if username:
            if request.session.get('isAdmin',None)==True:
                data['message'] = '您已登录！管理用户！'
                data['type']=2
                request.session['type'] = 2
                print(data)
                return JsonResponse(data)
            else:
                try:
                    user=models.User.objects.get(username=username)
                except:
                    data['message']='未找到user'
                    print(data)
                    return JsonResponse(data)
                if user.type=='企业':
                    data['type']=1
                    data['message'] = '您已登录！企业用户！'
                    request.session['type']=1
                    print(data)
                    return JsonResponse(data)

                else:
                    data['message'] = '您已登录！个人用户！'
                    request.session['type']=0
                    print(data)
                    return JsonResponse(data)

        else:
            data['message']='session中无数据'
            print(data)
            return JsonResponse(data)
    else:
        data['status'] = False
        data['message'] = "您还未登录！"
        print(data)
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
            try:
                send_mail(
                    '会议系统验证码',
                    "您的验证码为 " + code,
                    '1040214708@qq.com',
                    [email],
                )  # 发送邮件
            except:
                data['message']='无效的邮箱！'
                return JsonResponse(data)
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
            if request.session.get('code',None):
                if code == request.session.get('code',None):
                    data['status_check'] = True
                    data['message'] = '验证成功！'
                    return JsonResponse(data)
                else:
                    data['status_check'] = False
                    data['message'] = '验证失败！'
                    return JsonResponse(data)
            else:
                data['message']='session无数据'
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
            new_user.avatar =  'default.jpg'
            # 写入avatar文件
            path = path + 'default.jpg'
            default = open(globals.PATH_DEFAULT, 'rb+')
            avatar = open(path, 'wb+')
            avatar.write(default.read())
            default.close()
            avatar.close()
        # 如果上传了avatar，将avatar保存到本地并
        else:
            new_user.avatar = 'user/'+str(new_user.uuid)+ '/' + avatar.name

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
    list_num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    list_str = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 's', 't', 'x', 'y',
                'z']
    veri_str = random.sample(list_str, 2)
    veri_num = random.sample(list_num, 2)
    veri_out = random.sample(veri_num + veri_str, 4)
    veri_res = str(veri_out[0]) + str(veri_out[1]) + str(veri_out[2]) + str(veri_out[3])
    return veri_res

