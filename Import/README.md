# 数据导入说明
- 测试环境导入
- 数据量巨大，请下载到服务器运行
- 服务器下载数据慢可以先购买一个按需付费的ip
- path.py填写数据路径
- parallel_bulk有内存泄漏风险
- 我们的elasticsearch.yml配置如下
  ```yaml
    cluster.name: "nobc"
    network.host: 0.0.0.0
    http.cors.enabled: true
    http.cors.allow-origin: "*"
    bootstrap.memory_lock: true
    #xpack请在上线时开启
    #xpack.security.enabled: true
    #xpack.security.transport.ssl.enabled: true
    
    indices.memory.index_buffer_size: 20%
    indices.memory.min_index_buffer_size: 96mb
  ```
- 服务器配置为8核64G,负载1.4T本地盘
- jvm.options分配给elasticsearch的内存为31g