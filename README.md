# ITMA

## 项目说明

### 1. `itma/`
项目包，包含项目的全局配置文件，例如：
- `settings.py`: 项目配置文件
- `urls.py`: 全局 URL 路由配置

### 2. `system/`
用户登录与身份验证模块，主要功能包括：
- 用户注册、登录、注销功能

### 3. `taskcalendar/`
日历与任务管理模块，主要功能包括：
- **日历视图**：按日、周、月查看任务
- **任务管理**：任务的增删改查功能

### 4. `llmagent/`
大模型助手功能模块，主要功能包括：
- **`prompts.py`**: 存放提示词文件

### 5. `templates/`
模板文件目录，包含以下内容：
- **`users/`**: 包含用户登录、注册页面，以及设置大模型 `API Key` 的页面
- **`llmagent/`**: 包含大模型聊天界面
- **`taskcalendar/`**: 包含日历界面
- **`home.html`**: 项目的主页(目前主页继承了base.html)
- **`base.html`**: 用于计划表和大模型交互界面的基础模板

---

## 运行

项目使用 MySQL 作为数据库（可根据需要修改数据库类型）。运行步骤如下：

1. 根据 `itma/settings.py` 中的配置，确保 MySQL 数据库已启动并正确配置。
2. 运行以下命令迁移数据库：

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. 启动开发服务器：
   ```bash
   python manage.py runserver
   ```

---


