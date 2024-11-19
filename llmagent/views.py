from django.shortcuts import render, redirect
from .forms import APIKeyForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import APIKey
from django.http import JsonResponse
from zhipuai import ZhipuAI
from django.views.decorators.csrf import csrf_exempt
from .prompts import *


@login_required
def set_api_key(request):
    try:
        # 尝试获取当前用户的API Key，如果没有，则会创建一个新的APIKey对象
        api_key_instance = APIKey.objects.get(user=request.user)
    except APIKey.DoesNotExist:
        api_key_instance = None

    if request.method == 'POST':
        form = APIKeyForm(request.POST, instance=api_key_instance)
        if form.is_valid():
            api_key = form.save(commit=False)  # 不直接保存，先进行其他操作
            if not api_key_instance:  # 如果没有现有API Key，关联当前用户
                api_key.user = request.user
            api_key.save()  # 保存API Key
            messages.success(request, "API Key has been saved successfully.")
            return redirect('home')  
    else:
        form = APIKeyForm(instance=api_key_instance)

    return render(request, 'users/set_api_key.html', {'form': form})


@login_required
@csrf_exempt
def chatglm_view(request):
    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        try:
            api_key = APIKey.objects.get(user=request.user).api_key 
        except APIKey.DoesNotExist:
            return redirect('set_api_key')
        client = ZhipuAI(api_key=api_key) 
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": llm_process_event_prompt},
                {"role": "user", "content": user_input}
            ],
        )
        # print(response.choices[0].message) # for debug
        print(llm_process_event_prompt) # for debug
        return JsonResponse({"response": response.choices[0].message.content})

    return render(request, 'llmagent/chat.html')

