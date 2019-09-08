from django.http import JsonResponse
from . import models
import os
import datetime
import hashlib
import globals
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from yw import models as yw_models
from login import models as login_models
from yw import views as yw_views

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
        'num': 0,
        'files': [],
        'roleType': 0,
    }

    if request.method == 'GET':
        activity_uuid = request.GET.get('uuid')
        if activity_uuid:
            try:
                activity = models.Activity.objects.get(uuid=activity_uuid)

                if 'username' in request.session.keys():
                    viewer = request.session['username']
                else:
                    viewer = None

                if viewer and activity.username == viewer:
                    data['roleType'] = 2
                elif viewer:
                    data['roleType'] = 1

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
            data['num'] = len(yw_models.activity_sign_up.objects.filter(uuid_act=activity.uuid))

            try:
                files = models.UploadRecord.objects.filter(activity_id=activity_uuid)
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
        print(str(new_activity.uuid))
        data['uuid'] = str(new_activity.uuid)
        # 获取活动创建者用户名
        if 'username' not in request.session.keys():
            username = None
            print("没有UUID")
        else:
            username = request.session['username']
        if username:
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
                new_activity.logo = logo_path.split(globals.PATH)[1] + '/default.jpg'
                # 写入logo文件
                logo_path = logo_path + 'default.jpg'
                default = open(globals.PATH_DEFAULT, 'rb+')
                logo = open(logo_path, 'wb+')
                logo.write(default.read())
                default.close()
                logo.close()

            # 如果上传了logo，将logo保存到本地
            else:
                new_activity.logo = logo_path.split(globals.PATH)[1] + '/' + logo.name

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
            if name and start_time and end_time and location:
                # 填入数据

                new_activity.name = name
                new_activity.type = activity_type
                new_activity.start_time = start_time
                new_activity.end_time = end_time
                new_activity.location = location
                if organizer:
                    new_activity.organizer = organizer
                new_activity.organizer = username
                new_activity.introduction = introduction
                new_activity.username = username

                new_activity.save()

                data['message'] = '会议创建成功！'
                data['status'] = True

                return JsonResponse(data)
            else:
                data['message'] = '信息尚未完善！'
                return JsonResponse(data)
        else:
            data['message'] = 'session中无数据！'
            return JsonResponse


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
        file_path = file_path.split(globals.PATH)[1] + '/'
        # 新建文件记录的相关属性
        new_record.activity_id = act_uuid
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
        'sum': 0,  # 活动总数
        'activities': [],  # 活动列表
        'message': '',
    }

    if request.method == 'GET':
        if 'username' not in request.session.keys():
            username = None
            print("没有username")
        else:
            username = request.session['username']

        if username:
            acts = models.Activity.objects.filter(username=username).order_by('start_time')
            btn_type = request.GET.get('btn-type')
            page_id = int(request.GET.get('page-id'))
            per_page = int(request.GET.get('per-page'))

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
                            dictionary['num'] = len(yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                            data['activities'].append(dictionary)

                        count += 1
                import math
                data['pageNum'] = math.ceil(count / per_page)
                data['sum'] = count
                if data['pageNum'] == 0:
                    data['message'] = '不存在未发布的活动！'
                else:
                    data['message'] = '成功！'
                return JsonResponse(data)

            elif btn_type == 'management-published':
                count = 0
                for act in acts:
                    if act.status_publish == 'published':
                        if (page_id - 1) * per_page <= count < per_page * page_id:
                            dictionary = {}
                            import yw
                            recommend = yw_models.recommended_activity.objects.filter(activity_id=act.uuid)
                            if recommend:
                                dictionary['ifRecommended'] = True
                            else:
                                dictionary['ifRecommended'] = False
                            dictionary['logoSrc'] = act.logo
                            dictionary['activityName'] = act.name
                            dictionary['location'] = act.location
                            dictionary['startTime'] = act.start_time
                            dictionary['endTime'] = act.end_time
                            dictionary['id'] = act.uuid
                            dictionary['num'] = len(yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                            data['activities'].append(dictionary)
                        count += 1
                import math
                data['pageNum'] = math.ceil(count / per_page)
                data['sum'] = count
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
                            dictionary['num'] = len(yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                            data['activities'].append(dictionary)
                        count += 1
                import math
                data['pageNum'] = math.ceil(count / per_page)
                data['sum'] = count
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
                            dictionary['num'] = len(yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                            data['activities'].append(dictionary)
                        count += 1
                import math
                data['pageNum'] = math.ceil(count / per_page)
                data['sum'] = count
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
                            dictionary['num'] = len(yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                            admin_activity = models.AdminActivity.objects.get(activity_id=act.uuid)
                            dictionary['action'] = admin_activity.action
                            print(dictionary['action'])
                            data['activities'].append(dictionary)
                        count += 1
                import math
                data['pageNum'] = math.ceil(count / per_page)
                data['sum'] = count
                if data['pageNum'] == 0:
                    data['message'] = '不存在待审核的会议！'
                else:
                    data['message'] = '成功！'
                return JsonResponse(data)
            # author: y4ngyy
            elif btn_type[:2] == 'my':
                if 'uuid' not in request.session.keys():
                    user_uuid = None
                    print("没有UUID")
                else:
                    user_uuid = request.session['uuid']
                print(user_uuid)
                if user_uuid:
                    attend_acts_uuid = yw_models.activity_sign_up.objects.filter(user_id=user_uuid)
                    acts = []
                    # 获取所有报名会议的信息
                    for uid in attend_acts_uuid:
                        act = models.Activity.objects.get(uuid=uid.activity_id)
                        acts.append(act)
                    if btn_type == 'my-not_start':
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
                                    dictionary['num'] = len(
                                        yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                                    # admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                                    # dictionary['action'] = admin_activity.action
                                    # print(dictionary['action'])
                                    data['activities'].append(dictionary)
                                count += 1
                        import math
                        data['pageNum'] = math.ceil(count / per_page)
                        data['sum'] = count
                        if data['pageNum'] == 0:
                            data['message'] = '不存在参加的未开始的会议！'
                        else:
                            data['message'] = '成功！'
                        return JsonResponse(data)
                    elif btn_type == 'my-processing':
                        count = 0
                        for act in acts:
                            if act.status_publish == 'processing':
                                if (page_id - 1) * per_page <= count < per_page * page_id:
                                    dictionary = {}
                                    dictionary['logoSrc'] = act.logo
                                    dictionary['activityName'] = act.name
                                    dictionary['location'] = act.location
                                    dictionary['startTime'] = act.start_time
                                    dictionary['endTime'] = act.end_time
                                    dictionary['id'] = act.uuid
                                    dictionary['num'] = len(
                                        yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                                    # admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                                    # dictionary['action'] = admin_activity.action
                                    # print(dictionary['action'])
                                    data['activities'].append(dictionary)
                                count += 1
                        import math
                        data['pageNum'] = math.ceil(count / per_page)
                        data['sum'] = count
                        if data['pageNum'] == 0:
                            data['message'] = '不存在参加的进行中的会议！'
                        else:
                            data['message'] = '成功！'
                        return JsonResponse(data)
                    elif btn_type == 'my-finished':
                        count = 0
                        for act in acts:
                            if act.status_publish == 'finished':
                                if (page_id - 1) * per_page <= count < per_page * page_id:
                                    dictionary = {}
                                    dictionary['logoSrc'] = act.logo
                                    dictionary['activityName'] = act.name
                                    dictionary['location'] = act.location
                                    dictionary['startTime'] = act.start_time
                                    dictionary['endTime'] = act.end_time
                                    dictionary['id'] = act.uuid
                                    dictionary['num'] = len(
                                        yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                                    # admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                                    # dictionary['action'] = admin_activity.action
                                    # print(dictionary['action'])
                                    data['activities'].append(dictionary)
                                count += 1
                        import math
                        data['pageNum'] = math.ceil(count / per_page)
                        data['sum'] = count
                        if data['pageNum'] == 0:
                            data['message'] = '不存在参加的已结束的会议！'
                        else:
                            data['message'] = '成功！'
                        return JsonResponse(data)
                else:
                    data['message'] = 'session中无数据！'
                    return JsonResponse(data)
            elif btn_type[:3] == 'fav':
                if 'uuid' not in request.session.keys():
                    user_uuid = None
                    print("没有UUID")
                else:
                    user_uuid = request.session['uuid']
                if user_uuid:
                    collected_acts_uuid = yw_models.user_collection.objects.filter(user_id=user_uuid)
                    acts = []
                    for uid in collected_acts_uuid:
                        act = models.Activity.objects.get(uuid=uid.activity_id)
                        acts.append(act)
                    if btn_type == 'fav-not_start':
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
                                    dictionary['num'] = len(
                                        yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                                    # admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                                    # dictionary['action'] = admin_activity.action
                                    # print(dictionary['action'])
                                    data['activities'].append(dictionary)
                                count += 1
                        import math
                        data['pageNum'] = math.ceil(count / per_page)
                        data['sum'] = count
                        if data['pageNum'] == 0:
                            data['message'] = '不存在参加的进行中的会议！'
                        else:
                            data['message'] = '成功！'
                        return JsonResponse(data)
                    elif btn_type == 'fav-processing':
                        count = 0
                        for act in acts:
                            if act.status_publish == 'processing':
                                if (page_id - 1) * per_page <= count < per_page * page_id:
                                    dictionary = {}
                                    dictionary['logoSrc'] = act.logo
                                    dictionary['activityName'] = act.name
                                    dictionary['location'] = act.location
                                    dictionary['startTime'] = act.start_time
                                    dictionary['endTime'] = act.end_time
                                    dictionary['id'] = act.uuid
                                    dictionary['num'] = len(
                                        yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                                    # admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                                    # dictionary['action'] = admin_activity.action
                                    # print(dictionary['action'])
                                    data['activities'].append(dictionary)
                                count += 1
                        import math
                        data['pageNum'] = math.ceil(count / per_page)
                        data['sum'] = count
                        if data['pageNum'] == 0:
                            data['message'] = '不存在参加的进行中的会议！'
                        else:
                            data['message'] = '成功！'
                        return JsonResponse(data)
                    elif btn_type == 'fav-finished':
                        count = 0
                        for act in acts:
                            if act.status_publish == 'finished':
                                if (page_id - 1) * per_page <= count < per_page * page_id:
                                    dictionary = {}
                                    dictionary['logoSrc'] = act.logo
                                    dictionary['activityName'] = act.name
                                    dictionary['location'] = act.location
                                    dictionary['startTime'] = act.start_time
                                    dictionary['endTime'] = act.end_time
                                    dictionary['id'] = act.uuid
                                    dictionary['num'] = len(
                                        yw_models.activity_sign_up.objects.filter(uuid_act=act.uuid))
                                    # admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                                    # dictionary['action'] = admin_activity.action
                                    # print(dictionary['action'])
                                    data['activities'].append(dictionary)
                                count += 1
                        import math
                        data['pageNum'] = math.ceil(count / per_page)
                        data['sum'] = count
                        if data['pageNum'] == 0:
                            data['message'] = '不存在参加的进行中的会议！'
                        else:
                            data['message'] = '成功！'
                        return JsonResponse(data)
                else:
                    data['message'] = 'session中无数据！'
                    return JsonResponse(data)
            else:
                data['message'] = '不存在的会议状态！'
                return JsonResponse(data)
        else:
            data['message'] = 'session中无数据！'
            return JsonResponse(data)
    else:
        data['message'] = '空表单'
        return JsonResponse(data)


@csrf_exempt
def editActivity(request):
    data = {
        'act_status': False,
        'message': '',
    }

    if request.method == 'POST':

        uuid = request.POST.get('act_uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)

            if 'username' not in request.session.keys():
                editor = None
                print("没有Username")
            else:
                editor = request.session['username']
            if editor:
                if activity.username != editor:
                    data['message'] = '你没有权限修改该活动！'
                    return JsonResponse(data)
            else:
                data['message'] = 'session中无数据！'
                return JsonResponse(data)

        except:
            data['message'] = '该活动不存在！'
            return JsonResponse(data)

        if activity.status_publish == 'unpublished':

            logo = request.FILES.get('logo', None)
            if logo:
                os.remove(globals.PATH + activity.logo)
                # 新建logo保存路径
                logo_path = globals.PATH_ACTIVITY + str(activity.uuid) + '/'

                activity.logo = logo_path.split(globals.PATH)[1] + '/' + logo.name
                destination = open(os.path.join(logo_path, logo.name), 'wb+')
                for chunk in logo.chunks():
                    destination.write(chunk)
                destination.close()

            # 删除文件
            import json
            delete_files = request.POST.get('delete_files', None)
            delete_files = json.loads(delete_files)

            for filename in delete_files:
                os.remove(globals.PATH + 'activity/' + str(activity.uuid) + '/' + filename)
                files = models.UploadRecord.objects.filter(activity_id=activity.uuid)
                for file in files:
                    if file.file_name == filename:
                        file.delete()

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

            activity.name = name
            activity.type = activity_type
            activity.start_time = start_time
            activity.end_time = end_time
            activity.location = location
            activity.organizer = organizer
            activity.introduction = introduction

            activity.save()
            data['message'] = '会议信息修改成功！'

            return JsonResponse(data)

        elif activity.status_publish == 'published':
            # 获取活动logo

            old_path = globals.PATH_ADMIN + str(activity.uuid) + '/'
            isExists = os.path.exists(old_path)
            # 判断路径是否存在
            if not isExists:
                # 如果不存在则创建目录
                # 创建目录操作函数
                os.makedirs(old_path)

            old_logo_path = globals.PATH + activity.logo
            admin_logo_path = globals.PATH_ADMIN + activity.logo.split('activity/')[1]
            old_logo = activity.logo.replace('activity', 'admin')

            old = open(old_logo_path, 'rb+')
            admin = open(admin_logo_path, 'wb+')
            admin.write(old.read())
            old.close()
            admin.close()

            logo = request.FILES.get('logo', None)
            if logo:

                os.remove(globals.PATH + activity.logo)
                logo_path = globals.PATH_ACTIVITY + str(activity.uuid) + '/'

                activity.logo = logo_path.split(globals.PATH)[1] + '/' + logo.name
                destination = open(os.path.join(logo_path, logo.name), 'wb+')
                for chunk in logo.chunks():
                    destination.write(chunk)
                destination.close()

            # 删除文件
            import json
            delete_files = request.POST.get('delete_files', None)
            delete_files = json.loads(delete_files)

            for filename in delete_files:
                os.remove(globals.PATH + 'activity/' + str(activity.uuid) + '/' + filename)
                files = models.UploadRecord.objects.filter(activity_id=activity.uuid)
                for file in files:
                    if file.file_name == filename:
                        file.delete()

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

            old_info = models.OldInfo()
            old_info.uuid = activity.uuid
            old_info.name = activity.name
            old_info.type = activity.type
            old_info.start_time = activity.start_time
            old_info.end_time = activity.end_time
            old_info.organizer = activity.organizer
            old_info.location = activity.location
            old_info.introduction = activity.introduction
            old_info.logo = old_logo
            old_info.save()

            activity.status_publish = 'to_be_audited'
            data['act_status'] = True
            activity.name = name
            activity.type = activity_type
            activity.start_time = start_time
            activity.end_time = end_time
            activity.location = location
            activity.organizer = organizer
            activity.introduction = introduction
            activity.save()

            admin_activity = models.AdminActivity.objects.filter(activity_id=activity.uuid)
            if admin_activity:
                data['message'] = '您已提交申请，请不要重复提交！'
                return JsonResponse(data)
            else:
                new_admin_activity = models.AdminActivity()
                new_admin_activity.activity_id = activity.uuid
                new_admin_activity.action = 'modify'
                new_admin_activity.save()

            data['message'] = '已提交管理员审核！'

            return JsonResponse(data)


@csrf_exempt
def adminAgreeEdit(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)
        activity = models.Activity.objects.get(uuid=uuid)
        name_act = activity.name
        import login
        user = login_models.User.objects.get(username=activity.username)
        activity.status_publish = 'published'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        change = []
        oldInfo = models.OldInfo.objects.get(uuid=uuid)
        if activity.name != oldInfo.name:
            dictionary = {
                'item': '活动名',
                'old': oldInfo.name,
                'new': activity.name,
            }
            change.append(dictionary)
        if activity.type != oldInfo.type:
            dictionary = {
                'item': '活动类型',
                'old': oldInfo.type,
                'new': activity.type,
            }
            change.append(dictionary)
        if activity.start_time != oldInfo.start_time:
            dictionary = {
                'item': '开始时间',
                'old': oldInfo.start_time,
                'new': activity.start_time,
            }
            change.append(dictionary)
        if activity.end_time != oldInfo.end_time:
            dictionary = {
                'item': '结束时间',
                'old': oldInfo.end_time,
                'new': activity.end_time,
            }
            change.append(dictionary)
        if activity.location != oldInfo.location:
            dictionary = {
                'item': '举办地点',
                'old': oldInfo.location,
                'new': activity.location,
            }
            change.append(dictionary)
        if activity.organizer != oldInfo.organizer:
            dictionary = {
                'item': '主办方',
                'old': oldInfo.organizer,
                'new': activity.organizer,
            }
            change.append(dictionary)
        if activity.introduction != oldInfo.introduction:
            dictionary = {
                'item': '活动简介',
                'old': oldInfo.introduction,
                'new': activity.introduction,
            }
            change.append(dictionary)

        contents = '您报名参加的活动 %s 相关信息已被修改，请留意修改的信息：\n' % name_act
        for info in change:
            contents += '{item}已由{old}变为{new}\n'.format(**info)

        data['message'] = '会议资料修改成功！'
        # sendMail 发邮件
        title = '编辑审核结果'
        contents = '您申请编辑的活动 %s 信息已成功修改。' % name_act

        yw_views.sendMail(user.email, title, contents)
        # 操作报名表
        records = yw_models.activity_sign_up.objects.filter(activity_id=activity.uuid)

        for i in range(len(records)):  # 对报名会议的所有用户进行操作
            try:
                user = login_models.User.objects.get(uuid=records[i].uuid_user)
            except:
                print('handle_delete:未获得uuid_user对应的user')
            title = "活动通知"
            yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)


@csrf_exempt
def adminRefuseEdit(request):
    data = {
        'message': ''
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)
        activity = models.Activity.objects.get(uuid=uuid)
        oldInfo = models.OldInfo.objects.get(uuid=activity.uuid)

        os.remove(globals.PATH + activity.logo)
        old_logo_path = globals.PATH + oldInfo.logo
        logo_path = globals.PATH_ADMIN + oldInfo.logo.split('admin/')[1]
        logo = oldInfo.logo.replace('admin', 'activity')

        old = open(old_logo_path, 'rb+')
        admin = open(logo_path, 'wb+')
        admin.write(old.read())
        old.close()
        admin.close()

        import shutil
        shutil.rmtree(globals.PATH + 'admin/' + str(activity.uuid))

        activity.logo = logo
        activity.status_publish = 'published'
        activity.name = oldInfo.name
        activity.type = oldInfo.type
        activity.location = oldInfo.location
        activity.start_time = oldInfo.start_time
        activity.end_time = oldInfo.end_time
        activity.introduction = oldInfo.introduction
        activity.organizer = oldInfo.organizer
        activity.save()
        oldInfo.delete()

        name_act = activity.name
        import login
        user = login_models.User.objects.get(username=activity.username)

        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        data['message'] = '修改请求未通过！'
        # sendMail 发邮件
        title = '编辑审核结果'
        contents = '经审核，您申请编辑的活动 %s 信息不符合条件，不予修改。' % name_act
        yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)


@csrf_exempt
def deleteActivity(request):
    data = {
        'act_status': False,
        'message': ''
    }

    if request.method == 'POST':

        uuid = request.POST.get('uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)
            if 'username' not in request.session.keys():
                editor = None
                print("没有username")
            else:
                editor = request.session['username']
            if editor:
                if activity.username != editor:
                    data['message'] = '你没有权限删除该活动！'
                    return JsonResponse(data)
            else:
                data['message'] = 'session中无数据！'
                return JsonResponse(data)
        except:
            data['message'] = '该活动不存在！'
            return JsonResponse(data)

        if activity.status_publish == 'unpublished':
            import shutil
            shutil.rmtree(globals.PATH + 'activity/' + str(activity.uuid) + '/')
            models.UploadRecord.objects.filter(activity_id=activity.uuid).delete()
            activity.delete()
            data['act_status'] = True
            data['message'] = '活动已删除！'
            return JsonResponse(data)
        elif activity.status_publish == 'published':
            activity.status_publish = 'to_be_audited'
            data['act_status'] = True
            activity.save()
            admin_activity = models.AdminActivity.objects.filter(activity_id=activity.uuid)
            if admin_activity:
                data['message'] = '您已提交申请，请不要重复提交！'
                return JsonResponse(data)
            else:
                new_admin_activity = models.AdminActivity()
                new_admin_activity.activity_id = activity.uuid
                new_admin_activity.action = 'delete'
                new_admin_activity.save()

            data['message'] = '已向管理员提交申请'
            return JsonResponse(data)


@csrf_exempt
def adminAgreeDelete(request):
    data = {
        'message': ''
    }

    if request.method == 'POST':

        uuid = request.POST.get('act_uuid', None)
        print(uuid)

        activity = models.Activity.objects.get(uuid=uuid)
        name_act = activity.name
        import login
        user = login_models.User.objects.get(username=activity.username)

        import shutil
        shutil.rmtree(globals.PATH + 'activity/' + str(activity.uuid) + '/')
        models.UploadRecord.objects.filter(activity_id=activity.uuid).delete()
        activity.delete()
        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        data['message'] = '活动已删除！'

        # sendMail 发邮件
        title = '删除审核结果'
        contents = '您申请删除的活动 %s 已成功删除。' % name_act
        import yw
        yw_views.sendMail(user.email, title, contents)
        # 操作报名表
        records = yw_models.activity_sign_up.objects.filter(activity_id=activity.uuid)

        for i in range(len(records)):  # 对报名会议的所有用户进行操作
            try:
                user = login_models.User.objects.get(uuid=records[i].uuid_user)
            except:
                print('handle_delete:未获得uuid_user对应的user')
            title = "活动通知"
            contents = '您报名参加的活动 %s 已被举办者取消，请留意主办方发布的相关消息。' % name_act
            yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)


@csrf_exempt
def adminRefuseDelete(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        activity = models.Activity.objects.get(uuid=uuid)
        name_act = activity.name
        import login
        user = login_models.User.objects.get(username=activity.username)

        activity.status_publish = 'published'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        data['message'] = '删除审核未通过！'

        # sendMail 发邮件
        title = '删除审核结果'
        contents = '经审核，您申请删除的活动 %s 不符合条件，无法删除。' % name_act
        import yw
        yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)


@csrf_exempt
def publishActivity(request):
    data = {
        'act_status': False,
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)
            if 'username' not in request.session.keys():
                editor = None
                print("没有Username")
            else:
                editor = request.session['username']
            if editor:
                if activity.username != editor:
                    data['message'] = '你没有权限发布该活动！'
                    return JsonResponse(data)
            else:
                data['message'] = 'session中无数据！'
                return JsonResponse(data)

        except:
            data['message'] = '该活动不存在！'
            return JsonResponse(data)

        activity.status_publish = 'to_be_audited'
        data['act_status'] = True
        activity.save()

        admin_activity = models.AdminActivity.objects.filter(activity_id=activity.uuid)
        if admin_activity:
            data['message'] = '您已提交申请，请不要重复提交！'
            return JsonResponse(data)
        else:
            new_admin_activity = models.AdminActivity()
            new_admin_activity.activity_id = activity.uuid
            new_admin_activity.action = 'publish'

            new_admin_activity.save()

        data['message'] = '已向管理员提交申请！'
        return JsonResponse(data)


@csrf_exempt
def adminAgreePublish(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)
        print(uuid)

        activity = models.Activity.objects.get(uuid=uuid)
        name_act = activity.name

        user = login_models.User.objects.get(username=activity.username)
        activity.status_publish = 'published'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        data['message'] = '发布成功！'

        # sendMail发邮件
        title = '发布审核结果'
        contents = '您申请发布的活动 %s 已成功发布。' % name_act

        yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)


@csrf_exempt
def adminRefusePublish(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        activity = models.Activity.objects.get(uuid=uuid)
        name_act = activity.name

        user = login_models.User.objects.get(username=activity.username)
        activity.status_publish = 'unpublished'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        data['message'] = '发布请求未通过！'
        # sendMail 发邮件
        title = '发布审核结果'
        contents = '经审核，您申请发布的活动 %s 不符合条件，无法发布。' % name_act

        yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)


@csrf_exempt
def cancelApplication(request):
    data = {
        'act_status': False,
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)
            admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
            if 'username' not in request.session.keys():
                editor = None
                print("没有Username")
            else:
                editor = request.session['username']
            if editor:
                if activity.username != editor:
                    data['message'] = '你没有权限修改该活动！'
                    return JsonResponse(data)
            else:
                data['message'] = 'session中无数据！'
                return JsonResponse(data)

        except:
            data['message'] = '该活动不存在！'
            return JsonResponse(data)

        if admin_activity.action == 'publish':
            activity.status_publish = 'unpublished'
            activity.save()
            admin_activity.delete()
            data['act_status'] = True
            data['message'] = '已撤回发布请求！'
            return JsonResponse(data)

        elif admin_activity.action == 'delete':
            activity.status_publish = 'published'
            activity.save()
            admin_activity.delete()
            data['act_status'] = True
            data['message'] = '已撤回删除请求！'
            return JsonResponse(data)

        elif admin_activity.action == 'modify':
            oldInfo = models.OldInfo.objects.get(uuid=activity.uuid)

            os.remove(globals.PATH + activity.logo)
            old_logo_path = globals.PATH + oldInfo.logo
            logo_path = globals.PATH_ADMIN + oldInfo.logo.split('admin/')[1]
            logo = oldInfo.logo.replace('admin', 'activity')

            old = open(old_logo_path, 'rb+')
            admin = open(logo_path, 'wb+')
            admin.write(old.read())
            old.close()
            admin.close()

            import shutil
            shutil.rmtree(globals.PATH + 'admin/' + str(activity.uuid))

            activity.logo = logo
            activity.status_publish = 'published'
            activity.name = oldInfo.name
            activity.type = oldInfo.type
            activity.location = oldInfo.location
            activity.start_time = oldInfo.start_time
            activity.end_time = oldInfo.end_time
            activity.introduction = oldInfo.introduction
            activity.organizer = oldInfo.organizer
            activity.save()
            oldInfo.delete()

            admin_activity.delete()
            data['act_status'] = True
            data['message'] = '已撤回修改请求！'
            return JsonResponse(data)


@csrf_exempt
def applyRecommend(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)
            if 'username' not in request.session.keys():
                editor = None
                print("没有Username")
            else:
                editor = request.session['username']
            if editor:
                if activity.username != editor:
                    data['message'] = '你没有权限申请推荐该活动！'
                    return JsonResponse(data)
            else:
                data['message'] = 'session中无数据！'
                return JsonResponse(data)

        except:
            data['message'] = '该活动不存在！'
            return JsonResponse(data)

        admin_activity = models.AdminActivity.objects.filter(activity_id=activity.uuid)
        if admin_activity:
            data['message'] = '您已提交申请，请不要重复提交！'
            return JsonResponse(data)
        else:
            new_admin_activity = models.AdminActivity()
            new_admin_activity.activity_id = activity.uuid
            new_admin_activity.action = 'recommend'

            new_admin_activity.save()

        data['message'] = '已向管理员提交申请！'
        return JsonResponse(data)


@csrf_exempt
def adminAgreeRecommend(request):
    data = {
        'message': '',
    }
    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        activity = models.Activity.objects.get(uuid=uuid)
        name_act = activity.name

        user = login_models.User.objects.get(username=activity.username)


        recommend_activity = yw_models.recommended_activity.objects.filter(activity_id=activity.uuid)
        if recommend_activity:
            data['message'] = '活动已被推荐！'
            return JsonResponse(data)
        else:
            new_recommend = yw_models.recommended_activity()
            new_recommend.activity_id = activity.uuid
            new_recommend.save()

        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        data['message'] = '推荐请求成功！'

        # sendMail发邮件
        title = '推荐审核结果'
        contents = '您申请推荐的活动 %s 已登上首页。' % name_act
        import yw
        yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)


@csrf_exempt
def adminRefuseRecommend(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        activity = models.Activity.objects.get(uuid=uuid)
        name_act = activity.name

        user = login_models.User.objects.get(username=activity.username)

        admin_activity = models.AdminActivity.objects.get(activity_id=uuid)
        admin_activity.delete()

        data['message'] = '申请推荐未通过！'
        # sendMail 发邮件
        title = '推荐审核结果'
        contents = '经审核，您申请推荐的活动 %s 不符合条件，暂不能推荐。' % name_act

        yw_views.sendMail(user.email, title, contents)

        return JsonResponse(data)