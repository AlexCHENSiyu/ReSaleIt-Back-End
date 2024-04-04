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
    


    # email-no-exist
    def test_EmailNoExist_1(self):
        try:
            response = self.app.get('/email-no-exist?EmailAddress=1030920919@qq.com')  
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except:
            print("test_EmailNoExist_1 raise errors.")
    
   

    #login
    def test_Login_1(self):
        try:
            data = {'EmailAddress': '1030920919@qq.com', 'Password': 1234}  
            response = self.app.post('/login', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
        except:
            print("test_Login_1 raise errors.")

    

    #email-no-exist
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
            mock_db.UserInfos.find_one.return_value = {'EmailAddress': '1030920919@qq.com', 'Password': None}
            response = self.app.get('/email-no-exist?EmailAddress=1030920919@qq.com')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["Success"])
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
    

    #email-validation
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
    @patch('app.send_valid_code')
    @patch('app.db')
    def test_email_validation_code_match(self, mock_db, mock_send_valid_code):
        code = '123456'
        # 直接在 mock_db 对象上模拟 UserInfos.find_one 方法
        mock_db.UserInfos.find_one = MagicMock(return_value={'EmailAddress': 'test@example.com', 'ValidCode': code})
        mock_send_valid_code.return_value = (True, None)  # 假设验证码发送成功

        response = self.app.get(f'/email-validation?EmailAddress=test@example.com&InputCode={code}')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['Success'])

        # 确保没有调用数据库更新和插入操作
        mock_db.UserInfos.update_one.assert_not_called()
        mock_db.UserInfos.insert_one.assert_not_called()
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
    
    
    
    
    #set-reset-password
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
    



    #create-account
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
    def test_create_account_existing_email(self, mock_db, mock_check_email):
        try:
            existing_email = 'existing_email@example.com'
            mock_db.UserInfos.find_one.return_value = {'EmailAddress': existing_email}
            mock_check_email.return_value = (True, None)
            mock_db.UserInfos.update_one = MagicMock()
            mock_db.UserInfos.insert_one = MagicMock()
            user_data = {
                "EmailAddress": existing_email,
                "Password": "newpassword",
            }
            response = self.app.post('/create-account', json=user_data)
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data['Success'])  
            mock_db.UserInfos.find_one.assert_called_once_with({'EmailAddress': existing_email})
            mock_db.UserInfos.update_one.assert_not_called()
            mock_db.UserInfos.insert_one.assert_not_called()
            mock_db.reset_mock()
        except Exception as e:
            print(f"create_account_existing_email test raised errors, {e}")
            raise
    def test_create_account_wrong_password(self):
        try:
            response=self.app.post('/create-account',json={'EmailAddress': "x89zhang@uwaterloo.ca", 'Password': "000000"})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json["Success"])
        except Exception as e:
            print(f"create_account3 raise errors: {e}")
            raise
    
    



    #login
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
    
    
    
    
    #get-user-info
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
    
    
    
    
    #send-message
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

            mock_db.Messages.find_one.return_value = None
            mock_db.Messages.insert_one = MagicMock()

            response = self.app.post('/send-message', json={
                'Sender': 'valid_sender@example.com',
                'Receiver': 'valid_receiver@example.com',
                'Content': {'Text': 'Hello!'}
            })

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])

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
    
    
    
    
    #get-message
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
            data={'EmailAddress': "x89zhang@uwaterloo.ca", 'Password': "123456", 'Sender': "r9qian@uwaterloo.ca"}
            response=self.app.post('/get-message',data=data)
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.json["Success"])
        except Exception as e:
            print(f"get_message4 raise errors: {e}")
            raise
    
    
    
    
    #new-post
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
    
    
    
    
    #delete-post
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




    #get-post
    

    def test_get_post_history_invalid_email_format(self):
        try:
            params = {'EmailAddress': 'invalid_email_format'}
            response = self.app.get('/get-post-history', query_string=params)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "invalid_email_format is not a email address!")
        except Exception as e:
            print("test_get_post_history_invalid_email_format raised an error:", e)




    #click-post
    @patch('app.db')
    @patch('app.check_email')
    @patch('app.check_post')
    def test_click_post_success(self,mock_check_post,mock_check_email,mock_db):
        try:
            valid_pid = str(ObjectId())
            valid_email = "valid_email@example.com"
            mock_check_email.return_value = (True, None)
            mock_check_post.return_value = (True, None)
            mock_db.UserInfos.find_one = MagicMock(return_value={'EmailAddress': valid_email, 'PostHistory': []})
            mock_db.Posts.find_one = MagicMock(return_value={'_id': valid_pid, 'Count': '1'})
            mock_db.Posts.update_one = MagicMock()
            mock_db.UserInfos.update_one = MagicMock()
            response = self.app.get(f'/click-post?EmailAddress={valid_email}&PID={valid_pid}')
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])
            mock_db.Posts.update_one.assert_called()
            mock_db.UserInfos.update_one.assert_called()
        except Exception as e:
            print("test_click_post_success raised an error:", e)


    def test_click_post_invalid_email_format(self):
        try:
            params = {'EmailAddress': 'invalid_email_format', 'PID': '65a199aaa2c14c072766377a'}
            response = self.app.get('/click-post', query_string=params)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "invalid_email_format is not a email address!")
        except Exception as e:
            print("test_click_post_invalid_email_format raised an error:", e)



    #post-comment
    def test_post_comment_success(self):
        try:
            data = {
                'Commenter': 'commenter@example.com',
                'PID': '65a199aaa2c14c072766377a',
                'Text': 'This is a test comment.'
            }
            mock_user_info = {
                'EmailAddress': 'commenter@example.com',
                'NickName': 'Test Commenter',
                'HeadPortrait': 'avatar_url'
            }
            mock_post = {
                '_id': '65a199aaa2c14c072766377a',
                'Comments': []
            }
            self.mock_user_infos.find_one.return_value = mock_user_info
            self.mock_posts.find_one.return_value = mock_post
            response = self.app.post('/post-comment', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json['Success'])
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
            params = {'EmailAddress': '1030920919@qq.com'}
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
            self.mock_posts.find.return_value.limit.return_value = mock_user_posts
            response = self.app.get('/user-posts', query_string=params)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json['Success'])
            posts = response.json['Posts']
            self.assertEqual(len(posts), 2)
            self.assertEqual(posts[0]['PID'], 'post_id_1')
            self.assertEqual(posts[0]['PostOwner'], '1030920919@qq.com')
            self.assertEqual(posts[0]['CreateTime'], '2024-02-15 10:00:00')
            self.assertEqual(posts[1]['PID'], 'post_id_2')
            self.assertEqual(posts[1]['Title'], 'Title 2')
            self.assertEqual(posts[1]['Price'], 200)
        except Exception as e:
            print("test_user_posts_success raised an error:", e)
    @patch('app.check_email')
    @patch('app.check_post')
    def test_post_comment_invalid_pid(self, mock_check_post, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)

            mock_check_post.return_value = (False, "Invalid PID!")

            test_comment_data = {
                "Commenter": "commenter@example.com",
                "PID": "invalid_pid",
                "Text": "This is a test comment"
            }

            response = self.app.post('/post-comment', data=test_comment_data)

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data['Success'])
            self.assertEqual(json_data['Error'], "Invalid PID!")
        except Exception as e:
            print("test_post_comment_invalid_pid raised an error:", e)
            raise

    @patch('app.check_email')
    @patch('app.check_post')
    def test_post_comment_no_text(self, mock_check_post, mock_check_email):
        try:
            mock_check_email.return_value = (True, None)
            mock_check_post.return_value = (True, None)

            test_comment_data = {
                "Commenter": "commenter@example.com",
                "PID": "valid_pid",
            }

            response = self.app.post('/post-comment', data=test_comment_data)

            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data['Success'])
            self.assertEqual(json_data['Error'], "No text provided!")
        except Exception as e:
            print("test_post_comment_no_text raised an error:", e)
            raise
    @patch('app.db')
    def test_post_comment_existing_comments(self, mock_db):
        mock_pid = str(ObjectId())
        pid = mock_pid
        commenter_email = 'commenter@example.com'
        comment_text = 'This is a comment'
        mock_db.UserInfos.find_one.return_value = {
            'EmailAddress': commenter_email,
            'NickName': 'CommenterNick',
            'HeadPortrait': 'head_portrait.png'
        }
        existing_comments = [{'Text': 'Existing comment', 'Commenter': 'existing@example.com'}]
        mock_db.Posts.find_one.return_value = {
            '_id': pid,
            'Comments': existing_comments,
            'Deleted': False
        }
        mock_db.Posts.update_one.return_value = None
        response = self.app.post('/post-comment', data={
            'Commenter': commenter_email,
            'PID': pid,
            'Text': comment_text
        })
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['Success'])
        new_comment = {
            'Commenter': commenter_email,
            'Text': comment_text,
            'NickName': 'CommenterNick',
            'HeadPortrait': 'head_portrait.png'
        }
        existing_comments.append(new_comment)
        mock_db.Posts.update_one.assert_called_once_with({'_id': ObjectId(pid)}, {"$set": {'Comments': existing_comments}})
    @patch('app.db')
    def test_post_comment_no_existing_comments(self, mock_db):
        mock_pid = str(ObjectId())
        commenter_email = 'new_commenter@example.com'
        pid = mock_pid
        comment_text = 'New comment'
        mock_db.UserInfos.find_one.return_value = {
            'EmailAddress': commenter_email,
            'NickName': 'CommenterNick',
            'HeadPortrait': 'head_portrait.png'
        }
        mock_db.Posts.find_one.return_value = {
            '_id': pid,
            'Comments': [],
            'Deleted': False
        }
        mock_db.Posts.update_one.return_value = None
        test_comment_data = {
            "Commenter": commenter_email,
            "PID": pid,
            "Text": comment_text,
        }
        response = self.app.post('/post-comment', data=test_comment_data)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['Success'])
        expected_comments = [{
            'Commenter': commenter_email,
            'Text': comment_text,
            'NickName': 'CommenterNick',
            'HeadPortrait': 'head_portrait.png',
            'CreateTime': mock.ANY  
        }]
        mock_db.Posts.update_one.assert_called_once_with(
            {'_id': ObjectId(pid)},
            {"$set": {'Comments': expected_comments}}
        )

    def test_user_posts_invalid_email_format(self):
        try:
            params = {'EmailAddress': 'invalid_email_format'}
            response = self.app.get('/user-posts', query_string=params)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "invalid_email_format is not a email address!")
        except Exception as e:
            print("test_user_posts_invalid_email_format raised an error:", e)
    def test_post_comment_no_text(self):
        try:
            data = {
                'Commenter': 'commenter@example.com',
                'PID': '65a199aaa2c14c072766377a',
                'Text': ''
            }
            response = self.app.post('/post-comment', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json['Success'])
            self.assertEqual(response.json['Error'], "Did not find account. Please try it again!")
        except Exception as e:
            print("test_post_comment_no_text raised an error:", e)

    @patch('app.db')
    def test_get_posts_with_keyword(self,mock_db):
        try:
            valid_email = "valid_email@example.com"
            mock_posts = [
                {'_id': str(ObjectId()), 'Title': 'Post 1', 'Text': 'Content 1', 'Score': 1.0},
                {'_id': str(ObjectId()), 'Title': 'Post 2', 'Text': 'Content 2', 'Score': 2.0},
            ]
            mock_db.UserInfos.find_one.return_value = {'EmailAddress': valid_email}
            mock_db.Posts.find.return_value = MagicMock(return_value=mock_posts)
            mock_db.Posts.aggregate.return_value = MagicMock(return_value=mock_posts)
            response = self.app.get(f'/get-posts?EmailAddress={valid_email}&Keyword=Post')
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data['Success'])
            self.assertGreaterEqual(len(json_data['Posts']), 1)
            self.assertEqual(json_data['Posts'][0]['Title'], 'Post 1')
            self.mock_db.Posts.find.assert_called()
            self.mock_db.Posts.aggregate.assert_not_called()
        except Exception as e:
            print("test_get_posts_with_keyword raised an error:", e)

    def test_get_posts_without_keyword(self):
        try:
            data = {
                "EmailAddress": "1030920919@qq.com",
                "Num": 6
            }
            response = self.app.get('/get-posts', query_string=data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json['Success'])
            self.assertTrue(response.json['Posts'])
        except Exception as e:
            print("test_get_posts_without_keyword raised an error:", e)
    @mock.patch('app.check_password')
    def test_sold_post_invalid_password(self, mock_check_password):
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
    def test_sold_post_invalid_post(self, mock_check_password, mock_check_post):
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
    @patch('app.db')
    def test_click_post(self, mock_db):
        try:
            mock_pid = str(ObjectId())
            mock_email = "user@example.com"
            mock_post = {"_id": mock_pid, "Count": "5", "Deleted": False}
            mock_userinfo = {"EmailAddress": mock_email, "PostHistory": []}
            mock_db.Posts.find_one.return_value = mock_post
            mock_db.UserInfos.find_one.return_value = mock_userinfo
            response = self.app.get(f'/click-post?EmailAddress={mock_email}&PID={mock_pid}')
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertTrue(json_data["Success"])
            updated_count = str(int(mock_post["Count"]) + 1)
            mock_db.Posts.update_one.assert_called_once_with({'_id': ObjectId(mock_pid)}, {"$set": {'Count': updated_count}})
            updated_post_history = mock_userinfo["PostHistory"] + [mock_pid]
            mock_db.UserInfos.update_one.assert_called_once_with({'EmailAddress': mock_email}, {"$set": {'PostHistory': updated_post_history}})
        except Exception as e:
            print("test_click_post raised an error:", e)
            raise
    @patch('app.db')
    def test_click_post_invalid_pid(self, mock_db):
        try:
            invalid_pid = "invalid_pid"
            valid_email = "user@example.com"
            mock_db.Posts.find_one.return_value = None
            mock_userinfo = {"EmailAddress": valid_email}
            mock_db.UserInfos.find_one.return_value = mock_userinfo
            response = self.app.get(f'/click-post?EmailAddress={valid_email}&PID={invalid_pid}')
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data["Success"])
            self.assertEqual(json_data["Error"], "Invalid PID!")
            mock_db.Posts.update_one.assert_not_called()
            mock_db.UserInfos.update_one.assert_not_called()
        except Exception as e:
            print("test_click_post_invalid_pid raised an error:", e)
            raise
    @patch('app.db')
    def test_click_post_account_not_exist(self, mock_db):
        try:
            non_existent_email = "nonexistent@example.com"
            valid_pid = str(ObjectId())
            mock_db.UserInfos.find_one.return_value = None
            mock_db.Posts.find_one.return_value = {'_id': valid_pid}
            response = self.app.get(f'/click-post?EmailAddress={non_existent_email}&PID={valid_pid}')
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertFalse(json_data["Success"])
            self.assertEqual(json_data["Error"], "Did not find account. Please try it again!")
            mock_db.Posts.update_one.assert_not_called()
            mock_db.UserInfos.update_one.assert_not_called()
        except Exception as e:
            print("test_click_post_account_not_exist raised an error:", e)
            raise
    @patch('app.db')
    @patch('app.check_email')
    def test_get_post_history_with_existing_records(self, mock_check_email, mock_db):
        mock_pid=ObjectId()
        mock_check_email.return_value = (True, None)
        email = "user@example.com"
        mock_history = [str(mock_pid)]
        mock_user_info = {'EmailAddress': email, 'PostHistory': mock_history}
        mock_db.UserInfos.find_one.return_value = mock_user_info

        mock_post_data = {
            '_id': ObjectId(mock_history[0]),
            'PostOwner': 'owner@example.com',
            'Deleted': False
        }
        mock_db.Posts.find_one.return_value = mock_post_data
        response = self.app.get(f'/get-post-history?EmailAddress={email}')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['Success'])
        self.assertEqual(len(json_data['Posts']), len(mock_history))
        mock_db.reset_mock()
    @patch('app.db')
    @patch('app.check_email')
    def test_get_post_history_without_records(self, mock_check_email, mock_db):
        mock_check_email.return_value = (True, None)
        email = "user@example.com"
        mock_user_info = {'EmailAddress': email}
        mock_db.UserInfos.find_one.return_value = mock_user_info
        mock_db.Posts.find_one.return_value = None
        response = self.app.get(f'/get-post-history?EmailAddress={email}')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['Success'])
        self.assertEqual(len(json_data['Posts']), 0)
        mock_db.reset_mock()


    @patch('app.check_email')
    @patch('app.db')
    def test_create_account_correct_password(self,mock_db, mock_check_email):
        mock_check_email.return_value = (True, None)
        mock_db.UserInfos.find_one = MagicMock(return_value={'EmailAddress': 'existing_user@example.com', 'Password': 'correct_password'})
        mock_db.UserInfos.update_one = MagicMock()
        new_account_data = {
            "EmailAddress": "existing_user@example.com",
            "Password": "correct_password",
            "FirstName": "Test",
            "LastName": "User",
            "StudentID": "00000000",
            "NickName": "Test User",
            "HeadPortrait": "default.png",
            "Birthday": "2000-01-01",
            "Gender": "Male",
            "PhoneNumber": "123456789",
            "Profile": "This is a test profile.",
            "Region": "Waterloo",
            "FavoriteFields": [],
        }
        response = self.app.post('/create-account', json=new_account_data)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data['Success'])
        newuserinfo= {'StudentID': '00000000', 'FirstName': 'Test', 'LastName': 'User', 'NickName': 'Test User', 'Birthday': '2000-01-01', 'Gender': 'Male', 'Profile': 'This is a test profile.', 'Region': 'Waterloo', 'PhoneNumber': '123456789', 'HeadPortrait': 'default.png'}
        mock_db.UserInfos.update_one.assert_called_once_with({'EmailAddress': 'existing_user@example.com'}, {"$set": newuserinfo})
    






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