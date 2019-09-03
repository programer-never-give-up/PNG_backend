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
            new_activity.logo = logo_path.split(globals.PATH)[1]+'/default.jpg'
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
        file_path = file_path.split(globals.PATH)[1] + '/'
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
        'sum': 0,  # 活动总数
        'activities': [],  # 活动列表
        'message': '',
    }

    if request.method == 'GET':
        username = request.session['username']
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
                        admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                        dictionary['action'] = admin_activity.action
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
                        dictionary['logoSrc'] = act.logo
                        dictionary['activityName'] = act.name
                        dictionary['location'] = act.location
                        dictionary['startTime'] = act.start_time
                        dictionary['endTime'] = act.end_time
                        dictionary['id'] = act.uuid
                        data['activities'].append(dictionary)
                        admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                        dictionary['action'] = admin_activity.action
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
                        admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                        dictionary['action'] = admin_activity.action
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
                        admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                        dictionary['action'] = admin_activity.action
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
                        admin_activity = models.AdminActivity.objects.get(uuid=act.uuid)
                        dictionary['action'] = admin_activity.action
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


@csrf_exempt
def editActivity(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':

        uuid = request.POST.get('act_uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)

            editor = request.session['username']
            if activity.username != editor:
                data['message'] = '你没有权限修改该活动！'
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
                os.remove(globals.PATH + 'activity/' + activity.uuid + '/' + filename)
                files = models.UploadRecord.objects.filter(act_uuid=activity.uuid)
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

            old_path = globals.PATH_ADMIN + activity.uuid + '/'
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
                os.remove(globals.PATH + 'activity/' + activity.uuid + '/' + filename)
                files = models.UploadRecord.objects.filter(act_uuid=activity.uuid)
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
            activity.name = name
            activity.type = activity_type
            activity.start_time = start_time
            activity.end_time = end_time
            activity.location = location
            activity.organizer = organizer
            activity.introduction = introduction
            activity.save()

            new_admin_activity = models.AdminActivity()
            new_admin_activity.uuid = activity.uuid
            new_admin_activity.action = 'modify'
            new_admin_activity.save()

            data['message'] = '已提交管理员审核！'

            return JsonResponse(data)


@csrf_exempt
def adminAgreeEdit(request):
    data = {
        'message': ''
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)
        activity = models.Activity.objects.get(uuid=uuid)
        activity.status_publish = 'published'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(uuid=uuid)
        admin_activity.delete()

        data['message'] = '活动信息已修改！'

        change = []
        oldInfo = models.OldInfo.objects.get(uuid=uuid)
        if activity.name != oldInfo.name:
            dictionary = {
                'item': 'name',
                'old': oldInfo.name,
                'new': activity.name,
            }
            change.append(dictionary)
        if activity.type != oldInfo.type:
            dictionary = {
                'item': 'type',
                'old': oldInfo.type,
                'new': activity.type,
            }
            change.append(dictionary)
        if activity.start_time != oldInfo.start_time:
            dictionary = {
                'item': 'start_time',
                'old': oldInfo.start_time,
                'new': activity.start_time,
            }
            change.append(dictionary)
        if activity.end_time != oldInfo.end_time:
            dictionary = {
                'item': 'end_time',
                'old': oldInfo.end_time,
                'new': activity.end_time,
            }
            change.append(dictionary)
        if activity.location != oldInfo.location:
            dictionary = {
                'item': 'location',
                'old': oldInfo.location,
                'new': activity.location,
            }
            change.append(dictionary)
        if activity.organizer != oldInfo.organizer:
            dictionary = {
                'item': 'organizer',
                'old': oldInfo.organizer,
                'new': activity.organizer,
            }
            change.append(dictionary)
        if activity.introduction != oldInfo.introduction:
            dictionary = {
                'item': 'introduction',
                'old': oldInfo.introduction,
                'new': activity.introduction,
            }
            change.append(dictionary)

        # sendMail 发邮件
        return JsonResponse(data)


@csrf_exempt
def adminRefuseEdit(request):
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
        shutil.rmtree(globals.PATH + 'activity/' + activity.uuid)

        activity.logo =logo
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

        admin_activity = models.AdminActivity.objects.get(uuid=uuid)
        admin_activity.delete()


@csrf_exempt
def deleteActivity(request):
    data = {
        'message': ''
    }

    if request.method == 'POST':

        uuid = request.POST.get('act_uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)

            editor = request.session['username']
            if activity.username != editor:
                data['message'] = '你没有权限删除该活动！'
                return JsonResponse(data)

        except:
            data['message'] = '该活动不存在！'
            return JsonResponse(data)

        if activity.status_publish == 'unpublished':
            import shutil
            shutil.rmtree(globals.PATH + 'activity/' + activity.uuid)
            models.UploadRecord.objects.filter(uuid=activity.uuid).delete()
            activity.delete()
            data['message'] = '活动已删除！'
            return JsonResponse(data)
        elif activity.status_publish == 'published':
            activity.status_publish = 'to_be_audited'
            activity.save()
            new_admin_activity = models.AdminActivity()
            new_admin_activity.uuid = activity.uuid
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

        activity = models.Activity.objects.get(uuid=uuid)

        import shutil
        shutil.rmtree(globals.PATH + 'activity/' + activity.uuid)
        models.UploadRecord.objects.filter(uuid=activity.uuid).delete()
        activity.delete()
        admin_activity = models.AdminActivity.objects.get(uuid=uuid)
        admin_activity.delete()

        data['message'] = '活动已删除！'

        # sendMail 发邮件
        return JsonResponse(data)


@csrf_exempt
def adminRefuseDelete(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        activity = models.Activity.objects.get(uuid=uuid)
        activity.status_publish = 'published'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(uuid=uuid)
        admin_activity.delete()

        data['message'] = '删除成功！'
        return JsonResponse(data)


@csrf_exempt
def publishActivity(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        try:
            activity = models.Activity.objects.get(uuid=uuid)

            editor = request.session['username']
            if activity.username != editor:
                data['message'] = '你没有权限发布该活动！'
                return JsonResponse(data)

        except:
            data['message'] = '该活动不存在！'
            return JsonResponse(data)

        activity.status_publish = 'to_be_audited'
        activity.save()

        new_admin_activity = models.AdminActivity()
        new_admin_activity.uuid = activity.uuid
        new_admin_activity.action = 'publish'

        data['message'] = '已向管理员提交申请！'
        return JsonResponse(data)


@csrf_exempt
def adminAgreePublish(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        activity = models.Activity.objects.get(uuid=uuid)
        activity.status_publish = 'published'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(uuid=uuid)
        admin_activity.delete()

        data['message'] = '发布成功！'

        # sendMail发邮件

        return JsonResponse(data)


@csrf_exempt
def adminRefusePublish(request):
    data = {
        'message': '',
    }

    if request.method == 'POST':
        uuid = request.POST.get('act_uuid', None)

        activity = models.Activity.objects.get(uuid=uuid)
        activity.status_publish = 'unpublished'
        activity.save()
        admin_activity = models.AdminActivity.objects.get(uuid=uuid)
        admin_activity.delete()

        data['message'] = '拒绝发布请求！'
        return JsonResponse(data)
