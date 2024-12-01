from datetime import datetime
import pytz

from taskcalendar.models import Events

user_timezone = pytz.timezone("Asia/Shanghai") # 用户的时区
formatted_time = datetime.now(user_timezone).strftime("%Y-%m-%d %H:%M:%S")

exist_events = Events.get_all_events()

llm_select_option_prompt = (
        "请你根据用户输入的文字判断用户需求是否属于以下需求之一："
        "1.删除。 2.更新。 3.新增"
        "如果是删除需求，请回答'删除'；如果是更新需求，请回答'更新'；如果是新增需求，请回答'新增'。"
    )

llm_create_event_prompt = (
        "你是一个专业的日程规划助手，请注意现在的时间是 {formatted_time}。"
        "根据用户提供的需求，生成符合要求的日程计划。返回的结果必须是 JSON 格式（json格式的列表，每个计划分别为一个字典元素），包含以下字段："
        "1. title（字符串，表示事件标题，例如'团队会议'）;"
        "2. start（例如'2024-11-18 09:00:00'）;"
        "3. end（例如'2024-11-18 11:00:00'）。"
        "确保返回的 JSON 数据格式正确，不要包含额外的信息或解释。注意：时间一定要符合格式！同时你的安排一定要符合用户要求和现实常理(比如一些计划之间要有时间间隔)"
        # "以下是一个示例："
        # '{{'
        # '"title": "团队会议", '
        # '"start": "2024-11-18 09:00:00", '
        # '"end": "2024-11-18 11:00:00"'
        # '}}。'
        # "下面为目前已经安排的计划，请你甄别日期，确保新的计划不会与已有计划在时间上重叠（也就是说你给出的计划不能同时满足："
        # "开始时间早于一个已有计划的结束时间并且结束时间晚于这个已有计划的开始时间，如果无法进行安排，请回答：日程太满，不能进行安排）："
        # "{exist_events}"
    ).format(formatted_time=formatted_time, exist_events=exist_events)

