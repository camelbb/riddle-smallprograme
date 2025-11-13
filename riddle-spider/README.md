# 谜语网站爬虫项目

## 项目目的

本项目是一个Python爬虫程序，用于爬取谜语网站的内容并将其存储到MySQL数据库中。具体功能包括：

- 按页爬取谜语网站内容
- 提取谜语、谜语类型和谜底信息
- 在终端输出爬取结果
- 将数据存储到MySQL数据库
- 在存储前进行去重校验
- 每页爬完后休眠2秒，避免对服务器造成过大压力

## 项目结构

```
spider-python/
├── riddle_spider.py  # 主爬虫程序
├── requirements.txt  # 项目依赖包
├── riddle.sql  # MySQL建表语句
└── README.md  # 项目说明文档
```

## 安装步骤

### 1. 安装依赖包

```bash
pip install -r requirements.txt
```

### 2. 配置MySQL数据库

1. 确保已安装MySQL数据库
2. 编辑 `riddle_spider.py` 文件，修改数据库连接配置：

```python
# MySQL数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # 修改为你的MySQL用户名
    'password': 'your_password',  # 修改为你的MySQL密码
    'database': 'riddle_db',  # 数据库名
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
```

3. 执行SQL脚本创建数据库和表：
所需表结构已放在 riddle.sql 文件中

```bash
mysql -u root -p < riddle.sql
```
