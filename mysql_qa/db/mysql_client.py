"""
    MySQL客户端
"""
# 导入 MySQL 连接库
import pymysql
# 导入pandas
import pandas as pd
# 导入路径操作库
import os
# 导入配置和日志
from base.config import config
from base.logger import logger


class MySQLClient:

    def __init__(self):
        try:
            # 初始化MySQL连接对象
            self.connection = pymysql.connect(
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE
            )
            # 创建游标
            self.cursor = self.connection.cursor()
            # 记录连接成功
            logger.info("MySQL 连接成功")
        except pymysql.MySQLError as e:
            # 记录连接失败
            logger.error(f"MySQL 连接失败: {e}")
            raise

    # 创建表
    def create_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS security_qa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source_name VARCHAR(20),
                question VARCHAR(1000),
                answer VARCHAR(1000))
            '''
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("表创建成功")
        except pymysql.MySQLError as e:
            logger.error(f"表创建失败: {e}")
            raise

    # 插入指定csv文件的数据
    def insert_data(self, csv_path):
        try:
            data = pd.read_csv(csv_path)
            for _, row in data.iterrows():
                # print(row)
                insert_query = "INSERT INTO security_qa (source_name, question, answer) VALUES (%s, %s, %s)"
                self.cursor.execute(insert_query, (row['板块名称'], row['问题'], row['答案']))
            # 提交事务
            self.connection.commit()
            logger.info("数据插入成功")
        except Exception as e:
            logger.error(f"数据插入失败: {e}")
            self.connection.rollback()
            raise

    # 获取所有问题
    def fetch_questions(self):
        try:
            # 执行查询
            self.cursor.execute("SELECT question FROM security_qa")
            # 获取结果
            results = self.cursor.fetchall()
            # 记录获取成功
            logger.info("成功获取问题")
            # 返回结果
            return results
        except pymysql.MySQLError as e:
            # 记录查询失败
            logger.error(f"查询失败: {e}")
            # 返回空列表
            return []

    # 获取指定问题的答案
    def fetch_answer(self, question):
        try:
            # 执行查询
            self.cursor.execute("SELECT answer FROM security_qa WHERE question=%s", (question,))
            # 获取结果
            result = self.cursor.fetchone()
            # 返回答案或 None
            return result[0] if result else None
        except pymysql.MySQLError as e:
            # 记录答案获取失败
            logger.error(f"答案获取失败: {e}")
            # 返回 None
            return None

    # 关闭数据库连接
    def close(self):
        try:
            # 关闭连接
            self.connection.close()
            # 记录关闭成功
            logger.info("MySQL 连接已关闭")
        except pymysql.MySQLError as e:
            # 记录关闭失败
            logger.error(f"关闭连接失败: {e}")


if __name__ == '__main__':
    mysql_client = MySQLClient()

    mysql_client.create_table()
    mysql_client.insert_data(
        os.path.join(config.PROJECT_ROOT, 'mysql_qa/data/安保集团知识问答.csv')
    )

    questions = mysql_client.fetch_questions()
    # print(type(questions))
    # print(questions)
    for q in questions:
        print(q)
    #
    # result = mysql_client.fetch_answer('关联子查询的执行顺序是什么')
    # print(result)
    mysql_client.close()
