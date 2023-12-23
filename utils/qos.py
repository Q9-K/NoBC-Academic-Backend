from qiniu import Auth, put_file, etag, BucketManager
from config import ACCESS_KEY, SECRET_KEY, BUCKET_NAME, BASE_URL


def upload_file(key: str, file_path) -> bool:
    """
    上传文件
    :param key: 上传的文件保存的文件名
    :param file_path: 要上传的文件在本地的存储路径
    :return: 重名False,否则上传成功True
    """
    # 构建鉴权对象
    q = Auth(ACCESS_KEY, SECRET_KEY)
    # 检查是否重名
    bucket = BucketManager(q)
    ret, info = bucket.stat(BUCKET_NAME, key)
    # 如果存在则删除
    if ret:
        ret, info = bucket.delete(BUCKET_NAME, key)
        if ret:
            assert ret == {}
        else:
            return False
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(BUCKET_NAME, key, 3600)
    # 要上传文件的本地路径
    local_file = file_path
    ret, info = put_file(token, key, local_file)
    if ret:
        assert ret['key'] == key
        assert ret['hash'] == etag(local_file)
        return True
    return False


def get_file(key: str) -> str:
    """
    获取文件
    :param key: 文件名
    :return: url
    """
    # 检查是否存在
    q = Auth(ACCESS_KEY, SECRET_KEY)
    bucket = BucketManager(q)
    ret, info = bucket.stat(BUCKET_NAME, key)
    if not ret:
        return ''
    # 生成下载链接
    url = BASE_URL + key
    return q.private_download_url(url, expires=3600)


def delete_file(key: str) -> bool:
    """
    删除文件
    :param key: 文件名
    :return: 删除成功True,否则False
    """
    q = Auth(ACCESS_KEY, SECRET_KEY)
    bucket = BucketManager(q)
    ret, info = bucket.delete(BUCKET_NAME, key)
    if ret:
        assert ret == {}
        return True
    else:
        return False


if __name__ == '__main__':
    # upload_file("default_institution.png", "./default_institution.png")
    print(get_file("语境（考古学）.png"))
