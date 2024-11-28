import re

import json
import requests

from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from zhipuai import ZhipuAI

from .prompts import *
from .models import APIKey
from .forms import APIKeyForm

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
        # print(llm_process_event_prompt) # for debug
        try:
            update_calendar_with_model_response(response.choices[0].message.content) 
            return JsonResponse({"response": f"成功更新计划表，请检查！我的安排为：{response.choices[0].message.content}"})
        
        except Exception as e:
            return JsonResponse({"error": "大模型信息解析错误，请用户检查输入信息是否有误。"}, status=400)

    return render(request, 'llmagent/chat.html')


@csrf_exempt
def update_calendar_with_model_response(model_responses):
    # 获取当前站点域名
    # current_site = Site.objects.get_current()
    # base_url = f"http://{current_site.domain}"  # 动态获取域名
    base_url = "http://127.0.0.1:8000"
    # 动态获取 API 路径
    api_path = reverse('update_events_by_llm')
    full_url = f"{base_url}{api_path}"

    # 发送请求
    headers = {"Content-Type": "application/json"}

    pattern = "```json(.*?)```"
    clean_responses =  re.findall(pattern, model_responses, re.DOTALL)[0]
    clean_responses = json.loads(clean_responses)
    print(clean_responses)
    for index, model_response in enumerate(clean_responses):
        print(f'{index}: ', model_response)
        response = requests.post(full_url, headers=headers, json=model_response)
        print(full_url)
        print(response)
        if response.status_code == 201:
            print("Event created successfully")
        elif response.status_code == 200:
            print("Event already exists")
        else:
            print(f"Failed to update calendar")