from __future__ import absolute_import, unicode_literals

# 这将确保应用总是导入时
# 总是会导入 shared_task，这样如果你想使用
# shared_task 将确保你总是在你的项目中使用它
# 在你的项目中。
from .celery import app as celery_app


__all__ = ('celery_app',)
