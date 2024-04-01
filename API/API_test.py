import unittest
from app import app, db
import json
from unittest.mock import patch, MagicMock
from bson import ObjectId
from unittest.mock import patch, MagicMock, call
from unittest import mock
from datetime import datetime, timedelta



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

    def test_email_no_exist_no_email(self):
        try:
            response=self.app.get('/email-no-exist?EmailAddress=')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"email_no_exist1 raise errors: {e}")
            raise
    def test_email_no_exist_wrong_email(self):
        try:
            response=self.app.get('/email-no-exist?EmailAddress=3993293')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"email_no_exist2 raise errors: {e}")
            raise
    @patch('app.db')
    def test_email_no_exist_user_no_password(self, mock_db):
        try:
        # 模拟数据库返回存在的用户但没有密码
            mock_db.UserInfos.find_one.return_value = {'EmailAddress': '1030920919@qq.com', 'Password': None}

        # 发起请求
            response = self.app.get('/email-no-exist?EmailAddress=1030920919@qq.com')

        # 检查响应
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])

        # 验证是否进行了数据库查询
            mock_db.UserInfos.find_one.assert_called_with({'EmailAddress': '1030920919@qq.com'})

        except Exception as e:
            print(f"email_no_exist3 raise errors: {e}")
            raise
    def test_email_no_exist_user_has_password(self):
        try:
            response=self.app.get('/email-no-exist?EmailAddress=x89zhang@uwaterloo.ca&Password=123456')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"email_no_exist4 raise errors: {e}")
            raise
    def test_non_exist_email(self):
        try:
            response=self.app.get('/email-no-exist?EmailAddress=123456@qq.com')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"email_no_exist5 raise errors: {e}")
            raise
    
    def test_email_validation_no_email(self):
        try:
            response=self.app.get('/email-validation?EmailAddress=')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"email_validation1 raise errors: {e}")
            raise
    def test_wrong_email_validation(self):
        try:
            response=self.app.get('/email-validation?EmailAddress=3993293')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except:
            print("email_validation2 raise errors.")
    @patch('app.db.UserInfos.find_one')
    def test_email_validation_no_code_user_exist(self,mock_find_one):
        try:
            mock_user_info = {"EmailAddress": "test@example.com", "CodeTime": "2024-03-31T12:00:00"}
            mock_find_one.return_value = mock_user_info

            response = self.app.get('/email-validation?EmailAddress=test@example.com')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"email_validation3 raise errors: {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    def test_email_validation_no_code_user_no_exist(self,mock_find_one):
        try:
            mock_find_one.return_value = None
            response = self.app.get('/email-validation?EmailAddress=new_user@example.com')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"email_validation4 raise errors, {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    def test_email_validation_with_code_wrong(self, mock_find_one):
        try:
            mock_user_info = {"EmailAddress": "test@example.com", "ValidCode": "123456"}
            mock_find_one.return_value = mock_user_info

            response = self.app.get('/email-validation?EmailAddress=test@example.com&InputCode=654321')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
            self.assertEqual(response.json["Error"], "Wrong code!")
        except Exception as e:
            print(f"email_validation5 raise errors, {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    def test_email_validation_with_code_correct(self, mock_find_one):
        try:
            mock_user_info = {"EmailAddress": "test@example.com", "ValidCode": '123456'}
            mock_find_one.return_value = mock_user_info

            response = self.app.get('/email-validation?EmailAddress=test@example.com&InputCode=123456')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"email_validation6 raise errors, {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    def test_email_validation_recent_code_sent(self, mock_find_one):
        try:
            last_code_time = (datetime.now() - timedelta(seconds=60)).strftime('%Y-%m-%d %H:%M:%S')
            mock_find_one.return_value = {'EmailAddress': 'test@example.com', 'CodeTime': last_code_time}
            response = self.app.get('/email-validation?EmailAddress=test@example.com')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Already send email, please try it later!")
        except Exception as e:
            print(f"email_validation7 raise errors, {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    @patch('app.send_valid_code')
    def test_email_validation_code_sent_no_user(self, mock_send_valid_code, mock_find_one):
        try:
            mock_find_one.return_value = None
            mock_send_valid_code.return_value = (True, None)
            response = self.app.get('/email-validation?EmailAddress=newuser@example.com')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json['Success'])
        except Exception as e:
            print(f"email_validation8 raise errors, {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    @patch('app.send_valid_code')
    def test_email_validation_code_sent_fail(self, mock_send_valid_code, mock_find_one):
        try:
            mock_find_one.return_value = None
            mock_send_valid_code.return_value = (False, "Send validation code error!")
            response = self.app.get('/email-validation?EmailAddress=user@example.com')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Send validation code error!")
        except Exception as e:
            print(f"email_validation9 raise errors, {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    def test_email_validation_inputcode_correct(self, mock_find_one):
        try:
            mock_find_one.return_value = {'EmailAddress': 'user@example.com', 'ValidCode': '123456'}
            response = self.app.get('/email-validation?EmailAddress=user@example.com&InputCode=123456')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json['Success'])
        except Exception as e:
            print(f"email_validation10 raise errors, {e}")
            raise
    @patch('app.db.UserInfos.find_one')
    def test_email_validation_no_user_code_provided(self, mock_find_one):
        try:
            mock_find_one.return_value = None       
            response = self.app.get('/email-validation?EmailAddress=nonexist@example.com&InputCode=123456')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Illegal access: Please stop doing again!")
        except Exception as e:
            print(f"email_validation11 raise errors, {e}")
            raise
    
    def test_set_reset_password_no_email(self):
        try:
            data={'EmailAddress': "123456"}
            response=self.app.post('/set-reset-password',data=data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"set_reset_password1 raise errors: {e}")
            raise
    def test_set_reset_password_invalid_password(self):
        data={'EmailAddress': "281750569@qq.com", 'Password': '123456'}
        try:
            response=self.app.post('/set-reset-password',data=data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"set_reset_password2 raise errors: {e}")
            raise
    def test_set_reset_password_wrong_old_password(self):
        data={'EmailAddress': "281750569@qq.com"}
        try:
            response=self.app.post('/set-reset-password',data=data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"set_reset_password3 raise errors: {e}")
            raise
    @patch('app.check_email')
    @patch('app.check_password')
    @patch('app.db')
    def test_set_reset_password_correct(self, mock_db, mock_check_password, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (False, "This account has no password!")

            mock_db.UserInfos.update_one = MagicMock()

            response = self.app.post('/set-reset-password', data={
                'EmailAddress': 'test@example.com',
                'Password': 'new_password'
            })

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])

            mock_db.UserInfos.update_one.assert_called_once()
        except Exception as e:
            print(f"set_reset_password4 raise errors: {e}")
            raise
    @patch('app.check_password')
    @patch('app.check_email')
    @patch('app.db')
    def test_set_reset_password_new_old_pw_provided(self, mock_db, mock_check_email, mock_check_password):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (False, "This account has no password!")
            mock_db.UserInfos.update_one = MagicMock()
            response = self.app.post('/set-reset-password', data={
                'EmailAddress': 'test@example.com',
                'Password': 'old_password',
                'NewPassword': 'new_password'
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
            self.assertEqual(response.json["Error"], "You should not provide new password!")
            mock_db.UserInfos.update_one.assert_not_called()
        except Exception as e:
            print(f"set_reset_password5 raise errors: {e}")
            raise
    @patch('app.check_password')
    @patch('app.check_email')
    @patch('app.db')
    def test_set_reset_password_forget_pw_no_valid_email(self, mock_db, mock_check_email, mock_check_password):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (False, "Did not provide password.")
            code_time = datetime.now() - timedelta(seconds=121)
            mock_db.UserInfos.find_one.return_value = {
                'EmailAddress': 'test@example.com',
                'CodeTime': code_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            mock_db.UserInfos.update_one = MagicMock()
            response = self.app.post('/set-reset-password', data={
                'EmailAddress': 'test@example.com',
                'NewPassword': 'new_password'
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
            self.assertEqual(response.json["Error"], "You should do email validation first!")
            mock_db.UserInfos.update_one.assert_not_called()
        except Exception as e:
            print(f"set_reset_password6 raise errors: {e}")
            raise
    @patch('app.check_password')
    @patch('app.check_email')
    @patch('app.db')
    def test_set_reset_password_forget_pw_valid_email(self, mock_db, mock_check_email, mock_check_password):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (False, "Did not provide password.")
            code_time = datetime.now() - timedelta(seconds=60)
            mock_db.UserInfos.find_one.return_value = {
                'EmailAddress': 'test@example.com',
                'CodeTime': code_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            mock_db.UserInfos.update_one = MagicMock()
            response = self.app.post('/set-reset-password', data={
                'EmailAddress': 'test@example.com',
                'NewPassword': 'new_password'
            })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
            mock_db.UserInfos.update_one.assert_called_with(
                {'EmailAddress': 'test@example.com'},
                {"$set": {'Password': 'new_password'}}
            )
        except Exception as e:
            print(f"set_reset_password7 raise errors: {e}")
            raise
    @patch('app.check_password')
    @patch('app.check_email')
    @patch('app.db')
    def test_set_reset_pw_wrong_old_pw(self, mock_db, mock_check_email, mock_check_password):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (False, "Wrong password!")
            mock_db.UserInfos.find_one = MagicMock()
            mock_db.UserInfos.update_one = MagicMock()
            response = self.app.post('/set-reset-password', data={
                'EmailAddress': 'test@example.com',
                'Password': 'old_wrong_password',
                'NewPassword': 'new_password'
            })
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data["Success"])
            self.assertEqual(json_data["Error"], "Wrong password!")
            mock_db.UserInfos.update_one.assert_not_called()
        except Exception as e:
            print(f"set_reset_password8 raise errors: {e}")
            raise
    @patch('app.check_password')
    @patch('app.check_email')
    @patch('app.db')
    def test_set_reset_pw_old_pass_no_new(self, mock_db, mock_check_email, mock_check_password):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (True, None)
            mock_db.UserInfos.find_one = MagicMock()
            mock_db.UserInfos.update_one = MagicMock()
            response = self.app.post('/set-reset-password', data={
                'EmailAddress': 'test@example.com',
                'Password': 'old_password'
            })
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data["Success"])
            self.assertEqual(json_data["Error"], "Did not provide new password.")
            mock_db.UserInfos.update_one.assert_not_called()
        except Exception as e:
            print(f"set_reset_password9 raise errors: {e}")
            raise
    @patch('app.check_password')
    @patch('app.check_email')
    @patch('app.db')
    def test_set_reset_pw_old_pass_new_pass(self, mock_db, mock_check_email, mock_check_password):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (True, None)

            mock_db.UserInfos.find_one = MagicMock()
            mock_db.UserInfos.update_one = MagicMock()
            response = self.app.post('/set-reset-password', data={
                'EmailAddress': 'test@example.com',
                'Password': 'old_password',
                'NewPassword': 'new_password'
            })
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data["Success"])
            mock_db.UserInfos.update_one.assert_called_once_with(
                {'EmailAddress': 'test@example.com'},
                {'$set': {'Password': 'new_password'}}
            )
        except Exception as e:
            print(f"set_reset_password10 raise errors: {e}")
            raise
    


    def test_create_account_no_email(self):
        try:
            data={}
            headers={"Content-Type": "application/json"}
            response=self.app.post('/create-account',json=data,headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"create_account1 raise errors: {e}")
            raise

    @patch('app.check_email')
    @patch('app.db')
    def test_create_account_no_password(self, mock_db, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)

            mock_db.UserInfos.find_one = MagicMock(return_value={"EmailAddress": "existinguser@example.com"})

            user_update_data = {
                "EmailAddress": "existinguser@example.com",
            }

            response = self.app.post('/create-account', json=user_update_data)

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data['Success'])
            self.assertEqual(json_data['Error'], "Did not provide password.")

            mock_db.UserInfos.update_one.assert_not_called()
        except Exception as e:
            print(f"create_account2 raise errors, {e}")
            raise
    @patch('app.check_email')
    @patch('app.db')
    def test_create_account(self, mock_db, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)

        
            mock_db.UserInfos.find_one = MagicMock(return_value=None)
            mock_db.UserInfos.update_one = MagicMock()
            mock_db.UserInfos.insert_one = MagicMock(return_value=MagicMock(inserted_id=ObjectId()))

        
            new_user_data = {
                "EmailAddress": "newuser@example.com",
                "Password": "newpassword",
            }

        
            response = self.app.post('/create-account', json=new_user_data)

       
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])

        
            mock_db.UserInfos.find_one.assert_called_once_with({'EmailAddress': 'newuser@example.com'})
            mock_db.UserInfos.insert_one.assert_called_once()
        except Exception as e:
            print(f"create_account3 raise errors, {e}")
            raise
    def test_login_no_email(self):
        data={}
        try:
            response=self.app.post('/login',data=data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"login raise2 errors, {e}")
            raise
    def test_login_pw_fail(self):
        try:
            data={'EmailAddress': "x89zhang@uwaterloo.ca"}
            response=self.app.post('/login',data=data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"login raise3 errors, {e}")
            raise
    def test_get_user_info_no_email(self):
        try:
            response=self.app.get('/get-user-info?EmailAddress=')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"get_user_info1 raise errors, {e}")
            raise
    def test_get_user_info(self):
        try:
            response=self.app.get('/get-user-info?EmailAddress=x89zhang@uwaterloo.ca')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"get_user_info2 raise errors: {e}")
            raise
    def test_send_message_no_valid_email(self):
        try:
            data={'Sender': "invalid_email"}
            headers = {"Content-Type": "application/json"}
            response=self.app.post('/send-message',json=data, headers=headers)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
            self.assertEqual(response.json["Error"],"invalid_email is not a email address!")
        except Exception as e:
            print(f"send_message1 raise errors: {e}")
            raise  

    def test_send_message_no_valid_receiver(self):
        try:
            data={'Sender': "x89zhang@uwaterloo.ca", 'Receiver': "invalid_email"}
            headers={"Content-Type": "application/json"}
            response=self.app.post('/send-message',json=data,headers=headers)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"send_message2 raise errors: {e}")
            raise

    def test_send_message_no_valid_content(self):
        try:
            data={'Sender': "x89zhang@uwaterloo.ca", 'Receiver': "281750569@qq.com"}
            headers={"Content-Type": "application/json"}
            response=self.app.post('/send-message',json=data,headers=headers)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"send_message3 raise errors.")
            raise
    def test_send_message_correct(self):
        try:
            content={"Text": "test"}
            data={'Sender': "x89zhang@uwaterloo.ca", 'Receiver': "s354wang@uwaterloo.ca", 'Content': content}
            headers={"Content-Type": "application/json"}
            response=self.app.post('/send-message',json=data,headers=headers)
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"send_message4 raise errors: {e}")
            raise
    @patch('app.check_email')
    @patch('app.db')
    def test_send_message_empty_content(self, mock_db, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)

            response = self.app.post('/send-message', json={
                'Sender': 'valid_sender@example.com',
                'Receiver': 'valid_receiver@example.com',
                'Content': {}
            })
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data["Success"])
            self.assertEqual(json_data["Error"], "Empty content!")
        except Exception as e:
            print(f"send_message5 raise errors: {e}")
            raise
    @patch('app.check_email')
    @patch('app.db')
    def test_send_message_new_chat(self, mock_db, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)

    # 模拟数据库中没有现有聊天记录
            mock_db.Messages.find_one.return_value = None
            mock_db.Messages.insert_one = MagicMock()

    # 发送消息
            response = self.app.post('/send-message', json={
                'Sender': 'valid_sender@example.com',
                'Receiver': 'valid_receiver@example.com',
                'Content': {'Text': 'Hello!'}
            })

    # 验证响应
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])

    # 验证数据库插入操作是否如预期执行了两次
            calls = [
                call({
                    'Contents': [{'Text': 'Hello!', 'CreateTime': mock.ANY}],
                    'Sender': 'valid_sender@example.com',
                    'Receiver': 'valid_receiver@example.com',
                    'CreateTime': mock.ANY,
                    'UpdateTime': mock.ANY
                }),
                call({
                    'Contents': [{'Text': 'Auto reply: please wait for response.', 'Image': None, 'CreateTime': mock.ANY}],
                    'Sender': 'valid_receiver@example.com',
                    'Receiver': 'valid_sender@example.com',
                    'CreateTime': mock.ANY,
                    'UpdateTime': mock.ANY
                })
            ]
            mock_db.Messages.insert_one.assert_has_calls(calls, any_order=True)
        except Exception as e:
            print(f"send_message6 raise errors: {e}")
            raise
    def test_get_message_no_valid_email(self):
        try:
            data={'EmailAddress': "invalid_email"}
            response=self.app.post('/get-message',data=data)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"get_message1 raise errors: {e}")
            raise
    def test_get_message_wrong_password(self):
        try:
            data={'EmailAddress': "x89zhang@uwaterloo.ca"}
            response=self.app.post('/get-message',data=data)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"get_message2 raise errors: {e}")
            raise
    def test_get_message_correct_no_sender_given(self):
        try:
            data={'EmailAddress': "x89zhang@uwaterloo.ca", 'Password': "123456"}
            response=self.app.post('/get-message',data=data)
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"get_message3 raise errors: {e}")
            raise
    def test_get_message_correct_with_sender_given(self):
        try:
            data={'EmailAddress': "x89zhang@uwaterloo.ca", 'Password': "123456", 'Sender': "281750569@qq.com"}
            response=self.app.post('/get-message',data=data)
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"get_message4 raise errors: {e}")
            raise
    def test_new_post_no_email(self):
        try:
            data={}
            headers={"Content-Type": "application/json"}
            response=self.app.post('/new-post',json=data,headers=headers)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"new_post1 raise errors: {e}")
            raise
    @patch('app.check_email')
    @patch('app.db')
    def test_new_post(self, mock_db, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)

            mock_db.Posts.insert_one = MagicMock(return_value=MagicMock(inserted_id='mock_id'))

            new_post_data = {
                "PostOwner": "test@example.com",
                "Title": "Test Title",
                "Text": "Test Content",
                "Images": ["img1.png", "img2.png"],
                "Price": 100,
                "Fields": ["Field1", "Field2"],
                "Auction": False,
                "LostFound": False
            }
            response = self.app.post('/new-post', json=new_post_data)

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])

            mock_db.Posts.insert_one.assert_called_once()
        except Exception as e:
            print(f"new_post2 raise errors: {e}")
            raise
    def test_delete_post_invalid_email(self):
        try:
            data={'EmailAddress': "invalid_email"}
            response=self.app.post('/delete-post',data=data)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"delete_post1 raise errors: {e}")
            raise
    def test_delete_post_wrong_password(self):
        try:
            data={'EmailAddress': "x89zhang@uwaterloo.ca"}
            response=self.app.post('/delete-post',data=data)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except:
            print("delete_post2 raise errors.")
    def test_delete_post_invalid_pid(self):
        try:
            data={'EmailAddress': "x89zhang@uwaterloo.ca", 'Password': "123456"}
            response=self.app.post('/delete-post',data=data)
            self.assertEqual(response.status_code,200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"delete_post3 raise errors: {e}")
            raise
    @patch('app.check_email')
    @patch('app.check_password')
    @patch('app.check_post')
    @patch('app.db')
    def test_delete_post_correct(self, mock_db, mock_check_post, mock_check_password, mock_check_email):
        try:
            dummy_object_id = str(ObjectId())

            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (True, None)
            mock_check_post.return_value = (True, None)

            fake_post = {'_id': ObjectId(dummy_object_id), 'PostOwner': 'test@example.com'}
            mock_db.Posts.find_one.return_value = fake_post
            mock_db.Posts.update_one = MagicMock()

            response = self.app.post('/delete-post', data={
                'EmailAddress': 'test@example.com',
                'Password': 'valid_password',
                'PID': dummy_object_id
            })

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])

            expected_calls = [
                call({'_id': ObjectId(dummy_object_id)}, {'$set': {'Deleted': True}}),
                call({'_id': ObjectId(dummy_object_id)}, {'$set': {'UpdateTime': mock.ANY}})
            ]
            mock_db.Posts.update_one.assert_has_calls(expected_calls, any_order=True)

        except Exception as e:
            print(f"delete_post4 raise errors: {e}")
            raise
    @patch('app.check_email')
    @patch('app.check_password')
    @patch('app.check_post')
    @patch('app.db')
    def test_delete_post_not_owner(self, mock_db, mock_check_post, mock_check_password, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_password.return_value = (True, None)
            mock_check_post.return_value = (True, None)

            dummy_object_id = str(ObjectId())

            fake_post = {'_id': ObjectId(dummy_object_id), 'PostOwner': 'other@example.com'}
            mock_db.Posts.find_one.return_value = fake_post

            response = self.app.post('/delete-post', data={
                'EmailAddress': 'test@example.com',
                'Password': 'valid_password',
                'PID': dummy_object_id
            })

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data['Success'])
            self.assertEqual(json_data['Error'], 'You are not the owner of this post!')

            mock_db.Posts.update_one.assert_not_called()
        except Exception as e:
            print(f"delete_post5 raise errors: {e}")
            raise



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
            self.assertEqual(response.json['Error'], "invalid_email_format is not a email address!")
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
    @mock.patch('app.check_password')
    @mock.patch('app.db')
    def test_sold_post_invalid_password(self, mock_db, mock_check_password):
        try:
            mock_check_password.return_value = (False, "Invalid password")
            response = self.app.post('/sold-post', data={'EmailAddress': 'user@example.com', 'Password': 'wrongpass', 'PID': str(ObjectId())})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
            self.assertEqual(response.json["Error"], "Invalid password")
        except Exception as e:
            print("test_sold_post_invalid_password raised an error:", e)
            raise
    @mock.patch('app.check_post')
    @mock.patch('app.check_password')
    @mock.patch('app.db')
    def test_sold_post_invalid_post(self, mock_db, mock_check_password, mock_check_post):
        try:
            mock_check_password.return_value = (True, None)
            mock_check_post.return_value = (False, "Post does not exist")
            response = self.app.post('/sold-post', data={'EmailAddress': 'user@example.com', 'Password': 'password', 'PID': str(ObjectId())})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
            self.assertEqual(response.json["Error"], "Post does not exist")
        except Exception as e:
            print("test_sold_post_invalid_post raised an error:", e)
            raise
    @mock.patch('app.check_post')
    @mock.patch('app.check_password')
    @mock.patch('app.db')
    def test_sold_post_not_owner(self, mock_db, mock_check_password, mock_check_post):
        try:
            mock_check_password.return_value = (True, None)
            mock_check_post.return_value = (True, None)
            dummy_object_id = ObjectId()
            mock_db.Posts.find_one.return_value = {'_id': dummy_object_id, 'PostOwner': 'anotheruser@example.com'}
            response = self.app.post('/sold-post', data={'EmailAddress': 'user@example.com', 'Password': 'password', 'PID': str(dummy_object_id)})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
            self.assertEqual(response.json["Error"], "You are not the owner of this post or post does not exist.")
        except Exception as e:
            print("test_sold_post_not_owner raised an error:", e)
            raise
    @mock.patch('app.check_post')
    @mock.patch('app.check_password')
    @mock.patch('app.db')
    def test_sold_post_successful(self, mock_db, mock_check_password, mock_check_post):
        try:
            mock_check_password.return_value = (True, None)
            mock_check_post.return_value = (True, None)
            dummy_object_id = ObjectId()
            mock_db.Posts.find_one.return_value = {'_id': dummy_object_id, 'PostOwner': 'user@example.com'}
            mock_db.Posts.update_one = mock.MagicMock()
            response = self.app.post('/sold-post', data={'EmailAddress': 'user@example.com', 'Password': 'password', 'PID': str(dummy_object_id)})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
            mock_db.Posts.update_one.assert_called_with({'_id': dummy_object_id}, {'$set': {'IsSold': True}})
        except Exception as e:
            print("test_sold_post_successful raised an error:", e)
            raise



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