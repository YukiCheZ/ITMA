import json

from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Events


def taskcalendar(request):
    all_events = Events.objects.all()
    context = {
        "events": all_events,
    }
    return render(request, 'taskcalendar/taskcalendar.html', context)
 
 
def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
            'finished': event.finished,
        })
    return JsonResponse(out, safe=False)

 
def show_all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
            'finished': event.finished,
        })
    return render(request, 'taskcalendar/event_list.html', {'events': out})
 
 
def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(name=str(title), start=start, end=end)
    event.save()
    data = {}
    return JsonResponse(data)
 
 
def update(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.start = start
    event.end = end
    event.name = title
    event.save()
    data = {}
    return JsonResponse(data)
 
 
def remove(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.delete()
    data = {}
    # return JsonResponse(data, status=403)
    return JsonResponse(data)


from django.utils.decorators import method_decorator
@method_decorator(csrf_exempt, name='dispatch')
class UpdateEventsView(View):
    def post(self, request, *args, **kwargs):
        print("Enter!!!!")
        try:
            data = json.loads(request.body)

            try:
                title = data.get("title")
                start = data.get("start")
                end = data.get("end")
                # for debug:
                print(f"Title: {title}")
                print(f"Start: {start}")
                print(f"End: {end}")    
            except Exception as e:
                return JsonResponse({"error": "大模型信息解析错误，请用户检查输入信息是否有误。"}, status=400)

            event, created = Events.objects.get_or_create(
                name=title, 
                start=start, 
                end=end,
                defaults={"finished": False}
            )

            if created:
                return JsonResponse({"message": "事件创建成功"}, status=201)
            else:
                return JsonResponse({"message": "事件创建失败，事件已经存在"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)