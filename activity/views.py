from django.http import JsonResponse
from . import models
import os
import datetime
import hashlib
import globals
from django.views.decorators.csrf import csrf_exempt, csrf_protect


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
        "introduction": '',
        'files': [],
    }

    if request.method == 'POST':
        activity_uuid = request.POST.get('uuid')

        if activity_uuid:
            try:
                activity = models.Activity.objects.get(uuid=activity_uuid)
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

            try:
                files = models.UploadRecord.objects.filter(act_uuid=activity_uuid)
                for i in files:
                    dictionary = {}
                    dictionary['fileName'] = i.file_name
                    dictionary['fileSrc'] = i.file_path
                    data['files'].append(dictionary)
                    return JsonResponse(data)
            except:
                data['message'] = '该活动没有文件！'
                return JsonResponse(data)

        else:
            data['message'] = '活动名为空！！'
            return JsonResponse(data)


@csrf_exempt
def createActivity(request):
    data = {
        'uuid': '',
        'status': False,
        'message': '',
    }

    if request.method == 'POST':

        new_activity = models.Activity()  # 创建默认uuid
        data['uuid'] = str(new_activity.uuid)

        username = request.session['username']
        logo = request.FILES.get('logo', None)

        logo_path = globals.PATH_ACTIVITY + str(new_activity.uuid) + '/'
        isExists = os.path.exists(logo_path)

        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(logo_path)

        if logo is None:
            logo_path = logo_path + 'default.jpg'
            default = open(globals.PATH_DEFAULT, 'rb+')
            logo = open(logo_path, 'wb+')
            logo.write(default.read())
            default.close()
            logo.close()

            new_activity.logo = 'default.jpg'

        # 将文件保存到本地并改名
        else:
            new_activity.logo = logo.name
            destination = open(os.path.join(logo_path, logo.name), 'wb+')
            for chunk in logo.chunks():
                destination.write(chunk)
            destination.close()

        # 获取其他数据
        name = request.POST.get('name', None)
        activity_type = request.POST.get('type', None)
        start_time = request.POST.get('start_time', None)
        end_time = request.POST.get('end_time', None)
        location = request.POST.get('location', None)
        organizer = request.POST.get('organizer', None)
        introduction = request.POST.get('introduction', None)


        if name and start_time and end_time and location and organizer:
            # 填入数据

            new_activity.name = name
            new_activity.type = activity_type
            new_activity.status = '未发布'
            new_activity.start_time = start_time
            new_activity.end_time = end_time
            new_activity.location = location
            new_activity.organizer = organizer
            new_activity.introduction = introduction
            new_activity.username = username

            new_activity.save()

            data['message'] = '会议创建成功！'
            data['status'] = True

            return JsonResponse(data)
        else:
            data['message'] = '信息尚未完善！'
            return JsonResponse(data)

@csrf_exempt
def uploadFile(request):
    data = {
        'status': False,
        'message': '',
    }

    if request.method == 'POST':

        new_record = models.UploadRecord()

        act_uuid = request.POST.get('act_uuid', None)
        userfile = request.FILES.get('userfile', None)

        file_path = globals.PATH_ACTIVITY + str(act_uuid) + '/'
        isExists = os.path.exists(file_path)


        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(file_path)

        # 将文件保存到本地并改名
        destination = open(os.path.join(file_path, userfile.name), 'wb+')
        for chunk in userfile.chunks():
            destination.write(chunk)
        destination.close()

        file_path = file_path.strip('D:/Github/MeetingSystemFrontEnd/')
        file_path = file_path + '/'

        new_record.act_uuid = act_uuid
        new_record.file_name = userfile.name
        new_record.file_path = file_path

        new_record.save()

        data['status'] = True
        data['message'] = '上传成功！'
        return JsonResponse(data)
