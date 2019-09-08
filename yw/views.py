from django.http import JsonResponse
from login import models as models_login
from django.views.decorators.csrf import csrf_exempt
from . import models
import qrcode
import os
import globals
from activity import models as models_activity
from django.core.mail import send_mail, EmailMessage
from login import models as models_login
from personal_center import models as models_person


# Create your views here.

@csrf_exempt
def showRecent(request):
    data = {
        'list_activity': [],  # 字典嵌套列表再嵌套字典
        'message': '',
    }
    if request.method == 'GET':
        try:
            records = models_activity.Activity.objects.filter(status_publish='published',status_process='not_start')
        except:
            data['message'] = '无记录！'
            return JsonResponse(data)
        if len(records)<5:
            records=models_activity.Activity.objects.filter(status_publish='published',
                                                            status_process='not_start').order_by('start_time')[:len(records)]
        else:
            records = models_activity.Activity.objects.filter(status_publish='published',
                                                              status_process='not_start').order_by('start_time')[:5]
        for i in range(len(records)):
            activity = {
                'uuid_act': records[i].uuid,
                'name_act': records[i].name,
                'start_time': records[i].start_time,
                'end_time': records[i].end_time,
                'logo': records[i].logo,
                'location': records[i].location,
            }
            data['list_activity'].append(activity)
        data['message'] = '查询成功！'
        return JsonResponse(data)

    else:
        data['message'] = '空表单'
        return JsonResponse(data)


# 用户申请参加会议，将用户加入会议申请表,前端需post活动uuid
@csrf_exempt
def apply(request):
    data = {
        'message': '',
    }
    if request.method == 'POST':
        username = request.session['username']
        if username:
            try:
                user = models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            uuid_act = request.POST.get('uuid_act', None)
            if uuid_act:
                same_application = models.activity_sign_up.objects.filter(uuid_act=uuid_act, uuid_user=user.uuid)
                if same_application:
                    data['message'] = '重复报名！'
                    return JsonResponse(data)
                else:
                    new_record = models.activity_sign_up()
                    new_record.uuid_user = user.uuid
                    new_record.uuid_act = uuid_act
                    # 用uuid生成二维码并存入用户文件夹
                    path_code = globals.PATH_USER + user.uuid + '/qrcode/'
                    isExists = os.path.exists(path_code)
                    # 判断路径是否存在
                    if not isExists:
                        # 如果不存在则创建目录
                        # 创建目录操作函数
                        os.makedirs(path_code)

                    make_qr(user.uuid, path_code + '/' + uuid_act + '.png')  # 在本地生成二维码，二维码的数据为用户uuid

                    path_code = 'user/' + user.uuid + '/qrcode/' + uuid_act + '.png'  # 改变路径存入数据库
                    new_record.qr_code = path_code
                    new_record.save()
                    try:
                        activity=models_activity.Activity.objects.get(uuid=uuid_act)
                    except:
                        data['message']='未获得activity'
                        return JsonResponse(data)
                    target=user.email
                    title='提示信息'
                    contents='您已成功报名参加活动 %s !\n请凭附件中的二维码参与活动！'%activity.name

                    send_mail_with_file(title,contents,target,user.uuid,uuid_act)

                    data['message'] = '申请成功！'
                    return JsonResponse(data)
            else:
                data['message'] = '未获得uuid！'
                return JsonResponse(data)

        else:
            data['message'] = '未接收到用户名！'
            return JsonResponse(data)
    else:
        data['message'] = '无数据！'
        return JsonResponse(data)

@csrf_exempt
def cancel_apply(request):
    data = {
        'message': '',
        'status':False#取消成功为true
    }
    if request.method == 'POST':
        username = request.session['username']
        if username:
            try:
                user = models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            uuid_act = request.POST.get('uuid_act', None)
            if uuid_act:
                try:
                    application = models.activity_sign_up.objects.get(uuid_act=uuid_act, uuid_user=user.uuid)
                except:
                    data['message']='无对应报名数据！'
                    return JsonResponse(data)
                #删除本地二维码
                path_qrcode=globals.PATH+application.qr_code
                os.remove(path_qrcode)
                #删除数据库记录
                application.delete()
                data['message']='取消报名成功'
                data['status']=True
                return JsonResponse(data)
            else:
                data['message'] = '未获得uuid！'
                return JsonResponse(data)

        else:
            data['message'] = '未接收到用户名！'
            return JsonResponse(data)
    else:
        data['message'] = '无数据！'
        return JsonResponse(data)

@csrf_exempt
def collect(request):
    data = {
        'message': '',
    }
    if request.method == 'POST':
        username = request.session['username']
        if username:
            try:
                user = models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            uuid_act = request.POST.get('uuid_act', None)

            if uuid_act:
                same_collection = models.user_collection.objects.filter(uuid_act=uuid_act, uuid_user=user.uuid)
                if same_collection:
                    data['message'] = '重复收藏！'
                    return JsonResponse(data)
                else:
                    new_record = models.user_collection()
                    new_record.uuid_user = user.uuid
                    new_record.uuid_act = uuid_act
                    new_record.save()
                    data['message'] = '收藏成功！'
                    return JsonResponse(data)
            else:
                data['message'] = '未获得uuid！'
                return JsonResponse(data)
        else:
            data['message'] = '未接收到用户名！'
            return JsonResponse(data)
    else:
        data['message'] = '无数据！'
        return JsonResponse(data)

@csrf_exempt
def cancel_collect(request):
    data = {
        'message': '',
        'status':False,#取消成功为ture
    }
    if request.method == 'POST':
        username = request.session['username']
        if username:
            try:
                user = models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            uuid_act = request.POST.get('uuid_act', None)
            if uuid_act:
                try:
                    collection = models.activity_sign_up.objects.get(activity_id=uuid_act, user_id=user.uuid)
                except:
                    data['message'] = '无对应收藏数据！'
                    return JsonResponse(data)
                # 删除数据库记录
                collection.delete()
                data['message'] = '取消收藏成功'
                data['status']=True
                return JsonResponse(data)
            else:
                data['message'] = '未获得uuid！'
                return JsonResponse(data)
        else:
            data['message'] = '未接收到用户名！'
            return JsonResponse(data)
    else:
        data['message'] = '无数据！'
        return JsonResponse(data)



@csrf_exempt
def showActivityList(request):
    data = {
        'list_activity': [],
        'message': '',
    }
    if request.method == 'GET':
        try:
            activitys = models_activity.AdminActivity.objects.filter()
        except:
            data['message'] = '未取得AdminActivity中的数据'
            return JsonResponse(data)
        else:
            for i in range(len(activitys)):
                # 根据uuid去activity表找数据
                try:
                    record_act = models_activity.Activity.objects.get(uuid=activitys[i].activity_id)
                except:
                    data['message'] = '未取得uuid对应的活动'
                    return JsonResponse(data)
                else:
                    activity = {
                        'uuid_act': record_act.uuid,
                        'name_act': record_act.name,
                        'location': record_act.location,
                        'start_time': record_act.start_time,
                        'end_time': record_act.end_time,
                        'organizer': record_act.organizer,
                        'action': activitys[i].action,
                    }
                    data['list_activity'].append(activity)
            data['message'] = '已填入数据！'
            return JsonResponse(data)
    else:
        data['message'] = '未收到get'
        return JsonResponse(data)


@csrf_exempt
def showModification(request):
    data = {
        'message': '',
        'name_old': '',
        'name_new': '',
        'type_old': '',
        'type_new': '',
        'start_time_old': '',
        'start_time_new': '',
        'end_time_old': '',
        'end_time_new': '',
        'location_old': '',
        'location_new': '',
        'organizer_old': '',
        'organizer_new': '',
        'logo_old': '',
        'logo_new': '',
        'introduction_old': '',
        'introduction_new': '',
        'files_new': [],
        # 旧文件已审核过，不显示
    }
    print('运行')
    if request.method == 'GET':
        uuid = request.GET.get('uuid')
        print('收到GET')
        if uuid:
            print(uuid)
            try:
                activity_new = models_activity.Activity.objects.get(uuid=uuid)
                activity_old = models_activity.OldInfo.objects.get(uuid=uuid)
            except:
                data['message'] = '获取会议信息错误'
                return JsonResponse(data)
            data['name_new'] = activity_new.name
            data['name_old'] = activity_old.name
            data['type_new'] = activity_new.name
            data['type_old'] = activity_old.name
            data['start_time_new'] = activity_new.start_time
            data['start_time_old'] = activity_old.start_time

            data['end_time_new'] = activity_new.end_time
            data['end_time_old'] = activity_old.end_time
            print(data['end_time_new'])
            data['location_new'] = activity_new.location
            data['location_old'] = activity_old.location
            data['organizer_new'] = activity_new.organizer
            data['organizer_old'] = activity_old.organizer
            data['logo_new'] = activity_new.logo
            data['logo_old'] = activity_old.logo
            data['introduction_old'] = activity_old.introduction
            data['introduction_new'] = activity_new.introduction
            try:
                files = models_activity.UploadRecord.objects.filter(activity_id=uuid)
                print('取得files')
                for i in range(len(files)):
                    print('进入循环')
                    dictionary = {'fileName':'','fileSrc':'',}
                    dictionary['fileName'] = files[i].file_name
                    dictionary['fileSrc'] = files[i].file_path
                    data['files_new'].append(dictionary)
                    print('添加字典')
                print(data['files_new'])
                return JsonResponse(data)
            except:
                data['message'] = '该活动没有文件！'
                return JsonResponse(data)
        else:
            data['message'] = '未获得uuid'
            return JsonResponse(data)
    else:
        data['message'] = '未收到GET'
        return JsonResponse(data)

@csrf_exempt
def getQRcode(request):
    data={
         'qrcode':'',
         'message':'',
     }
    if request.method=="GET":
        uuid_act=request.GET.get('uuid_act')
        if uuid_act:
            uuid_user=request.session['uuid']
            if uuid_user:
                try:
                    record = models.activity_sign_up.objects.get(activity_id=uuid_act, user_id=uuid_user)
                except:
                    data['message'] = '未获得报名表中的记录'
                    return JsonResponse(data)
                data['qrcode'] = record.qr_code
                data['message'] = '已获得二维码路径'
                return JsonResponse(data)
            else:
                data['message']='未获得uuid_user'
                return JsonResponse(data)

        else:
            data['message']='未获得uuid_act'
            return JsonResponse(data)
    else:
        data['message']='未获得GET'

@csrf_exempt
def add_in_recommendation(request):
    data={
        'message':'',
    }
    if request.method=='POST':
        uuid_act=request.POST.get('uuid_act')
        if uuid_act:
            same_act=models.recommended_activity.objects.filter(activity_id=uuid_act)
            if same_act:
                data['message']='此活动已上推荐！'
                return JsonResponse(data)
            new_recommendation=models.recommended_activity()
            new_recommendation.activity_id=uuid_act
            new_recommendation.save()
            data['message']='申请推荐成功！'
            return JsonResponse(data)
        else:
            data['message']='未获得uuid'
            return JsonResponse(data)
    else:
        data['message']='未获得post'
        return JsonResponse(data)

def showRecommendation(request):
    data = {
        'list_activity': [],  # 字典嵌套列表再嵌套字典
        'message': '',
    }
    if request.method == 'GET':
        try:
            records = models.recommended_activity.objects.all().select_related('activity')#主动联表查询
        except:
            data['message'] = '无记录！'
            return JsonResponse(data)
        for i in range(len(records)):
            activity = {
                'uuid_act': records[i].activity_id,
                'name_act': records[i].activity.name,
                'start_time': records[i].activity.start_time,
                'end_time': records[i].activity.end_time,
                'logo': records[i].activity.logo,
                'location': records[i].activity.location,
                'organizer':records[i].activity.organizer,
            }
            data['list_activity'].append(activity)
        data['message'] = '查询成功！'
        return JsonResponse(data)

    else:
        data['message'] = '空表单'
        return JsonResponse(data)

@csrf_exempt
def search(request):
    data={
        'message':'',
        'list_activity': [],
    }
    if request.method=='GET':
        keyword=request.GET.get('keyword')
        try:
            records=models_activity.Activity.objects.filter(name__icontains=keyword,status_publish='published')
        except:
            data['message']='无结果！'
            return JsonResponse(data)
        for i in range(len(records)):
            activity = {
                'uuid_act': records[i].uuid,
                'name_act': records[i].name,
                'start_time': records[i].start_time,
                'end_time': records[i].end_time,
                'logo': records[i].logo,
                'location': records[i].location,
            }
            data['list_activity'].append(activity)
        data['message'] = '已搜索到%s条结果！'%len(records)
        return JsonResponse(data)
    else:
        data['message']='未收到get'
        return JsonResponse(data)

@csrf_exempt
def check_attend(request):
    data={
        'message':'',
        'status':False,#true表示验证通过
    }
    if request.method=='POST':
        uuid_act=request.POST.get('uuid_act',None)
        uuid_user=request.POST.get('uuid_user',None)
        if uuid_act and uuid_user:
            try:
                record=models.activity_sign_up.objects.filter(activity_id=uuid_act,user_id=uuid_user)
            except:
                data['message']='未找到记录！'
                return JsonResponse(data)
            new_record=models_person.On_site()
            new_record.user_id=uuid_user
            new_record.activity_id=uuid_act
            new_record.save()
            data['message']='入场成功！'
            data['status']=True
            return JsonResponse(data)
        else:
            data['message']='无活动uuid或用户uuid'
            return JsonResponse(data)
    else:
        data['message']='未收到post'
        return JsonResponse(data)


# @csrf_exempt
# def publish(request):
#     """发布会议"""
#     data={
#         'message':'',
#     }
#     if request.method == 'POST':
#         uuid_act=request.POST.get('uuid_act',None)
#         if uuid_act:
#             try:
#                 activity=models_activity.Activity.objects.filter(uuid=uuid_act)
#             except:
#                 data['message']='不存在的会议！'
#                 return JsonResponse(data)
#             activity.update(status_publish='待审核')
#             data['message']='请等待审核！'
#             return JsonResponse(data)
#
#         else:
#             data['message']='未取得活动uuid！'
#             return JsonResponse(data)
#     else:
#         data['message'] = '无数据！'
#         return JsonResponse(data)

# @csrf_exempt
# def inspect(request):
#     """管理员对请求发布，修改，删除的管理"""
#     data={
#         'message':'',
#     }
#     #需要前端的请求类型1：发布 2：修改 3：删除
#     #发布：需要result,uuid_user（用于发邮件）,uuid_act
#     if request.method=='POST':
#         type=request.POST.get('type')
#         result=request.POST.get('result')
#         uuid_act=request.POST.get('uuid_act')
#         try:
#             activity=models_activity.Activity.objects.get(uuid=uuid_act)
#         except:
#             data['message']='未获得uuid_act对应的activity'
#             return JsonResponse(data)
#         username=activity.username
#         if type==1:#发布审核
#             data['message']=handle_publish(result,username,uuid_act)
#         elif type==2:#修改审核
#             pass
#         elif type==3:
#             pass
#         else:
#             data['message']='无type'
#             return JsonResponse(data)
#     else:
#         data['message']='未post'
#         return JsonResponse(data)
#
# def handle_publish(result,username,uuid_act):
#     try:
#         user=models_login.User.objects.get(username=username)
#     except:
#         return '无user'
#     #如果同意发布
#     if result==True:
#         activity=models_activity.Activity.objects.filter(uuid=uuid_act)
#         activity.update(status_publish='已发布')
#         title='发布审核结果'
#         contents='您提交的活动已通过审核并发布！'
#         sendMail(user.email,title,contents)
#         return '发布审核通过！'
#     else:#不同意发布
#         title = '发布审核结果'
#         contents = '您提交的活动未通过审核，请检查活动内容是否违法违规！'
#         sendMail(user.email, title, contents)
#         return '发布审核未通过！'
#
# def handle_delete(result,username,uuid_act):
#     """已发布的会议删除需要进行审核，并向已报名的用户发送邮件通知"""
#     #取得email
#     try:
#         user=models_login.User.objects.get(username=username)
#     except:
#         return '无user'
#     #如果同意删除
#     if result==True:
#         try:
#             activity=models_activity.Activity.objects.get(uuid=uuid_act)#获得活动
#         except:
#             return 'handle_delete:未获得uuid_act对应的活动'
#
#         name_act=activity.name#在会议删除前取得名字
#         activity.delete()
#         title='删除审核结果'
#         contents='您申请删除的活动 %s 已成功删除。'%name_act
#         sendMail(user.email,title,contents)
#         #操作报名表
#         records=models.activity_sign_up.objects.filter(uuid_act=uuid_act)
#
#         for i in range(len(records)):#对报名会议的所有用户进行操作
#             try:
#                 user=models_login.User.objects.get(uuid=records[i].uuid_user)
#             except:
#                 return 'handle_delete:未获得uuid_user对应的user'
#             title="活动通知"
#             contents='您报名参加的活动 %s 已被举办者取消，请留意主办方发布的相关消息。'%name_act
#             sendMail(user.email,title,contents)
#         return '删除审核通过！'


# 生成二维码图片

def make_qr(str, save):
    qr = qrcode.QRCode(
        version=4,  # 生成二维码尺寸的大小 1-40 1:21*21（21+(n-1)*4）
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # L:7% M:15% Q:25% H:30%
        box_size=10,  # 每个格子的像素大小
        border=2,  # 边框的格子宽度大小
    )
    qr.add_data(str)
    qr.make(fit=True)
    image = qr.make_image()
    image.save(save)


def sendMail(target, title, contents):
    send_mail(
        title,
        contents,
        '1040214708@qq.com',
        [target],
    )

#发送带附件的邮件
def send_mail_with_file(title,contents,target,uuid_user,uuid_act):
    '''发送附件'''
    email = EmailMessage(
        title,
        contents,
        '1040214708@qq.com',   # 发件人
        [target],   # 收件人
    )

    filepath=globals.PATH_USER+'%s/qrcode/%s.png'%(uuid_user,uuid_act)
    email.attach_file(filepath, mimetype=None)
    email.send()

