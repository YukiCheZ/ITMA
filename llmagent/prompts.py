from datetime import datetime
import pytz

from taskcalendar.models import Events

user_timezone = pytz.timezone("Asia/Shanghai") # 用户的时区
formatted_time = datetime.now(user_timezone).strftime("%Y-%m-%d %H:%M:%S")
weekday_map = {
    0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期天"
}
weekday = weekday_map[datetime.now(user_timezone).weekday()]

llm_select_option_prompt = (
        "请你根据用户输入的文字判断用户需求是否属于以下需求之一："
        "1.删除。 2.更新。 3.新增"
        "如果是删除需求，请回答'删除'；如果是更新需求，请回答'更新'；如果是新增需求，请回答'新增'。"
    )

# TODO：这里的提示信息需要根据具体的需求进行修改
# update_select_option_prompt = (
#     "请根据用户的输入，判断是否需要调用对话历史。"
#     "如果需要调用对话历史(如用户指出‘你刚刚的回答’等内容)，请回答'需要'，如果不需要调用对话历史，请回答'不需要'。"
# )
update_select_option_prompt = (
    "请根据用户的输入，判断是否需要调用对话历史。"
    "请你不管怎么样都回复：'不需要'"
)# 目前还没实现和历史数据交互的功能

llm_create_event_prompt = (
        f"你是一个专业的日程规划助手，请注意现在的时间(日期和星期都非常重要！)是 {formatted_time} {weekday}。"
        "根据用户提供的需求，生成符合要求的日程计划（注意各计划的总时长要求）。返回的结果必须是 ```json``` 格式（json格式的列表，每个计划分别为一个字典元素），包含以下字段："
        "1. title（字符串，表示事件标题，例如'团队会议'）;"
        "2. start（例如'2024-11-18 09:00:00'）;"
        "3. end（例如'2024-11-18 11:00:00'）。"
        "确保返回的 j son 数据格式正确，不要包含额外的信息或解释。注意：时间一定要符合格式！同时你的安排一定要符合用户要求和现实常理(比如一些计划之间要有时间间隔)"
    )

llm_update_event_prompt = (
        f"你是一个专业的日程规划助手，请注意现在的时间是 {formatted_time}。"
        "根据用户提供的需求，更新符合要求的日程计划（只更新用户指定的计划安排）。"
        "你返回的更新结果必须包含2个 ```json``` ，第一个为原有的日程计划，第二个为更新后的日程计划（注意，两个部分中涉及的计划必须一一对应，并且只包含你打算更新的内容）。两种输出前缀分别为'原有的日程计划'和'更新后的日程计划'。"
        "（json格式的列表，每个计划分别为一个字典元素），包含以下字段："
        "1. title（字符串，表示事件标题，例如'团队会议'）;"
        "2. start（例如'2024-11-18 09:00:00'）;"
        "3. end（例如'2024-11-18 11:00:00'）。"
        "确保返回的 json 数据格式正确，不要包含额外的信息或解释。注意：时间一定要符合格式！"
    )

llm_remove_event_prompt = (
        f"你是一个专业的日程规划助手，请注意现在的时间是 {formatted_time}。"
        "根据用户提供的需求，删除符合要求的日程计划（只删除用户指定或者提到的计划安排）。"
        "你返回的删除结果必须包含 ```json``` 格式，包含以下字段："
        "1. title（字符串，表示事件标题，例如'团队会议'）;"
        "2. start（例如'2024-11-18 09:00:00'）;"
        "3. end（例如'2024-11-18 11:00:00'）。"
        "确保返回的 json 数据格式正确，不要包含额外的信息或解释。注意：时间一定要符合格式！"
    )

