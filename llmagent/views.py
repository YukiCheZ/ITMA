import re
import json

from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from openai import OpenAI
from zhipuai import ZhipuAI

from .prompts import *
from .models import APIKey
from taskcalendar.models import Events
from .forms import APIKeyForm

temporal_history = list()
openai_model = "gpt-4o"

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
        
        zhipu_client = ZhipuAI(api_key=api_key) 
        openai_client = OpenAI()     
        exist_events =  Events.get_all_events(request.user)
        # print("exist_events:", exist_events)
        # print('llm_create_event_prompt:', llm_create_event_prompt)
        response_preprocess = zhipu_client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": llm_select_option_prompt},
                {"role": "user", "content": user_input}
            ],
        )
        print(response_preprocess.choices[0].message) # for debug

        if response_preprocess.choices[0].message.content == "新增":
            response = openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": llm_create_event_prompt + f"目前已经有的安排是这样的（请不要与已有安排的时间重复）:{exist_events}"},
                    {"role": "user", "content": user_input}
                ]
            )
            print(llm_create_event_prompt + f"目前已经有的安排是这样的（请不要与已有安排的时间重复）:{exist_events}")
            print(response.choices[0].message) # for debug
            # print(llm_process_event_prompt) # for debug
            arrangements = response.choices[0].message.content
            pattern = "```json(.*?)```" # 大模型生成的回复有这个前后缀
            arrangements =  re.findall(pattern, arrangements, re.DOTALL)[0].strip().replace("/", "-")
            temporal_history.append(
                dict(
                    round = len(temporal_history) + 1,
                    user_input = user_input,
                    response = arrangements 
                )
            )
            arrangements = json.loads(arrangements)
            try:
                create_events_with_model_response(arrangements, request.user) 
                return JsonResponse({"response": f"成功更新计划表，请检查！我的安排为：{arrangements}"})
            
            except Exception as e:
                return JsonResponse({"error": "大模型信息解析错误，请用户检查输入信息是否有误。"}, status=400)
            

        if response_preprocess.choices[0].message.content == "更新":
            print("更新")
            update_method = zhipu_client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": update_select_option_prompt},
                    {"role": "user", "content": user_input}
                ],
            )
            print("update_method:", update_method.choices[0].message.content)
            # 这个功能为TODO，待实现，应该需要把历史记录存在数据库中
            if update_method.choices[0].message.content == "需要" and len(temporal_history) != 0:
                print("需要调用对话历史")
                llm_prompt = (
                    f"{llm_update_event_prompt}"
                    f"目前已经有的安排是这样的（请不要与已有安排的时间重复）:{exist_events}"
                    f"其中，你之前一轮的对话给出的结果为：{temporal_history[-1].response}"
                )
                
                response = openai_client.chat.completions.create(
                    model=openai_model,
                    messages=[
                        {"role": "system", "content": llm_prompt},
                        {"role": "user", "content": user_input}
                    ]
                )
                print("llm_prompt:", llm_prompt)
                

            elif update_method.choices[0].message.content == "不需要":
                print("不需要调用对话历史")
                llm_prompt = (
                    f"{llm_update_event_prompt}"
                    f"你需要从已有的安排里面挑选用户指定的计划进行更新，目前已经有的安排是这样的（请不要与已有安排的时间重复）"
                    f":{exist_events}"
                )
                response = openai_client.chat.completions.create(
                    model=openai_model,
                    messages=[
                        {"role": "system", "content": llm_prompt},
                        {"role": "user", "content": user_input}
                    ]
                )
                print(llm_prompt)
            
            arrangements = response.choices[0].message.content
            # print(arrangements)
            pattern = "```json(.*?)```" # 大模型生成的回复有这个前后缀
            before =  re.findall(pattern, arrangements, re.DOTALL)[0].strip().replace("/", "-")
            after = re.findall(pattern, arrangements, re.DOTALL)[1].strip().replace("/", "-")
            # print(before)
            # print(after)
            before = json.loads(before)
            after = json.loads(after)
            print("原有的计划： ", before)
            print("更新后的计划：",after)
            try:
                remove_events_with_model_response(before, request.user)
                create_events_with_model_response(after, request.user)
                return JsonResponse({"response": f"成功更新计划表，请检查！原有的计划为：{before}，更新后的计划为：{after}"})
            except Exception as e:
                return JsonResponse({"error": "大模型信息解析错误，请用户检查输入信息是否有误。"}, status=400)
            
        if response_preprocess.choices[0].message.content == "删除":
            print("删除")
            response = openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": llm_remove_event_prompt + f"目前已经有的安排是这样的:{exist_events}"},
                    {"role": "user", "content": user_input}
                ]
            )
            print(llm_remove_event_prompt + f"目前已经有的安排是这样的:{exist_events}")
            arrangements = response.choices[0].message.content
            pattern = "```json(.*?)```"
            arrangements =  re.findall(pattern, arrangements, re.DOTALL)[0].strip().replace("/", "-")
            arrangements = json.loads(arrangements)
            print("需要删除的内容：", arrangements)
            try:
                remove_events_with_model_response(arrangements, request.user)
                return JsonResponse({"response": f"成功更新计划表，请检查！删除的计划为：{arrangements}"})
            except Exception as e:
                return JsonResponse({"error": "大模型信息解析错误，请用户检查输入信息是否有误。"}, status=400)

        
    return render(request, 'llmagent/chat.html')


def remove_events_with_model_response(model_responses, user):
    try:
        datas = [model_responses] if not isinstance(model_responses, list) else model_responses
        for data in datas:
            try:
                title = data.get("title")
                start = datetime.strptime(data.get("start"), "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(data.get("end"), "%Y-%m-%d %H:%M:%S")
            
            except Exception as e:
                raise e

            start_aware = timezone.make_aware(start) if start else None
            end_aware = timezone.make_aware(end) if end else None
            print("delete:", Events.objects.filter(user=user, name=title, start=start_aware, end=end_aware))
            Events.objects.filter(user=user, name=title, start=start_aware, end=end_aware).delete()

    except Exception as e:
        raise e
        

def create_events_with_model_response(model_responses, user):
    try:
        datas = [model_responses] if not isinstance(model_responses, list) else model_responses
        for data in datas:
            try:
                title = data.get("title")
                start = datetime.strptime(data.get("start"), "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(data.get("end"), "%Y-%m-%d %H:%M:%S")
            
            except Exception as e:
                raise e
        
            start_aware = timezone.make_aware(start) if start else None
            end_aware = timezone.make_aware(end) if end else None

            event, created = Events.objects.get_or_create(
                user=user,
                name=title,
                start=start_aware,  
                end=end_aware,     
                defaults={"finished": False}
            )

            print("event ", event)
        
    except Exception as e:
        raise e
        

