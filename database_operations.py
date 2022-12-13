#from turtle import title
import pymysql
from flask import Flask, Response, request
import json

class DatabaseOperations:

    def __int__(self):
        pass

    @staticmethod
    def _get_connection():

        usr = "root"
        pw = "84443295412lx."
        # h = "localhost"
        h = "db6156.c4qfxod7s5ol.us-east-1.rds.amazonaws.com"

        conn = pymysql.connect(
            user=usr,
            password=pw,
            host=h,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn


    @staticmethod
    def new_blog_post(owner_id, blog_title, blog_content, post_time, tags):
        #init vars
        new_blog_id = ""
        total_post = 0 

        #create a new blog id
        sql = "SELECT owner_id, MAX(total_post) AS max_count FROM blogs.blog_info WHERE owner_id = %s GROUP BY owner_id";
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=(owner_id))
        result = cur.fetchone()
        tag1 = None if len(tags) == 0 else tags[0]
        tag2 = None if len(tags) <= 1 else tags[1]
        tag3 = None if len(tags) <= 2 else tags[2]
        
        if result:
            new_blog_id =  result["owner_id"] + "-" + str(int(result["max_count"]) + 1)
            total_post = int(result["max_count"]) + 1
        else:
            new_blog_id = owner_id + "-" + str(1)
            total_post = 1
     
        #enter new entry into blog_info table
        sql = "INSERT INTO blogs.blog_info VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '[]', 0, '[]', 0)"
        conn = DatabaseOperations._get_connection()

        cur = conn.cursor()
        res = cur.execute(sql, args=(new_blog_id, owner_id, blog_title, blog_content, post_time, total_post, tag1, tag2, tag3))
        if res:
            posting_success = {'status': 'success', 'message': 'Successfully Posted'}
            success_response = Response(json.dumps(posting_success), status=200, content_type="application.json")
            return success_response
        else:
            posting_failed = {'status': 'fail', 'message': 'Posting Failed'}
            fail_response = Response(json.dumps(posting_failed), status=200, content_type="application.json")
            return fail_response


    @staticmethod
    def get_blog_number(username):
        sql = "SELECT COUNT(*) FROM blogs.blog_info WHERE owner_id=%s"
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()

        try:
            cur.execute(sql, username)
        except:
            return None
        
        result = cur.fetchone()
        result = result["COUNT(*)"]
        return result    


    @staticmethod
    def get_own_post(owner_id):
        sql = "SELECT * FROM blogs.blog_info Where owner_id = %s ORDER BY unique_blog_id DESC;"
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql,owner_id)
        except:
            return None
        result = cur.fetchall()
        return result
    

    @staticmethod
    def get_all_posts():
        sql = "SELECT * FROM blogs.blog_info ORDER BY unique_blog_id DESC;"
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql)
        except:
            return None
        result = cur.fetchall()
        return result


    @staticmethod
    def get_blog_by_blogid(blog_id):
        sql = "SELECT * FROM blogs.blog_info WHERE unique_blog_id=%s"
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, blog_id)
        except:
            return None
        result = cur.fetchone()
        return result 

   
    @staticmethod
    def get_like_state(user_id, blog_id):
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        sql = "SELECT JSON_SEARCH((select liked_by from blogs.blog_info where unique_blog_id = %s), 'one', %s)"

        cur.execute(sql, (blog_id, user_id))
        result = list(cur.fetchone().values())[0]
        if result:
            return 1
        else:
            return 0


    @staticmethod
    def get_dislike_state(user_id, blog_id):
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        sql = "SELECT JSON_SEARCH((select disliked_by from blogs.blog_info where unique_blog_id = %s), 'one', %s)"

        cur.execute(sql, (blog_id, user_id))
        result = list(cur.fetchone().values())[0]
        if result:
            return 1
        else:
            return 0


    @staticmethod
    def get_like_and_dislike_num(blog_id):
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        sql = "select likecount, dislikecount from blogs.blog_info where unique_blog_id = %s"
        cur.execute(sql, blog_id)
        res = cur.fetchone()
        return res


    @staticmethod
    def like_and_dislike_state_check(user_id, blog_id):

        res = DatabaseOperations.get_like_and_dislike_num(blog_id)
        like = DatabaseOperations.get_like_state(user_id, blog_id)
        dislike = DatabaseOperations.get_dislike_state(user_id, blog_id)

        if like:
            res['likestate'] = '1'
        elif dislike:
            res['likestate'] = '2'
        else:
            res['likestate'] = '0'
        return res


    @staticmethod
    def add_to_like(user_id, blog_id):
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()

        sql = "select json_array_append((select liked_by from blogs.blog_info where unique_blog_id = %s),'$', %s)"  
        res = cur.execute(sql, (str(blog_id), str(user_id)))
        added_res = list(cur.fetchone().values())[0]

        update_sql = "update blogs.blog_info set liked_by = %s where unique_blog_id=%s"
        res = cur.execute(update_sql,(added_res, blog_id))

        plus_sql = "update blogs.blog_info set likecount = likecount + 1 where unique_blog_id=%s"
        cur.execute(plus_sql, blog_id)

        if res:
            message = {'status': 'success', 'message': 'like Successfully added!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response   
        else:
            message = {'status': 'failed', 'message': 'like failed added!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response 


    @staticmethod
    def add_to_dislike(user_id, blog_id):
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        sql = "select json_array_append((select disliked_by from blogs.blog_info where unique_blog_id=%s),'$', %s)"  
        cur.execute(sql, (blog_id, user_id))
        added_res = list(cur.fetchone().values())[0]

        update_sql = "update blogs.blog_info set disliked_by = %s where unique_blog_id=%s"
        res = cur.execute(update_sql,(added_res, blog_id))

        plus_sql = "update blogs.blog_info set dislikecount = dislikecount + 1 where unique_blog_id=%s"
        cur.execute(plus_sql, blog_id)

        if res:
            message = {'status': 'success', 'message': 'dislike Successfully added!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response 
        else:
            message = {'status': 'failed', 'message': 'dislike failed added!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response 


    @staticmethod
    def remove_from_like(user_id, blog_id):
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        sql = "select json_remove((select liked_by from blogs.blog_info where unique_blog_id = %s), JSON_UNQUOTE((SELECT JSON_SEARCH((select liked_by from blogs.blog_info where unique_blog_id = %s), 'one', %s))))"
        cur.execute(sql, (blog_id, blog_id, user_id))
        removed_res = list(cur.fetchone().values())[0]

        update_sql = "update blogs.blog_info set liked_by = %s where unique_blog_id=%s"
        res = cur.execute(update_sql,(removed_res, blog_id))

        minus_sql = "update blogs.blog_info set likecount = likecount - 1 where unique_blog_id=%s"
        cur.execute(minus_sql, blog_id)

        if res:
            message = {'status': 'success', 'message': 'like Successfully removed!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response 
        else:
            message = {'status': 'failed', 'message': 'like failed removed!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response 


    @staticmethod
    def remove_from_dislike(user_id, blog_id):
        conn = DatabaseOperations._get_connection()
        cur = conn.cursor()
        sql = "select json_remove((select disliked_by from blogs.blog_info where unique_blog_id = %s), JSON_UNQUOTE((SELECT JSON_SEARCH((select disliked_by from blogs.blog_info where unique_blog_id = %s), 'one', %s))))"
        cur.execute(sql, (blog_id, blog_id, user_id))
        removed_res = list(cur.fetchone().values())[0]

        update_sql = "update blogs.blog_info set disliked_by = %s where unique_blog_id=%s"
        res = cur.execute(update_sql,(removed_res, blog_id))

        minus_sql = "update blogs.blog_info set dislikecount = dislikecount - 1 where unique_blog_id=%s"
        cur.execute(minus_sql, blog_id)

        if res:
            message = {'status': 'success', 'message': 'dislike Successfully removed!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response 
        else:
            message = {'status': 'failed', 'message': 'dislike failed removed!'}
            response = Response(json.dumps(message), status=200, content_type="application.json")
            return response 