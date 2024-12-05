from django.shortcuts import get_object_or_404, render
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
    all_events = Events.get_all_events(request.user) 
    return JsonResponse(all_events, safe=False)

 
def show_all_events(request):
    all_events = Events.get_all_events(request.user)
    return render(request, 'taskcalendar/event_list.html', {'events': all_events})
 
 
def add_event(request):
    user = request.user
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(user = user, name=str(title), start=start, end=end)
    event.save()
    data = {}
    return JsonResponse(data)
 
 
def update(request):
    user = request.user
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.user = user
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

@csrf_exempt 
def mark_completed(request):
    event_id = request.POST.get("id", None)
    if not event_id:
        return JsonResponse({'error': 'Event ID is required'}, status=400)
    event = get_object_or_404(Events, id=event_id)
    if event.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    event.finished = True
    event.save()
    return JsonResponse({'message': 'Event marked as completed successfully'}, status=200)




