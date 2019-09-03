from django.http import JsonResponse
from login import models as models_login
from django.views.decorators.csrf import csrf_exempt
from . import models
import qrcode
import os
import globals
from activity import models as models_activity
from django.core.mail import send_mail
from login import models as models_login

# Create your views here.

@csrf_exempt
def showRecent(request):
    data={
        'list_activity': [],  # 字典嵌套列表再嵌套字典
        'message': '',
    }
    if request.method == 'GET':
        try:
            record=models.recent_activity.objects.filter()
        except:
            data['message']='无记录！'
            return JsonResponse(data)
        for entry in range(len(record)):
            activity = {
                'uuid_act': '',
                'name_act': '',
                'start_time': '',
                'end_time': '',
                'logo':'',
                'location':'',
            }
            # print('进入了for')
            activity['uuid_act'] = record[entry].uuid_act
            # 进入activity表根据uuid获取会议名
            try:
                tmp_activity = models_activity.Activity.objects.get(uuid=record[entry].uuid_act)
            except:
                data['message'] = '无此活动！'
                return JsonResponse(data)
            # print(tmp_activity.name)
            activity['name_act'] = tmp_activity.name
            activity['start_time'] = tmp_activity.start_time
            activity['end_time'] = tmp_activity.end_time
            activity['logo']=tmp_activity.logo
            activity['location']=tmp_activity.location
            # 将字典activity加入列表

            data['list_activity'].append(activity)
        data['message']='查询成功！'
        return JsonResponse(data)

    else:
        data['message'] = '空表单'
        return JsonResponse(data)

#用户申请参加会议，将用户加入会议申请表,前端需post活动uuid
@csrf_exempt
def apply(request):
    data={
        'message':'',
    }
    if request.method=='POST':
        username=request.session['username']
        if username:
            try:
                user= models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            uuid_act=request.POST.get('uuid_act',None)
            if uuid_act:
                same_application=models.activity_sign_up.objects.filter(uuid_act=uuid_act,uuid_user=user.uuid)
                if same_application:
                    data['message']='重复报名！'
                    return JsonResponse(data)
                else:
                    new_record=models.activity_sign_up()
                    new_record.uuid_user=user.uuid
                    new_record.uuid_act=uuid_act
                    #用uuid生成二维码并存入用户文件夹
                    path_code = globals.PATH_USER + user.uuid + '/qrcode/'
                    isExists = os.path.exists(path_code)
                    # 判断路径是否存在
                    if not isExists:
                        # 如果不存在则创建目录
                        # 创建目录操作函数
                        os.makedirs(path_code)

                    make_qr(uuid_act,path_code+'/'+uuid_act+'.png')#在本地生成二维码


                    path_code = 'user/' +user.uuid+'/qrcode/'+uuid_act+'.png' # 改变路径存入数据库
                    new_record.qr_code=path_code
                    new_record.save()
                    data['message']='申请成功！'
                    return  JsonResponse(data)



            else:
                data['message']='未获得uuid！'
                return JsonResponse(data)

        else:
            data['message'] = '未接收到用户名！'
            return JsonResponse(data)
    else:
        data['message']='无数据！'
        return JsonResponse(data)





@csrf_exempt
def collect(request):
    data={
        'message':'',
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
                same_collection=models.user_collection.objects.filter(uuid_act=uuid_act,uuid_user=user.uuid)
                if same_collection:
                    data['message']='重复收藏！'
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
def showActivityList(request):
    data={
        'list_activity':[],
        'message':'',
    }
    if request.method=='GET':
        try:
            activitys=models_activity.AdminActivity.objects.filter()
        except:
            data['message']='未取得AdminActivity中的数据'
            return  JsonResponse(data)
        else:
            for i in range(len(activitys)):
                #根据uuid去activity表找数据
                try:
                    record_act=models_activity.Activity.objects.get(uuid=activitys[i].uuid)
                except:
                    data['message']='未取得uuid对应的活动'
                    return JsonResponse(data)
                else:
                    activity={
                        'uuid_act':record_act.uuid,
                        'name_act':record_act.name,
                        'location':record_act.location,
                        'start_time':record_act.start_time,
                        'end_time':record_act.end_time,
                        'organizer':record_act.organizer,
                        'action':activitys[i].action,
                    }
                    data['list_activity'].append(activity)
            data['message'] = '已填入数据！'
            return JsonResponse(data)
    else:
        data['message']='未收到get'
        return JsonResponse(data)

@csrf_exempt
def showModification(request):
    data={
        'message':'',
        'name_old':'',
        'name_new':'',
        'type_old':'',
        'type_new':'',
        'start_time_old':'',
        'start_time_new':'',
        'end_time_old':'',
        'end_time_new':'',
        'location_old':'',
        'location_new':'',
        'organizer_old':'',
        'organizer_new':'',
        'logo_old':'',
        'logo_new':'',
        'introduction_old':'',
        'introduction_new':'',
        'files_new':'',
        #旧文件已审核过，不显示
    }
    if request.method=='GET':
        uuid=request.GET.get('uuid')
        if uuid:
            try:
                activity_new=models_activity.Activity.objects.get(uuid=uuid)
                activity_old=models_activity.OldInfo.objects.get(uuid=uuid)
            except:
                data['message']='获取会议信息错误'
                return JsonResponse(data)
            data['name_new']=activity_new.name
            data['name_old']=activity_old.name
            data['type_new']=activity_new.name
            data['type_old']=activity_old.name
            data['start_time_new']=activity_new.start_time
            data['start_time_old']=activity_old.start_time
            data['end_time_new']=activity_new.end_time
            data['end_time_old']=activity_old.end_time
            data['location_new']=activity_new.location
            data['location_old']=activity_old.location
            data['organizer_new']=activity_new.organizer
            data['organizer_old']=activity_old.organizer
            data['logo_new']=activity_new.logo
            data['logo_old']=activity_old.logo
            data['introduction_old']=activity_new.introduction
            data['introduction_new']=activity_old.introduction
            try:
                files=models_activity.UploadRecord.objects.filter(act_uuid=uuid)
                for i in files:
                    dictionary = {}
                    dictionary['fileName'] = i.file_name
                    dictionary['fileSrc'] = i.file_path
                    data['files_new'].append(dictionary)
                return JsonResponse(data)
            except:
                data['message'] = '该活动没有文件！'
                return JsonResponse(data)
        else:
            data['message']='未获得uuid'
            return JsonResponse(data)
    else:
        data['message']='未收到GET'
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




#生成二维码图片

def make_qr(str,save):
  qr=qrcode.QRCode(
    version=4, #生成二维码尺寸的大小 1-40 1:21*21（21+(n-1)*4）
    error_correction=qrcode.constants.ERROR_CORRECT_M, #L:7% M:15% Q:25% H:30%
    box_size=10, #每个格子的像素大小
    border=2, #边框的格子宽度大小
  )
  qr.add_data(str)
  qr.make(fit=True)
  image=qr.make_image()
  image.save(save)

def sendMail(target,title,contents):
    send_mail(
        title,
        contents,
        '1040214708@qq.com',
        [target],
    )