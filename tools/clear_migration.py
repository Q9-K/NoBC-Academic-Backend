# 遍历当前目录文件夹，找到所有的迁移文件，然后清空迁移文件中的内容
import os
# 获取当前目录
current_path = os.getcwd()
# 获取当前目录下的所有文件夹
dirs = os.listdir(current_path)
# 遍历所有文件夹
for tmp_dir in dirs:
    # 判断是否为文件夹
    if os.path.isdir(tmp_dir):
        # 获取迁移文件夹的路径
        migration_path = os.path.join(current_path, tmp_dir, 'migrations')
        if os.path.isdir(migration_path):
            # 获取迁移文件夹下的所有文件
            migration_files = os.listdir(migration_path)
            # 遍历所有文件
            for migration_file in migration_files:
                # 判断是否为迁移文件，保留__init__.py文件
                if migration_file.startswith('00'):
                    # 获取迁移文件的路径
                    migration_file_path = os.path.join(migration_path, migration_file)
                    os.remove(migration_file_path)
                    print('remove file: %s' % migration_file_path)
