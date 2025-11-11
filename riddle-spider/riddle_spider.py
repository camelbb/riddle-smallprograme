from traceback import print_exc
import requests
from bs4 import BeautifulSoup
import pymysql
import time
import re

# MySQL数据库连接配置
# 注意：实际使用前请修改为正确的数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # 请修改为你的MySQL用户名
    'password': '',  # 请修改为你的MySQL密码
    'database': 'riddle_db',  # 数据库名
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 初始化数据库连接（简化版，假设数据库和表已通过riddle.sql创建）
def init_database():
    try:
        # 尝试连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 验证riddle表是否存在
        cursor.execute("SHOW TABLES LIKE 'riddle'")
        riddle_table = cursor.fetchone()
        
        # 验证riddle_type表是否存在
        cursor.execute("SHOW TABLES LIKE 'riddle_type'")
        riddle_type_table = cursor.fetchone()
        
        if not riddle_table or not riddle_type_table:
            print("错误：riddle表或riddle_type表不存在，请先执行riddle.sql文件创建数据库和表")
            cursor.close()
            conn.close()
            return False
        
        cursor.close()
        conn.close()
        print("数据库连接验证成功")
        return True
    except Exception as e:
        print(f"数据库连接验证失败: {e}")
        print("请先执行riddle.sql文件创建数据库和表")
        return False

# 检查谜语是否已存在
def is_riddle_exist(riddle):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查谜语是否已存在 - 使用模糊匹配
        sql = "SELECT COUNT(*) AS count FROM riddle_db.riddle WHERE riddle LIKE %s"
        cursor.execute(sql, (f"%{riddle}%",))
        count = cursor.fetchone()['count']
        cursor.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"检查谜语是否存在时出错: {e}")
        return False
    


# 查找谜语类型的id，如果类型没有则新增，有则直接返回id
def get_riddle_type_id(type_name):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查谜语类型是否已存在
        sql = "SELECT id FROM riddle_type WHERE type = %s"
        cursor.execute(sql, (type_name,))
        result = cursor.fetchone()
        
        if result:
            return result['id']
        else:
            # 新增谜语类型
            sql = "INSERT INTO riddle_type (type) VALUES (%s)"
            cursor.execute(sql, (type_name,))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"获取谜语类型ID时出错: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# 保存谜语到数据库
def save_to_database(riddle, riddle_type_name, answer):
    try:
        # 检查是否已存在
        if is_riddle_exist(riddle):
            print(f"谜语已存在，跳过存储: {riddle}")
            return False
        
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        riddle_type_id = None
        if riddle_type_name and riddle_type_name.strip():
            # 获取或创建谜语类型
            riddle_type_id = get_riddle_type_id(riddle_type_name.strip())
        
        # 插入数据
        sql = "INSERT INTO riddle (riddle, answer, riddle_type_id) VALUES (%s, %s, %s)"
        cursor.execute(sql, (riddle, answer, riddle_type_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        print(f"成功保存谜语到数据库")
        return True
    except Exception as e:
        print(f"保存谜语到数据库时出错: {e}")
        return False

# 爬取单页谜语
def crawl_page(page_id):
    url = f"http://miyu.shanxiyoudi.com/miyu.asp?pageid={page_id}"
    riddle = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'gb2312'  # 设置正确的编码
        
        if response.status_code != 200:
            print(f"请求页面失败: {page_id}, 状态码: {response.status_code}")
            return 0
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 调试信息：尝试查找特定表格
        target_table = soup.find('table',{'id':'chaciju'}).find_all('td')
        riddle_txt = ''
        riddle_asw = ''
        riddle_type = ''
        count = 0
        for i, td in enumerate(target_table):
            if i % 2 == 0:
                # 谜语文案
                riddle_txt = td.text.strip()
                riddle_type = extract_riddle_type(riddle_txt)
                # print(f"谜语: {riddle_txt}")
                # print(f"谜语类型: {riddle_type}")
            else:
                # 谜底
                riddle_asw= extract_answers_from_html(td)
                #print(f"谜底: {riddle_asw}")
                # 保存到数据库
                if riddle_txt and riddle_asw and len(riddle_txt) > 2 and len(riddle_asw) > 1:
                    isSave = save_to_database(riddle_txt, riddle_type, riddle_asw)
                    if isSave:
                        count += 1
        print(f"第 {page_id} 页爬取完成，共获取 {count} 条谜语")
        return count
    except Exception as e:
        print(f"爬取页面 {page_id} 时出错: {e}")
        # 打印部分页面内容用于调试
        if 'response' in locals():
            print("页面内容预览:", response.text[:200])
        return 0

# 解析谜底
def extract_answers_from_html(soup):
    answer= '' 
    # 查找所有包含onclick属性的input按钮
    button = soup.find('input', attrs={'onclick': True})
    if button:
        onclick = button['onclick']
        match = re.search(r"谜底：([^'\)\"]+)", onclick)
        if match:
            answer = match.group(1)
    return answer

# 解析谜语类型
def extract_riddle_type(riddle):
    riddle_type = ''
    # 预编译正则表达式提高性能
    pattern = re.compile(
        r"""
        ^(.*?)                       # 谜面部分 (非贪婪匹配)
        (?:                           # 非捕获组开始
            [\s(（【]*               # 可能的前置空白或括号
            (?:打一|猜一|谜底是)      # 分类前缀
            [\s:：]*                 # 可能的空白或冒号
            (                        # 捕获组开始 (分类内容)
                (?:                  # 处理书名号情况
                    《[^》]+》       # 书名号内容
                    [\w\u4e00-\u9fa5]* # 书名号后的分类词
                )                    # 或
                |                    # 普通分类情况
                [\w\u4e00-\u9fa5]+  # 中文字符和单词字符
                (?:类|类别|名称)?     # 可能的尾缀
            )                        # 捕获组结束
            [\s)）】。，：]*         # 可能的尾随标点
        )                             # 非捕获组结束
        $""", 
        re.VERBOSE | re.IGNORECASE
    )
    match = pattern.search(riddle)
    if match:
        # 提取谜面和分类
        riddle_type = match.group(2).strip()
        # 清理多余标点
        if riddle_type.endswith(('。', '，', '）', ')')):
            riddle_type = riddle_type[:-1]

    return riddle_type


# 主函数
def main():
    # 初始化数据库
    if not init_database():
        print("数据库未准备好，无法继续执行爬取任务")
        return
    
    # 定义要爬取的页面范围
    start_page = 1
    end_page = 406  # 先只爬取第2页，可根据需要修改
    
    total_count = 0
    
    for page_id in range(start_page, end_page + 1):
        count = crawl_page(page_id)
        total_count += count
        
        # 每页爬完后sleep2秒
        if page_id < end_page:
            print("休息2秒...")
            time.sleep(2)
    
    print(f"爬取任务完成，共获取 {total_count} 条谜语")

if __name__ == "__main__":
    main()