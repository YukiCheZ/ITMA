from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from taskcalendar.models import Events
from llmagent.models import APIKey


@login_required
def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)  
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'users/login.html')
 

def logout_view(request):
    logout(request)
    return redirect('login') 


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '注册成功！')
            return redirect('login')  
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def delete_user_data_view(request):
    user = request.user

    # 注销用户
    logout(request)
    
    user.delete()  # 删除用户

    # 提示用户数据已删除
    messages.success(request, "用户数据已删除并成功注销。")
    
    # 重定向到登录页面
    return redirect('login')