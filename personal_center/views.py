from login import models as models_login
from activity import models as models_activity
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import JsonResponse
import globals
import os
import uuid
from . import  models
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
                print('取得用户')
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            data['username'] = user.username
            data['avatar']=user.avatar
            data['gender']=user.gender
            data['email']=user.email
            data['phone_number']=user.phone_number
            print(user.phone_number)
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
        #print('收到post')
        username = request.session['username']
        if username:
            try:
                user= models_login.User.objects.filter(username=username)
                #print('获得user')
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
            #print(phone_number)
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
            if address:
                user.address=address
                user.update(address=address)
            if profession:
                user.profession=profession
                user.update(profession=profession)
            if company:
                user.company=company
                user.update(company=company)
            if gender:
                user.gender=gender
                user.update(gender=gender)
            if phone_number:
                user.phone_number=phone_number
                print('第二次电话'+user.phone_number)
                for i in range(len(user)):
                    print(user[i].uuid)
                user.update(phone_number=phone_number)
            if introduction:
                user.introduction=introduction
                user.update(introduction=introduction)
            if password:
                user.password=password
                user.update(password=password)
            #user.save()


            data['message']='修改成功！'
            return JsonResponse(data)

        else:
            data['message']='未接收到用户名！'

    else:
        data['message']='无数据！'
        return JsonResponse(data)

@csrf_exempt
def history_attend(request):
    data={
        'list_activity':[],#字典嵌套列表再嵌套字典
        'message':'',
    }
    if request.method=='POST':
        print('收到post')
        uuid_user=uuid.UUID(request.session['uuid'])#session中的string转uuid
        if uuid_user:
            try:
                record= models.On_site.objects.filter(uuid_user=uuid_user)
                #筛选出这个uuid对应的所有条目
                #print('获得user')
            except:
                data['message'] = '不存在的记录'
                return JsonResponse(data)
            activity={
                'uuid_act':'',
                'name_act':'',
                'start_time':'',
                'end_time':'',
            }
            for entry in range(len(record)):
                activity['uuid_act']=str(record[entry].uuid_act)
                #进入activity表根据uuid获取会议名
                try:
                    tmp_activity=models_activity.Activity.objects.get(uuid=record[entry].uuid_act)
                except:
                    data['message']='无此活动！'
                    return JsonResponse(data)
                activity['name_act']=tmp_activity.name
                activity['start_time']=tmp_activity.start_time
                activity['end_time']=tmp_activity.end_time
                #将字典activity加入列表
                data['list_activity'].append(activity)
            return JsonResponse(data)
        else:
            data['message']='无uuid!'
            return JsonResponse(data)
    else:
        data['message']='空表单'
        return JsonResponse(data)


@csrf_exempt
def history_organize(request):
    data={
        'list_activity': [],  # 字典嵌套列表再嵌套字典
        'message': '',
    }
    if request.method=='POST':
        username=request.session['username']#取出session中username
        if username:
            try:
                record= models_activity.Activity.objects.filter(username=username)
                #筛选出这个username创建的所有记录
            except:
                data['message'] = '不存在的记录'
                return JsonResponse(data)
            activity={
                'uuid_act':'',
                'name_act':'',
                'start_time': '',
                'end_time': '',
            }
            for entry in range(len(record)):
                activity['uuid_act']=str(record[entry].uuid)
                activity['name_act']=record[entry].name
                activity['start_time']=record[entry].start_time
                activity['end_time']=record[entry].end_time
                #将字典activity加入列表
                data['list_activity'].append(activity)
            return JsonResponse(data)
        else:
            data['message']='无username!'
            return JsonResponse(data)
    else:
        data['message']='空表单'
        return JsonResponse(data)
