from django.http import JsonResponse
from . import models
import uuid
import os
import datetime
import hashlib
import globals
from django.views.decorators.csrf import csrf_exempt,csrf_protect
# Create your views here.

@csrf_exempt
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
        activity_uuid = request.POST.get('uuid')
        if activity_uuid:
            try:
                activity= models.Activity.objects.get(uuid=activity_uuid)
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
            data['message'] = '活动名为空！！'
            return JsonResponse(data)

@csrf_exempt
def createActivity(request):
    data = {
        "message": '',
    }

    if request.method == 'POST':

        new_activity = models.Activity()#创建默认uuid

        logo = request.FILES.get('logo', None)
        # 将文件保存到本地并改名
        destination = open(os.path.join(globals.PATH_LOGO, logo.name), 'wb+')
        for chunk in logo.chunks():
            destination.write(chunk)
        destination.close()
        # 改名
        path_logo = os.path.join(globals.PATH_LOGO, logo.name)
        extension = '.'+logo.name.split('.')[-1]
        new_name = str(new_activity.uuid) + extension
        new_file = os.path.join(globals.PATH_LOGO,new_name)
        os.rename(path_logo, new_file)

        # 获取其他数据
        name = request.POST.get('name', None)
        activity_type = request.POST.get('type',None)
        start_time = request.POST.get('start_time', None)
        end_time = request.POST.get('end_time', None)
        location = request.POST.get('location', None)
        organizer = request.POST.get('organizer', None)
        introduction = request.POST.get('introduction', None)

        if name and start_time and end_time and location and organizer:
            # 填入数据
            new_activity.logo = new_name

            new_activity.name = name
            new_activity.type = activity_type
            new_activity.status = '未发布'
            new_activity.start_time = start_time
            new_activity.end_time = end_time
            new_activity.location = location
            new_activity.organizer = organizer
            new_activity.introduction = introduction

            new_activity.save()

            data['message'] = '会议创建成功！'
            return JsonResponse(data)
        else:
            data['message'] = '信息尚未完善！'
            return JsonResponse(data)
