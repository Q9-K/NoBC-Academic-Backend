import time
import threading
import ujson
import pymysql

# 创建数据库连接
db = pymysql.connect(host='127.0.0.1',
                     user='root',
                     password='root',
                     database='NoBC',
                     )
cursor = db.cursor()

def process_paper(filename):
    print(1)
    # 开始时间
    start_time = time.time()
    print('------------------开始处理' + filename + '------------------')
    data_all = []

    with open(filename, 'r') as file:
        line_num = 0
        for line in file:
            line_num = line_num + 1
            if line_num % 1000 == 0:
                print(line_num)

            item = ujson.loads(line)
            _id = ''
            if item.get('id') is not None:
                _id = item.get('id')

            _title = ''
            if item.get('title') is not None:
                _title = item.get('title')

            _year = 0
            if item.get('year') is not None:
                _year = item.get('year')

            _n_citation = 0
            if item.get('n_citation') is not None:
                _n_citation = item.get('n_citation')

            _doc_type = ''
            if item.get('doc_type') is not None:
                _doc_type = item.get('doc_type')

            _publisher = ''
            if item.get('publisher') is not None:
                _publisher = item.get('publisher')

            _volume = ''
            if item.get('volume') is not None:
                _volume = item.get('volume')

            _issn = ''
            if item.get('issn') is not None:
                _issn = item.get('issn')

            _isbn = ''
            if item.get('isbn') is not None:
                _isbn = item.get('isbn')

            _doi = ''
            if item.get('doi') is not None:
                _doi = item.get('doi')

            _pdf = ''
            if item.get('pdf') is not None:
                _pdf = item.get('pdf')

            _url = ''
            if item.get('url') is not None:
                _url = item.get('url')

            _abstract = ''
            if item.get('abstract') is not None:
                _abstract = item.get('abstract')

            data = (_id, _title, _year, _n_citation, _doc_type, _publisher, _volume, _issn, _isbn, _doi, _pdf, _url, _abstract)
            data_all.append(data)

    # 结束时间
    end_time = time.time()
    print('组装数据' + filename + '结束, 耗时' + str(end_time - start_time) + '秒')

    sql = 'INSERT INTO paper_paper VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    try:
        start_time1 = time.time()
        print('开始插入数据')
        cursor.executemany(sql, data_all)
        db.commit()
        print('插入数据成功，共' + str(len(data_all)) + '条')
        end_time1 = time.time()
        print('插入数据' + filename + '结束, 耗时' + str(end_time1 - start_time1) + '秒')

        # 总耗时
        print('总耗时' + str(end_time1 - start_time) + '秒')
        # 平均每秒插入数据
        print('平均每秒插入数据' + str(len(data_all) / (end_time1 - start_time)) + '条')
    except Exception as ex:
        print("出现如下异常%s" % ex)
        db.rollback()
        print('插入数据失败，已回滚插入失败的部分' + filename)

    # 关闭文件
    file.close()
    print('------------------结束处理' + filename + '------------------')


def process_author(filename):
    # 开始时间
    start_time = time.time()
    print('------------------开始处理' + filename + '------------------')
    data_all = []

    with open(filename, 'r') as file:
        line_num = 0
        for line in file:
            line_num = line_num + 1
            if line_num % 10000 == 0:
                print(line_num)

            item = ujson.loads(line)
            _id = ''
            if item.get('id') is not None:
                _id = item.get('id')

            _name = ''
            if item.get('name') is not None:
                _name = item.get('name')

            _orgs = ''
            if item.get('orgs') is not None:
                # 遍历Orgs, 拼接成字符串
                for org in item.get('orgs'):
                    _orgs = org + ' '

            _last_org = ''
            if item.get('org') is not None:
                _last_org = item.get('org')

            _position = ''
            if item.get('position') is not None:
                _position = item.get('position')

            _n_pubs = 0
            if item.get('n_pubs') is not None:
                _n_pubs = item.get('n_pubs')

            _n_citation = 0
            if item.get('n_citation') is not None:
                _n_citation = item.get('n_citation')

            _h_index = 0
            if item.get('h_index') is not None:
                _h_index = item.get('h_index')

            data = (_id, _name, _orgs, _last_org, _position, _n_pubs, _n_citation, _h_index)

            data_all.append(data)

            if len(data_all) % 1000000 == 0:
                print('---------------------')
                sql = 'INSERT INTO scholar_scholar VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
                try:
                    start_time1 = time.time()
                    print('开始插入数据')
                    cursor.executemany(sql, data_all)
                    db.commit()
                    print('插入数据成功，共' + str(len(data_all)) + '条')
                    end_time1 = time.time()
                    print('插入数据' + filename + '结束, 耗时' + str(end_time1 - start_time1) + '秒')

                    # 总耗时
                    print('总耗时' + str(end_time1 - start_time) + '秒')
                    # 平均每秒插入数据
                    print('平均每秒插入数据' + str(len(data_all) / (end_time1 - start_time)) + '条')
                except Exception as ex:
                    print("出现如下异常%s" % ex)
                    db.rollback()
                    print('插入数据失败，已回滚插入失败的部分' + filename)

                data_all = []

    # 结束时间
    end_time = time.time()
    print('组装数据' + filename + '结束, 耗时' + str(end_time - start_time) + '秒')

    # 关闭文件
    file.close()
    print('------------------结束处理' + filename + '------------------')


if __name__ == '__main__':
    start_time_all = time.time()

    # 目前使用的是方法一，串行执行=-=
    # 个人倾向于方法三中的多窗口执行，但是要改代码QAQ

    # 方法一：串行执行
    # 0、cursor.executemany()批量插入数据的最佳数据量是多少？？？一次性插入所有数据，还是一个文件插一次或是更细粒度？？？
    for i in range(2, 3):
        filename = 'D:\\mag_authors_0\\mag_authors_' + str(i) + '.txt'
        process_author(filename)

    # 方法二：多线程执行
    # 0、真的会快吗o.O?
    #   瓶颈在于数据库插入，如果每个线程中使用独立的数据库连接，就可以并行插入mysql
    # 1、会不会插入mysql时存在问题？？？总的插入条数直接在mysql里面查
    #   gpt: 确保在每个线程中使用独立的数据库连接。数据库连接通常是线程不安全的，因此每个线程应该有自己的连接实例，避免多个线程共享同一个连接。这可以防止潜在的并发问题和数据混乱。
    # 2、控制台输出会不会乱掉？？？可以尝试写入不同的log文件来记录
    # for i in range(1, 6):
    #     filename = 'G:\\aminer_authors_' + str(i) + '.txt'
    #     t = threading.Thread(target=process_author, args=(filename,))
    #     t.start()
    #     t.join()

    # 方法三：多进程执行 multiprocessing vs 多窗口执行
    # 0、不如直接同时运行多个程序，将文件名作为参数传入？？？
    # 1、这样好像每个程序使用的是独立的数据库连接，相比于多线程实现起来简单？？？
    # 2、多窗口的话，print好像也不会乱掉？？？
    # for i in range(1, 6):
    #     filename = 'G:\\aminer_authors_' + str(i) + '.txt'
    #     p = multiprocessing.Process(target=process_author, args=(filename,))
    #     p.start()
    #     p.join()

    end_time_all = time.time()
    print('插入author数据总共耗时' + str(end_time_all - start_time_all) + '秒')
