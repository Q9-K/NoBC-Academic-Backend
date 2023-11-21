import os

app_list = ['manager', 'message', 'work', 'author', 'user']
for app in app_list:
    path = os.path.join(os.getcwd(), app, 'migrations')
    # 创建迁移文件夹
    if not os.path.exists(path):
        os.mkdir(path)
        print('create dir: %s' % path)

    # 创建__init__.py文件
    init_file_path = os.path.join(path, '__init__.py')
    if not os.path.exists(init_file_path):
        with open(init_file_path, 'w') as f:
            f.write('')
            print('create file: %s' % init_file_path)
