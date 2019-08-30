from django.http import JsonResponse
from login import models as models_login
# Create your views here.

def showRecent(request):
    pass

#用户申请参加会议，将用户加入会议申请表,前端需post活动uuid
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
                pass
            else:
                data['message']='未获得uuid！'
                return JsonResponse(data)
        else:
            data['message'] = '未接收到用户名！'
            return JsonResponse(data)
    else:
        data['message']='无数据！'
        return JsonResponse(data)