from django.http import JsonResponse
from login import models as models_login
from django.views.decorators.csrf import csrf_exempt
from . import models
import qrcode
import os
import globals
from activity import models as models_activity
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


                    path_code = path_code.strip('D:/FRONTEND/MeetingSystemFrontEnd/') + '/' +user.uuid+'/qrcode/'+uuid_act+'.png' # 改变路径存入数据库
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
def publish(request):
    """发布会议"""
    data={
        'message':'',
    }
    if request.method == 'POST':
        uuid_act=request.POST.get('uuid_act',None)
        if uuid_act:
            try:
                activity=models_activity.Activity.objects.filter(uuid=uuid_act)
            except:
                data['message']='不存在的会议！'
                return JsonResponse(data)
            activity.update(status_publish='待审核')
            data['message']='请等待审核！'
            return JsonResponse(data)

        else:
            data['message']='未取得活动uuid！'
            return JsonResponse(data)
    else:
        data['message'] = '无数据！'
        return JsonResponse(data)

@csrf_exempt
def inspect(request):
    """管理员对请求发布，修改，删除的管理"""
    data={
        'message':'',
    }
    #需要前端的请求类型1：发布 2：修改 3：删除
    #发布：需要result,uuid_user（用于发邮件）,uuid_act

def handle_publish(result,uuid_user,uuid_act):
    #如果同意发布
    if result==True:
        activity=models_activity.Activity.objects.filter(uuid=uuid_act)
        activity.update(status_publish='已发布')
        return '审核通过！'
    else:#不同意发布
        return '审核未通过！'



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

