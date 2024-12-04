import re
import json

from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from zhipuai import ZhipuAI

from .prompts import *
from .models import APIKey
from taskcalendar.models import Events
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
        exist_events =  Events.get_all_events()
        # print("exist_events:", exist_events)
        # print('llm_create_event_prompt:', llm_create_event_prompt)
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": llm_create_event_prompt},
                {"role": "user", "content": user_input}
            ],
        )
        # print(response.choices[0].message) # for debug
        # print(llm_process_event_prompt) # for debug
        arrangements = response.choices[0].message.content
        pattern = "```json(.*?)```" # 大模型生成的回复有这个前后缀
        arrangements =  re.findall(pattern, arrangements, re.DOTALL)[0]
        arrangements = json.loads(arrangements)

        try:
            update_calendar_with_model_response(arrangements) 
            return JsonResponse({"response": f"成功更新计划表，请检查！我的安排为：{arrangements}"})
        
        except Exception as e:
            return JsonResponse({"error": "大模型信息解析错误，请用户检查输入信息是否有误。"}, status=400)

    return render(request, 'llmagent/chat.html')


def update_calendar_with_model_response(model_responses):
    try:
        datas = model_responses
        for data in datas:
            try:
                title = data.get("title")
                start = datetime.strptime(data.get("start"), "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(data.get("end"), "%Y-%m-%d %H:%M:%S")
            
            except Exception as e:
                raise e
        
            # overlap_events = check_time_overlap(start, end)
            # if check_time_overlap(start, end).exists():
            #     conflict_events = [
            #         {
            #             "id": event.id,
            #             "title": event.name,
            #             "start": event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            #             "end": event.end.strftime("%m/%d/%Y, %H:%M:%S"),
            #             "finished": event.finished,
            #         }
            #         for event in overlap_events
            #     ]
            #     return JsonResponse({"error": "时间段与已有事件重叠，请检查！", "conflict_events": conflict_events}, status=400)
            start_aware = timezone.make_aware(start) if start else None
            end_aware = timezone.make_aware(end) if end else None
            event, created = Events.objects.get_or_create(
                name=title,
                start=start_aware,  
                end=end_aware,     
                defaults={"finished": False}
            )
            print("event ", event)
        
    except Exception as e:
        raise e
        

from django.db.models import Q
def check_time_overlap(start, end):
    # 判断是否有事件与给定时间段重叠
    overlap = Events.objects.filter(
        Q(start__lt=end) &  # 新事件的开始时间早于已有事件的结束时间
        Q(end__gt=start)    # 新事件的结束时间晚于已有事件的开始时间
    )
    return overlap