import unittest
import app
from unittest.mock import patch
import mongomock

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.api.test_client()
        self.app.testing = True
    
    # def test_email_validation_no_email(self):
    #     try:
    #         response=self.app.get('/email-validation?EmailAddress=')
    #         print("1", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertFalse(response.json["Success"])
    #     except Exception as e:
    #         print(f"email_validation 1 raise errors: {e}")
    #         raise
    # def test_wrong_email_validation(self):
    #     try:
    #         response=self.app.get('/email-validation?EmailAddress=3993293')
    #         print("2", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertFalse(response.json["Success"])
    #     except:
    #         print("email_validation 2 raise errors.")
            
    # @patch('app.db.UserInfos.find_one')
    # def test_email_validation_no_code_user_exist(self,mock_find_one):
    #     try:
    #         mock_find_one.return_value = {"EmailAddress": "test@example.com", "CodeTime": "2024-03-31T12:00:00"}
    #         response = self.app.get('/email-validation?EmailAddress=test@example.com')
    #         print("3", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.json["Success"])
    #     except Exception as e:
    #         print(f"email_validation 3 raise errors: {e}")
    #         raise
        
    # @patch('app.db.UserInfos.find_one')
    # def test_email_validation_no_code_user_no_exist(self,mock_find_one):
    #     try:
    #         mock_find_one.return_value = None
    #         response = self.app.get('/email-validation?EmailAddress=new_user@example.com')
    #         print("4", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.json["Success"])
    #     except Exception as e:
    #         print(f"email_validation 4 raise errors, {e}")
    #         raise
        
    # @patch('app.db.UserInfos.find_one')
    # def test_email_validation_with_code_wrong(self, mock_find_one):
    #     try:
    #         mock_find_one.return_value = {"EmailAddress": "test@example.com", "ValidCode": "123456"}
    #         response = self.app.get('/email-validation?EmailAddress=test@example.com&InputCode=654321')
    #         print("5", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertFalse(response.json["Success"])
    #         self.assertEqual(response.json["Error"], "Wrong code!")
    #     except Exception as e:
    #         print(f"email_validation 5 raise errors, {e}")
    #         raise
        
    # @patch('app.db.UserInfos.find_one')
    # def test_email_validation_with_code_correct(self, mock_find_one):
    #     try:
    #         mock_find_one.return_value = {"EmailAddress": "test@example.com", "ValidCode": '123456'}
            
    #         response = self.app.get('/email-validation?EmailAddress=test@example.com&InputCode=123456')
    #         print("6", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.json["Success"])
    #     except Exception as e:
    #         print(f"email_validation 6 raise errors, {e}")
    #         raise
        
    @mongomock.patch(servers=(('server.example.com', 27017),))
    def test_email_validation_inputcode_correct(self):
        try:
            # 创建一个模拟的 MongoDB 客户端
            mock_client = mongomock.MongoClient('server.example.com', 27017)
            app.db = mock_client['chen_db']  # 使用你的数据库名称替换
            app.db['UserInfos'].insert_one({'EmailAddress': 'test@example.com', 'ValidCode': '123456'})
            
            response = self.app.get('/email-validation?EmailAddress=test@example.com&InputCode=123456')
            # print("\n response:", response.json["Error"])
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])

        except Exception as e:
            print(f"email_validation 6 raise errors, {e}")
            raise
        
    # @patch('app.db.UserInfos.find_one')
    # def test_email_validation_recent_code_sent(self, mock_find_one):
    #     try:
    #         last_code_time = (datetime.now() - timedelta(seconds=60)).strftime('%Y-%m-%d %H:%M:%S')
    #         mock_find_one.return_value = {'EmailAddress': 'test@example.com', 'CodeTime': last_code_time}
    #         response = self.app.get('/email-validation?EmailAddress=test@example.com')
    #         print("7", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertFalse(response.json['Success'])
    #         self.assertEqual(response.json['Error'], "Already send email, please try it later!")
    #     except Exception as e:
    #         print(f"email_validation 7 raise errors, {e}")
    #         raise
        
    # @patch('app.db.UserInfos.find_one')
    # @patch('app.send_valid_code')
    # def test_email_validation_code_sent_no_user(self, mock_send_valid_code, mock_find_one):
    #     try:
    #         mock_find_one.return_value = None
    #         mock_send_valid_code.return_value = (True, None)
    #         response = self.app.get('/email-validation?EmailAddress=newuser@example.com')
    #         print("8", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.json['Success'])
    #     except Exception as e:
    #         print(f"email_validation 8 raise errors, {e}")
    #         raise
        
    # @patch('app.db.UserInfos.find_one')
    # @patch('app.send_valid_code')
    # def test_email_validation_code_sent_fail(self, mock_send_valid_code, mock_find_one):
    #     try:
    #         mock_find_one.return_value = None
    #         mock_send_valid_code.return_value = (False, "Send validation code error!")
    #         response = self.app.get('/email-validation?EmailAddress=user@example.com')
    #         print("9", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertFalse(response.json['Success'])
    #         self.assertEqual(response.json['Error'], "Send validation code error!")
    #     except Exception as e:
    #         print(f"email_validation 9 raise errors, {e}")
    #         raise
        
    # @patch.object(db.UserInfos, 'find_one')
    # def test_email_validation_inputcode_correct(self, mock_find_one):
    #     try:
    #         mock_find_one.return_value = {'EmailAddress': 'user@example.com', 'ValidCode': '123456'}
    #         response = self.app.get('/email-validation?EmailAddress=user@example.com&InputCode=123456')
    #         print("10", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTrue(response.json['Success'])
    #     except Exception as e:
    #         print(f"email_validation 10 raise errors, {e}")
    #         raise
        
    # @patch('app.db.UserInfos.find_one')
    # def test_email_validation_no_user_code_provided(self, mock_find_one):
    #     try:
    #         mock_find_one.return_value = None       
    #         response = self.app.get('/email-validation?EmailAddress=nonexist@example.com&InputCode=123456')
    #         print("11", response.json.get("Error"))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertFalse(response.json['Success'])
    #         self.assertEqual(response.json['Error'], "Illegal access: Please stop doing again!")
    #     except Exception as e:
    #         print(f"email_validation 11 raise errors, {e}")
    #         raise

        
        
if __name__ == '__main__':
    unittest.main()



# 先下载 coverage：
# pip install coverage

# 运行文件：
# coverage run -m API_test

# 生成html
# coverage html

# 在同文件夹下会有一个交htmlcov的文件夹，打开里面的html可以看到那些行被使用