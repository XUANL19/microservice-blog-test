import pymysql
import os

class CommentResource:
    def __int__(self):
        pass

    @staticmethod
    def _get_connection():

        usr = "root"
        pw = "84443295412lx."
        h = "localhost"

        conn = pymysql.connect(
            user=usr,
            password=pw,
            host=h,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn

    @staticmethod
    def get_comments_by_blogID(blog_id):
        sql = "SELECT * FROM commentdb.comments WHERE blog_id=%s"
        conn = CommentResource._get_connection()
        cur = conn.cursor()

        try:
            cur.execute(sql, blog_id)
        except:
            return None
        
        result = cur.fetchall()
        return result


    @staticmethod
    def get_comments_number(blog_id):
        sql = "SELECT COUNT(*) FROM commentdb.comments WHERE blog_id=%s"
        conn = CommentResource._get_connection()
        cur = conn.cursor()

        try:
            cur.execute(sql, blog_id)
        except:
            return None
        
        result = cur.fetchone()
        result = result["COUNT(*)"]
        return result
        
        
    @staticmethod
    def get_commentsnum_by_username(username):
        sql = "SELECT COUNT(*) FROM commentdb.comments WHERE owner_id=%s"
        conn = CommentResource._get_connection()
        cur = conn.cursor()

        try:
            cur.execute(sql, username)
        except:
            return None
        
        result = cur.fetchone()
        result = result["COUNT(*)"]
        return result