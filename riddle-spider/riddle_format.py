import pymysql
import traceback

# 源数据库配置
SOURCE_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'riddle_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 目标数据库配置
TARGET_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'wechat-riddle-db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 需要筛选的谜语类型
TARGET_TYPES = {
    '植物': 1,
    '动物': 2,
    '水果': 3,
    '蔬菜': 4,
    '交通工具': 5,
    '日常用品': 6
}

def create_target_database():
    """创建目标数据库和表结构"""
    try:
        # 连接MySQL服务器（不指定数据库）
        conn = pymysql.connect(
            host=TARGET_DB_CONFIG['host'],
            user=TARGET_DB_CONFIG['user'],
            password=TARGET_DB_CONFIG['password'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS `wechat-riddle-db` DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # 选择数据库
        cursor.execute("USE `wechat-riddle-db`")
        
        # 创建riddle_type表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS riddle_type (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_type (type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 创建riddle表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS riddle (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            riddle VARCHAR(500) NOT NULL,
            answer VARCHAR(255) NOT NULL,
            riddle_type_id INT UNSIGNED,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_riddle (riddle),
            FOREIGN KEY (riddle_type_id) REFERENCES riddle_type(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        cursor.close()
        conn.close()
        print("目标数据库和表结构创建成功")
        return True
    except Exception as e:
        print(f"创建目标数据库时出错: {e}")
        traceback.print_exc()
        return False

def transfer_data():
    """传输数据：从源数据库筛选指定类型的谜语并写入目标数据库"""
    try:
        # 连接源数据库
        source_conn = pymysql.connect(**SOURCE_DB_CONFIG)
        source_cursor = source_conn.cursor()
        
        # 连接目标数据库
        target_conn = pymysql.connect(**TARGET_DB_CONFIG)
        target_cursor = target_conn.cursor()
        
        # 首先插入目标类型到riddle_type表
        for type_name, type_id in TARGET_TYPES.items():
            try:
                # 使用INSERT IGNORE避免重复插入
                target_cursor.execute(
                    "INSERT IGNORE INTO riddle_type (id, type) VALUES (%s, %s)",
                    (type_id, type_name)
                )
                if target_cursor.rowcount > 0:
                    print(f"插入谜语类型: {type_name} (ID: {type_id})")
            except Exception as e:
                print(f"插入类型 {type_name} 时出错: {e}")
        target_conn.commit()
        
        # 从源数据库查询并筛选指定类型的谜语
        source_cursor.execute(
            """SELECT r.id, r.riddle, r.answer, rt.type 
             FROM riddle r 
             JOIN riddle_type rt ON r.riddle_type_id = rt.id 
             WHERE rt.type IN (%s, %s, %s, %s, %s, %s)""",
            tuple(TARGET_TYPES.keys())
        )
        
        riddles = source_cursor.fetchall()
        print(f"找到 {len(riddles)} 条符合条件的谜语")
        
        # 插入到目标数据库
        inserted_count = 0
        for riddle in riddles:
            try:
                # 获取目标数据库中的类型ID
                source_type = riddle['type']
                target_type_id = TARGET_TYPES.get(source_type)
                
                if target_type_id:
                    # 插入谜语数据
                    target_cursor.execute(
                        "INSERT IGNORE INTO riddle (riddle, answer, riddle_type_id) VALUES (%s, %s, %s)",
                        (riddle['riddle'], riddle['answer'], target_type_id)
                    )
                    if target_cursor.rowcount > 0:
                        inserted_count += 1
                        if inserted_count % 100 == 0:
                            print(f"已插入 {inserted_count} 条谜语")
                            target_conn.commit()
            except Exception as e:
                print(f"插入谜语时出错: {e}")
                continue
        
        # 提交剩余的数据
        target_conn.commit()
        
        # 关闭连接
        source_cursor.close()
        source_conn.close()
        target_cursor.close()
        target_conn.close()
        
        print(f"数据传输完成，成功插入 {inserted_count} 条谜语")
        return True
    except Exception as e:
        print(f"传输数据时出错: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始准备目标数据库...")
    if not create_target_database():
        print("创建目标数据库失败，程序终止")
        return
    
    print("\n开始传输数据...")
    transfer_data()
    
    print("\n所有操作完成")

if __name__ == "__main__":
    main()