
from django.http import HttpResponse
from django.http import JsonResponse
from . import models
from . import forms
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import datetime
import hashlib
import uuid
from django.core.mail import send_mail
# Create your views here.

def index(request):
    return HttpResponse("This is index")


@csrf_exempt
def login(request):
    data = {
        "status": True,
        "message":''
    }#登录信息
    if request.method == 'POST':
        #login_form = forms.UserForm(request.POST)
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
            except :
                message = '用户不存在！'
                data['message']=message
                data['status'] = False
                return JsonResponse(data)

            if user.password == password:
                #在session字典加入用户状态

                request.session['is_login']=True
<<<<<<< Updated upstream
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username
=======
               # request.session['user_uuid'] = str(user.uuid)
                request.session['username'] = user.username
>>>>>>> Stashed changes
                request.session.set_expiry(0)#关闭浏览器过期
                print(username, password)
                data['status']=True

                return JsonResponse(data)
            else:
                message = '密码不正确！'
                data['message'] = message
                data['status'] = False
                return JsonResponse(data)

        else:
            data['status']=False
            return JsonResponse(data)#若验证不通过

    #login_form=forms.UserForm    #空表单
    data['status'] = False
    return JsonResponse(data)


def check(request):#判断是否登录
    data = {
        "status": True,
    }
    if request.session.get('is_login', None):  # 不允许重复登录
        return JsonResponse(data)
    else:
        data['status'] = False
        return JsonResponse(data)


def register(request):
    pass

    return JsonResponse('')


def logout(request):
    data={
        'status':True,
        'message':''
    }
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        data['message']='您未登录'
        data['status']=False
        return JsonResponse(data)
    request.session.flush()#删除会话
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    data['message']='退出！'
    return JsonResponse(data)

def verify(request):
    data={
        'status':False,
        'message':'',
        'status_email':False,
        'status_verify':False,
    }
    if request.method=='POST':
        email=request.POST.get('email')

        if email:
            same_email_user=models.User.objects.filter(email=email)#确认邮箱是否重复
            if same_email_user:
                data['message']='此邮箱已被注册'
                data['status_email']=True
                return JsonResponse(data)
            code=get_random_str()#生成验证码
            send_mail(
                '会议系统验证码',
                "您的验证码为 "+email,
                '1040214708@qq.com',
                [email],
            )#发送邮件
            request.session.set_expiry(60)#60秒过期
            request.session['code'] =code

            if request.POST.get('code')==request.session.get('code'):
                data['status_email','status_verify']=(True,True)#注册成功
                new_user = models.User()
                new_user.email = email
                new_user.save()
                return JsonResponse(data)


# 生成验证码
def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()
