import unittest
from app import app, db
from unittest.mock import MagicMock


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_EmailNoExist_1(self):
        try:
            response = self.app.get('/email-no-exist?EmailAddress=1030920919@qq.com')  # GET 请求发送的数据
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except:
            print("test_EmailNoExist_1 raise errors.")

    def test_Login_1(self):
        try:
            data = {'EmailAddress': '1030920919@qq.com', 'Password': 1234}  # POST 请求发送的数据
            response = self.app.post('/login', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
        except:
            print("test_Login_1 raise errors.")



    def test_get_post_history_success(self):
        try:
            # 模拟请求参数
            params = {'EmailAddress': 'user@example.com'}
            # 模拟用户存在，且有帖子历史记录的情况
            mock_user_info = {
                'EmailAddress': 'user@example.com',
                'PostHistory': ['post_id_1', 'post_id_2']
            }
            # 模拟帖子记录
            mock_post_1 = {
                '_id': 'post_id_1',
                'PostOwner': 'owner1',
                'CreateTime': 'create_time_1',
                'Title': 'title1',
                'Text': 'text1',
                'Price': 100,
                'Auction': False,
                'LostFound': False,
                'Images': [],
                'Comments': [],
                'Score': 5
            }

            mock_post_2 = {
                '_id': 'post_id_2',
                'PostOwner': 'owner2',
                'CreateTime': 'create_time_2',
                'Title': 'title2',
                'Text': 'text2',
                'Price': 200,
                'Auction': True,
                'LostFound': False,
                'Images': ['image_url'],
                'Comments': [{'user': 'comment_user', 'text': 'comment_text'}],
                'Score': 4
            }
            # 设置模拟行为
            self.mock_user_infos.find_one.return_value = mock_user_info
            self.mock_posts.find_one.side_effect = [mock_post_1, mock_post_2]
            # 发送请求
            response = self.app.get('/get-post-history', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含成功标志和帖子历史记录
            self.assertTrue(response.json['Success'])
            self.assertTrue(response.json['Posts'])
        except Exception as e:
            print("test_get_post_history_success raised an error:", e)

    def test_get_post_history_user_not_found(self):
        try:
            # 模拟请求参数
            params = {'EmailAddress': 'user@example.com'}
            # 模拟用户不存在的情况
            self.mock_user_infos.find_one.return_value = None
            # 发送请求
            response = self.app.get('/get-post-history', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含失败标志和错误消息
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Did not find account. Please try it again!")
        except Exception as e:
            print("test_get_post_history_user_not_found raised an error:", e)

    def test_get_post_history_invalid_email_format(self):
        try:
            # 模拟请求参数
            params = {'EmailAddress': 'invalid_email_format'}
            # 发送请求
            response = self.app.get('/get-post-history', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含失败标志和错误消息
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Invalid email address!")
        except Exception as e:
            print("test_get_post_history_invalid_email_format raised an error:", e)


    def test_click_post_success(self):
        try:
            # 模拟请求参数
            params = {'EmailAddress': '1030920919@qq.com', 'PID': '65a199aaa2c14c072766377a'}
            # 模拟帖子存在的情况
            mock_post = {
                '_id': '65a199aaa2c14c072766377a',
                'Count': '5'
            }
            # 模拟用户存在的情况
            mock_user_info = {
                'EmailAddress': '1030920919@qq.com',
                'PostHistory': ['65a199aaa2c14c072766377a']
            }
            # 设置模拟行为
            self.mock_posts.find_one.return_value = mock_post
            self.mock_user_infos.find_one.return_value = mock_user_info
            # 发送请求
            response = self.app.get('/click-post', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含成功标志
            self.assertTrue(response.json['Success'])
            # 检查帖子点击计数是否正确更新
            self.assertEqual(response.json['Count'], 6)
            # 检查用户的帖子历史记录是否正确更新
            self.assertIn('65a199aaa2c14c072766377a', response.json['UserPostHistory'])
        except Exception as e:
            print("test_click_post_success raised an error:", e)

    def test_click_post_user_not_found(self):
        try:
            # 模拟请求参数
            params = {'EmailAddress': 'nonexistent_user@example.com', 'PID': '65a199aaa2c14c072766377a'}
            # 模拟用户不存在的情况
            self.mock_user_infos.find_one.return_value = None
            # 发送请求
            response = self.app.get('/click-post', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含失败标志和错误消息
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Did not find account. Please try it again!")
        except Exception as e:
            print("test_click_post_user_not_found raised an error:", e)

    def test_click_post_invalid_email_format(self):
        try:
            # 模拟请求参数
            params = {'EmailAddress': 'invalid_email_format', 'PID': '65a199aaa2c14c072766377a'}
            # 发送请求
            response = self.app.get('/click-post', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含失败标志和错误消息
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Invalid email address!")
        except Exception as e:
            print("test_click_post_invalid_email_format raised an error:", e)

    def test_post_comment_success(self):
        try:
            # 模拟请求数据
            data = {
                'Commenter': 'commenter@example.com',
                'PID': '65a199aaa2c14c072766377a',
                'Text': 'This is a test comment.'
            }
            # 模拟评论者存在且合法，帖子存在的情况
            mock_user_info = {
                'EmailAddress': 'commenter@example.com',
                'NickName': 'Test Commenter',
                'HeadPortrait': 'avatar_url'
            }
            mock_post = {
                '_id': '65a199aaa2c14c072766377a',
                'Comments': []
            }
            # 设置模拟行为
            self.mock_user_infos.find_one.return_value = mock_user_info
            self.mock_posts.find_one.return_value = mock_post
            # 发送请求
            response = self.app.post('/post-comment', data=data)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含成功标志
            self.assertTrue(response.json['Success'])
            # 检查评论是否正确添加到帖子中
            comments = response.json['Comments']
            self.assertEqual(len(comments), 1)
            self.assertEqual(comments[0]['Commenter'], 'commenter@example.com')
            self.assertEqual(comments[0]['Text'], 'This is a test comment.')
            self.assertEqual(comments[0]['NickName'], 'Test Commenter')
            self.assertEqual(comments[0]['HeadPortrait'], 'avatar_url')
        except Exception as e:
            print("test_post_comment_success raised an error:", e)

    def test_user_posts_success(self):
        try:
            # 模拟请求参数
            params = {'EmailAddress': '1030920919@qq.com'}
            # 模拟用户存在的情况，且有帖子存在
            mock_user_posts = [
                {
                    '_id': 'post_id_1',
                    'PostOwner': '1030920919@qq.com',
                    'CreateTime': '2022-03-01 10:00:00',
                    'Title': 'Title 1',
                    'Text': 'Text 1',
                    'Price': 100,
                    'Auction': False,
                    'LostFound': False,
                    'Images': [],
                    'Comments': []
                },
                {
                    '_id': 'post_id_2',
                    'PostOwner': '1030920919@qq.com',
                    'CreateTime': '2022-03-02 12:00:00',
                    'Title': 'Title 2',
                    'Text': 'Text 2',
                    'Price': 200,
                    'Auction': True,
                    'LostFound': False,
                    'Images': ['image_url'],
                    'Comments': [{'user': 'comment_user', 'text': 'comment_text'}]
                }
            ]
            # 设置模拟行为
            self.mock_posts.find.return_value.limit.return_value = mock_user_posts

            # 发送请求
            response = self.app.get('/user-posts', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含成功标志和用户的帖子列表
            self.assertTrue(response.json['Success'])
            posts = response.json['Posts']
            self.assertEqual(len(posts), 2)
            self.assertEqual(posts[0]['PID'], 'post_id_1')
            self.assertEqual(posts[0]['PostOwner'], '1030920919@qq.com')
            self.assertEqual(posts[0]['CreateTime'], '2024-02-15 10:00:00')
            # 检查第二个帖子的一些属性
            self.assertEqual(posts[1]['PID'], 'post_id_2')
            self.assertEqual(posts[1]['Title'], 'Title 2')
            self.assertEqual(posts[1]['Price'], 200)
        except Exception as e:
            print("test_user_posts_success raised an error:", e)

    def test_user_posts_invalid_email_format(self):
        try:
            # 模拟请求参数，但邮箱格式不正确
            params = {'EmailAddress': 'invalid_email_format'}
            # 发送请求
            response = self.app.get('/user-posts', query_string=params)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含失败标志和错误消息
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Invalid email address!")
        except Exception as e:
            print("test_user_posts_invalid_email_format raised an error:", e)



    def test_post_comment_no_text(self):
        try:
            # 模拟请求数据，但没有评论内容
            data = {
                'Commenter': 'commenter@example.com',
                'PID': '65a199aaa2c14c072766377a',
                'Text': ''
            }
            # 发送请求
            response = self.app.post('/post-comment', data=data)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含失败标志和错误消息
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "No text provided!")
        except Exception as e:
            print("test_post_comment_no_text raised an error:", e)

    def test_get_posts_with_keyword(self):
        try:
            # 模拟请求数据，带有关键词
            data = {
                "EmailAddress": "1030920919@qq.com",
                "Keyword": "test",
                "Num": 6
            }
            # 发送请求
            response = self.app.get('/get-posts', query_string=data)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含成功标志和帖子列表
            self.assertTrue(response.json['Success'])
            self.assertTrue(response.json['Posts'])
        except Exception as e:
            print("test_get_posts_with_keyword raised an error:", e)

    def test_get_posts_without_keyword(self):
        try:
            # 模拟请求数据，不带关键词
            data = {
                "EmailAddress": "1030920919@qq.com",
                "Num": 6
            }
            # 发送请求
            response = self.app.get('/get-posts', query_string=data)
            # 断言状态码为 200
            self.assertEqual(response.status_code, 200)
            # 断言返回的结果包含成功标志和帖子列表
            self.assertTrue(response.json['Success'])
            self.assertTrue(response.json['Posts'])
        except Exception as e:
            print("test_get_posts_without_keyword raised an error:", e)


#     def test_notification_channel_set(self):
#         try:
#             # 模拟登录操作，例如发送POST请求到登录端点
#             data = {'EmailAddress': 'S354wang@uwaterloo.ca', 'Password': 'Wsnnb3418^'}  # POST 请求发送的数据
#             response = self.app.post('/login', data=data)
#
#             # 检查登录是否成功，这取决于您的应用程序逻辑
#             self.assertEqual(response.status_code, 200)
#             self.assertTrue(response.json["Success"])
#
#             # 检查登录后是否生成了通知频道
#             response = self.app.get('/check_notification')
#             self.assertEqual(response.status_code, 200)
#             self.assertTrue(response.json["NotificationGenerated"])
#
#         except:
#             print("test_notification_channel_after_login raised an error")
#
#     def test_
        
if __name__ == '__main__':
    unittest.main()



# 先下载 coverage：
# pip install coverage

# 运行文件：
# coverage run -m API_test

# 生成html
# coverage html

# 在同文件夹下会有一个交htmlcov的文件夹，打开里面的html可以看到那些行被使用