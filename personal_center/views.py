from login import models as models_login
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import JsonResponse

# Create your views here.


@csrf_exempt
def showInfo(request):
    data={
       "avatar":'',
       'username':'',
       'gender':'',
       'email':'',
       'phone_number':'',
       'type':'',
       'address':'',
       'company':'',
       'profession':'',
       'introduction':'',
       'message':'',
    }
    if request.method=='POST':
        username=request.POST.get('username',None)
        if username:
            try:
                user= models_login.User.objects.get(username=username)
            except:
                data['message'] = '不存在的用户'
                return JsonResponse(data)
            data['avatar']=user.avatar
            data['gender']=user.gender
            data['email']=user.email
            data['phone_number']=user.phone_number
            data['type']=user.type
            data['address']=user.address
            data['company']=user.company
            data['profession']=user.profession
            data['introduction']=user.introduction
            data['message']='提取信息完毕！'
            return JsonResponse(data)
        else:
            data['message']='未接收到用户名'
            return JsonResponse(data)

def editInfo(request):
    data={
        'message':'',
    }
