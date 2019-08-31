from django.http import JsonResponse
from login import models as models_login
from django.views.decorators.csrf import csrf_exempt
from . import models
import qrcode
import os
import globals

# Create your views here.

@csrf_exempt
def showRecent(request):
    pass

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
                new_record=models.activity_sign_up()
                new_record.uuid_act=user.uuid
                new_record.uuid_act=uuid_act
                #用uuid生成二维码并存入用户文件夹
                path_code = globals.PATH_USER + user.uuid_user + '/qrcode/'
                isExists = os.path.exists(path_code)
                # 判断路径是否存在
                if not isExists:
                    # 如果不存在则创建目录
                    # 创建目录操作函数
                    os.makedirs(path_code)

                make_qr(uuid_act,path_code)#在本地生成二维码


                path_code = path_code.strip('D:/FRONTEND/MeetingSystemFrontEnd/') + '/' +uuid_act+'.png' # 改变路径存入数据库
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
    pass


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