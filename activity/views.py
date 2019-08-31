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
        'message': '',
        'name': '',
        'type': '',
        'status_process': '',
        'status_publish': '',
        'start_time': '',
        'end_time': '',
        'location': '',
        'organizer': '',
        'logo': '',
        'introduction': '',
        'files': [],
    }

    if request.method == 'GET':
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
            data['status_process'] = activity.status_process
            data['status_publish'] = activity.status_publish
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
        'status': False,  # 是否成功创建活动
        'message': '',
    }

    if request.method == 'POST':

        new_activity = models.Activity()  # 创建活动，默认uuid
        data['uuid'] = str(new_activity.uuid)
        # 获取活动创建者用户名
        username = request.session['username']
        # 获取活动logo
        logo = request.FILES.get('logo', None)
        # 新建logo保存路径
        logo_path = globals.PATH_ACTIVITY + str(new_activity.uuid) + '/'
        isExists = os.path.exists(logo_path)

        # 判断路径是否存在
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(logo_path)
        # 如果未上传logo，设置默认logo，default.jpg
        if logo is None:
            new_activity.logo = logo_path.strip('D:/FRONTEND/MeetingSystemFrontEnd/')+'/default.jpg'
            # 写入logo文件
            logo_path = logo_path + 'default.jpg'
            default = open(globals.PATH_DEFAULT, 'rb+')
            logo = open(logo_path, 'wb+')
            logo.write(default.read())
            default.close()
            logo.close()

        # 如果上传了logo，将logo保存到本地
        else:
            new_activity.logo = logo_path.strip('D:/FRONTEND/MeetingSystemFrontEnd/') + '/' + logo.name

            destination = open(os.path.join(logo_path, logo.name), 'wb+')
            for chunk in logo.chunks():
                destination.write(chunk)
            destination.close()

        # 获取其他数据
        name = request.POST.get('name', None)
        activity_type = request.POST.get('type', None)
        start_time = request.POST.get('start_time', None)
        start_time = start_time.replace('T', ' ')
        end_time = request.POST.get('end_time', None)
        end_time = end_time.replace('T', ' ')
        location = request.POST.get('location', None)
        organizer = request.POST.get('organizer', None)
        introduction = request.POST.get('introduction', None)

        # 如果有数据未填写，数据库中不会保存会议记录
        if name and start_time and end_time and location and organizer:
            # 填入数据

            new_activity.name = name
            new_activity.type = activity_type
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
        'status': False,  # 是否成功上传文件
        'message': '',
    }

    if request.method == 'POST':
        # 新建一条文件记录
        new_record = models.UploadRecord()
        # 获取活动id、要上传的文件
        act_uuid = request.POST.get('act_uuid', None)
        userfile = request.FILES.get('userfile', None)
        # 新建文件保存路径
        file_path = globals.PATH_ACTIVITY + str(act_uuid) + '/'
        isExists = os.path.exists(file_path)
        # 判断路径是否存在
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(file_path)

        # 将文件保存到本地
        destination = open(os.path.join(file_path, userfile.name), 'wb+')
        for chunk in userfile.chunks():
            destination.write(chunk)
        destination.close()
        # 文件前端下载路径
        file_path = file_path.strip('D:/FRONTEND/MeetingSystemFrontEnd/')
        file_path = file_path + os.path.sep
        # 新建文件记录的相关属性
        new_record.act_uuid = act_uuid
        new_record.file_name = userfile.name
        new_record.file_path = file_path
        # 保存
        new_record.save()

        data['status'] = True
        data['message'] = '上传成功！'
        return JsonResponse(data)

@csrf_exempt
def pageDisplay(request):
    data = {
        'pageNum': 0,  # 总页数
        'activities': [],  # 活动列表
        'message': '',
    }
    print('fsdfds')

    if request.method == 'GET':
        username = request.session['username']
        print(username)
        acts = models.Activity.objects.filter(username=username)

        btn_type = request.GET.get('btn-type')
        page_id = int(request.GET.get('page-id'))
        per_page = int(request.GET.get('per-page'))
        print(btn_type)
        print(per_page)
        print(page_id)

        if btn_type == 'management-unpublished':
            count = 0
            for act in acts:
                if act.status_publish == 'unpublished':
                    if (page_id - 1) * per_page <= count < per_page * page_id:
                        dictionary = {}
                        dictionary['logoSrc'] = act.logo
                        dictionary['activityName'] = act.name
                        dictionary['location'] = act.location
                        dictionary['startTime'] = act.start_time
                        dictionary['endTime'] = act.end_time
                        dictionary['id'] = act.uuid
                        data['activities'].append(dictionary)

                        print(dictionary['activityName'])
                    print(count)
                    count += 1
            import math
            print(count / per_page)
            data['pageNum'] = math.ceil(count / per_page)
            print(data['pageNum'])
            if data['pageNum'] == 0:
                data['message'] = '不存在未发布的活动！'
            else:
                data['message'] = '成功！'
            print(data['message'])
            return JsonResponse(data)

        elif btn_type == 'management-published':
            count = 0
            for act in acts:
                if act.status_publish == 'published':
                    if (page_id - 1) * per_page <= count < per_page * page_id:
                        dictionary = {}
                        dictionary['logoSrc'] = act.logo
                        dictionary['activityName'] = act.name
                        dictionary['location'] = act.location
                        dictionary['startTime'] = act.start_time
                        dictionary['endTime'] = act.end_time
                        dictionary['id'] = act.uuid
                        data['activities'].append(dictionary)
                    count += 1
            data['pageNum'] = int(count / per_page) + 1
            if data['pageNum'] == 0:
                data['message'] = '不存在已发布的活动！'
            else:
                data['message'] = '成功！'
            return JsonResponse(data)

        elif btn_type == 'management-processing':
            count = 0
            for act in acts:
                if act.status_process == 'processing':
                    if (page_id - 1) * per_page <= count < per_page * page_id:
                        dictionary = {}
                        dictionary['logoSrc'] = act.logo
                        dictionary['activityName'] = act.name
                        dictionary['location'] = act.location
                        dictionary['startTime'] = act.start_time
                        dictionary['endTime'] = act.end_time
                        dictionary['id'] = act.uuid
                        data['activities'].append(dictionary)
                    count += 1
            data['pageNum'] = int(count / per_page) + 1
            if data['pageNum'] == 0:
                data['message'] = '不存在进行中的活动！'
            else:
                data['message'] = '成功！'
            return JsonResponse(data)

        elif btn_type == 'management-finished':
            count = 0
            for act in acts:
                if act.status_process == 'finished':
                    if (page_id - 1) * per_page <= count < per_page * page_id:
                        dictionary = {}
                        dictionary['logoSrc'] = act.logo
                        dictionary['activityName'] = act.name
                        dictionary['location'] = act.location
                        dictionary['startTime'] = act.start_time
                        dictionary['endTime'] = act.end_time
                        dictionary['id'] = act.uuid
                        data['activities'].append(dictionary)
                    count += 1
            data['pageNum'] = int(count / per_page) + 1
            if data['pageNum'] == 0:
                data['message'] = '不存在已完成的会议！'
            else:
                data['message'] = '成功！'
            return JsonResponse(data)

        elif btn_type == 'management-to_be_audited':
            count = 0
            for act in acts:
                if act.status_publish == 'to_be_audited':
                    if (page_id - 1) * per_page <= count < per_page * page_id:
                        dictionary = {}
                        dictionary['logoSrc'] = act.logo
                        dictionary['activityName'] = act.name
                        dictionary['location'] = act.location
                        dictionary['startTime'] = act.start_time
                        dictionary['endTime'] = act.end_time
                        dictionary['id'] = act.uuid
                        data['activities'].append(dictionary)
                    count += 1
            data['pageNum'] = int(count / per_page) + 1
            if data['pageNum'] == 0:
                data['message'] = '不存在待审核的会议！'
            else:
                data['message'] = '成功！'
            return JsonResponse(data)

        elif btn_type == 'my-not_start':
            return JsonResponse(data)
        elif btn_type == 'my-processing':
            return JsonResponse(data)
        elif btn_type == 'my-finished':
            return JsonResponse(data)
        elif btn_type == 'fav-not_start':
            return JsonResponse(data)
        elif btn_type == 'fav-processing':
            return JsonResponse(data)
        elif btn_type == 'fav-finished':
            return JsonResponse(data)

        else:
            data['message'] = '不存在的会议状态！'
            return JsonResponse(data)
    else:
        data['message'] = '空表单'
        return JsonResponse(data)
