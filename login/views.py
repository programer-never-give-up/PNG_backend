from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from . import forms
# Create your views here.

def index(request):
    pass
    return render(request, 'login/index.html')



def login(request):
    if request.session.get('is_login',None):#不允许重复登录
        return redirect('/index/')
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
                user = models.User.objects.get(name=username)
            except :
                message = '用户不存在！'
                return render(request, 'login/login.html', {'message':message})#返回当前所有的本地变量字典

            if user.password == password:
                #在session字典加入用户状态

                request.session['is_login']=True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session.set_expiry(10)#十秒过期，无效
                print(username, password)
                return redirect('/index/')
            else:
                message = '密码不正确！'
                return render(request, 'login/login.html',{'message':message})
        else:
            return render(request, 'login/login.html', {'message':message})#若验证不通过

    #login_form=forms.UserForm    #空表单
    return render(request, 'login/login.html')


def register(request):
    pass
    return render(request, 'login/register.html')


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()#删除会话
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/")

def verify(request):
    pass
    return render(request, 'login/verify.html')