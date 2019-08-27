from login import models as models_login
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import JsonResponse
import globals
import os

# Create your views here.


@csrf_exempt
def showInfo(request):
    data={
       "avatar":'',
       'username':'',
       'gender':'',
       'email':'',
       'phone_number':'',
       'type':'',
       'address':'',
       'company':'',
       'profession':'',
       'introduction':'',
       'message':'',
    }
    if request.method=='GET':
        username=request.session['username']
        if username:
            try:
                user= models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            data['avatar']=user.avatar
            data['gender']=user.gender
            data['email']=user.email
            data['phone_number']=user.phone_number
            data['type']=user.type
            data['address']=user.address
            data['company']=user.company
            data['profession']=user.profession
            data['introduction']=user.introduction
            data['message']='提取信息完毕！'
            return JsonResponse(data)
        else:
            data['message']='未接收到用户名'
            return JsonResponse(data)
    else:
        data['message']='无数据!'
        return JsonResponse(data)

@csrf_exempt
def editInfo(request):
    data={
        'message':'',
    }
    if request.method=='POST':
        username = request.session['username']
        if username:
            try:
                user= models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            avatar = request.FILES.get('avatar', None)
            type = request.POST.get('type', None)
            address = request.POST.get('address', None)
            profession = request.POST.get('profession', None)
            company = request.POST.get('company', None)
            gender = request.POST.get('gender', None)
            phone_number = request.POST.get('phone_number', None)
            introduction = request.POST.get('introduction', None)
            password = request.POST.get('password', None)

            if avatar:
                # 将文件保存到本地并改名
                destination = open(os.path.join(globals.PATH_AVATAR, avatar.name), 'wb+')
                for chunk in avatar.chunks():
                    destination.write(chunk)
                destination.close()
                # 改名
                path_avatar = os.path.join(globals.PATH_AVATAR, avatar.name)
                extension = '.' + avatar.name.split('.')[-1]
                new_name = str(user.uuid) + extension
                new_file = os.path.join(globals.PATH_AVATAR, new_name)
                os.rename(path_avatar, new_file)
            if type:
                user.type=type
            if address:
                user.address=address
            if profession:
                user.profession=profession
            if company:
                user.company=company
            if gender:
                user.gender=gender
            if phone_number:
                user.phone_number=phone_number
            if introduction:
                user.introduction=introduction
            if password:
                user.password=password
            data['message']='修改成功！'
            return JsonResponse('data')

        else:
            data['message']='未接收到用户名！'

    else:
        data['message']='无数据！'
        return JsonResponse(data)