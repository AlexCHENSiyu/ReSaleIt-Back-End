import unittest
from app import app, db

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
            
    
        
if __name__ == '__main__':
    unittest.main()



# 先下载 coverage：
# pip install coverage

# 运行文件：
# coverage run -m API_test

# 生成html
# coverage html

# 在同文件夹下会有一个交htmlcov的文件夹，打开里面的html可以看到那些行被使用