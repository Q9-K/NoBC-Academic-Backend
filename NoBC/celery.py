from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# 设置 Django 设置模块的默认值。
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NoBC.settings')

app = Celery('NoBC')

# 使用字符串，这样 worker 不必序列化
# 配置对象到子进程。
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# 加载任何Django应用中注册的任务模块。
app.autodiscover_tasks()
