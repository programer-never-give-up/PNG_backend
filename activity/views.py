from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from . import models
import uuid
import os
import datetime
import hashlib

# Create your views here.

def showActivity(request):
    data = {
        "message": '',
        "name": '',
        "type": '',
        "status": '',
        "start_time": '',
        "end_time": '',
        "location": '',
        "organizer": '',
        "logo": '',
        "introduction": ''
    }
    if request.method == 'POST':
        activity_id = request.POST.get('id')
        if activity_id:
            try:
                activity = models.Activity.objects.get(id=activity_id)
            except:
                message = '不存在的活动！'
                data['message'] = message
                return JsonResponse(data)

            data['name'] = activity.name
            data['type'] = activity.type
            data['status'] = activity.status
            data['start_time'] = activity.start_time
            data['end_time'] = activity.end_time
            data['location'] = activity.location
            data['organizer'] = activity.organizer
            data['logo'] = activity.logo
            data['introduction'] = activity.introduction

            return JsonResponse(data)

        else:
            data['message'] = '不存在的活动号！'
            return JsonResponse(data)


def createActivity(request):
    data = {
        "message": '',
    }

    if request.method == 'POST':
        avatar = request.FILES.get('avatar', None)
        import uuid
        new_uuid = uuid.uuid1()
        # 将文件保存到本地并改名
        destination = open(os.path.join(globals.PATH_AVATAR, avatar.name), 'wb+')
        for chunk in avatar.chunks():
            destination.write(chunk)
        destination.close()
        # 改名
        path_avatar = os.path.join(globals.PATH_AVATAR, avatar.name)
        extension = '.'+avatar.name.split('.')[-1]
        new_name = str(uuid) + extension
        new_file = os.path.join(globals.PATH_AVATAR,new_name)
        os.rename(path_avatar, new_file)

        # 获取其他数据
        name = request.POST.get('name', None)
        activity_type = request.POST.get('name',None)
        start_time = request.POST.get('start_time', None)
        end_time = request.POST.get('end_time', None)
        location = request.POST.get('location', None)
        organizer = request.POST.get('organizer', None)
        introduction = request.POST.get('introduction', None)

        if name and start_time and end_time and location and organizer:
            # 填入数据
            new_activity = models.Activity()

            new_activity.logo = new_name
            new_activity.uuid = new_uuid
            new_activity.name = name
            new_activity.type = activity_type
            new_activity.status = '未发布'
            new_activity.start_time = start_time
            new_activity.end_time = end_time
            new_activity.location = location
            new_activity.organizer = organizer
            new_activity.introduction = introduction

            new_activity.save()
            data['status'] = True
            data['message'] = '注册成功！'
            return JsonResponse(data)
        else:
            data['message'] = '信息尚未完善！'
            return JsonResponse(data)
