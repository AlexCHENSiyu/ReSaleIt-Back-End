from flask import Flask, request, Blueprint
import pymongo
import numpy as np
import json
from bson import ObjectId
#import base64
from pymongo.database import Database 
from datetime import date, datetime
from datetime import datetime
from pyisemail import is_email
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from random import randint
from operator import itemgetter
from collections import Counter


# Helper function
def mongodb_init():
    # connect to mongodb
    mongo = pymongo.MongoClient(host='18.162.214.19', port=27017, username="root", password="1647#4hkust",
                                authSource='admin')
    print('数据库当前的databases: ', mongo.list_database_names())
    return mongo


def get_db(mongo, db_name):
    db = Database(name=db_name, client=mongo)
    print('获取/创建库：', db.name)
    return db


def get_time_attribute(type):
    # generate current time
    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if type == 'update':
        return {'UpdateTime': now_time}
    elif type == 'create':
        return {'CreateTime': now_time, 'UpdateTime': now_time, 'CodeTime': now_time}
    elif type == 'create withour code':
        return {'CreateTime': now_time, 'UpdateTime': now_time}
    elif type == 'only create':
        return {'CreateTime': now_time}
    elif type == 'code':
        return {'UpdateTime': now_time, 'CodeTime': now_time}

    print("Please input type = 'update', 'create', 'create withour code', 'only create', 'code' ")
    return 0


def send_valid_code(email_address, code):
    # 向邮箱提供验证码

    my_user = "1030920919@qq.com"  # 收件人邮箱
    my_pass = 'VTEXDKFIHHRFECIK'  # 授权码
    title = 'Your one-time validation code!'  # 标题
    sender_name = '[Campus-Transaction] Team'  # 发件人名称
    my_sender = 'schendf@163.com'  # 发件者邮箱
    content = "Dear user:\n\n \
              We have received your request for a one-time code for your Campus-Transaction account.\n\n \
              Your Campus-Transaction Validation code is {0}.\n\n \
              If you did not request this code, you can safely ignore this email. Someone may have mistyped your email address.\n\n \
              Thank you for using!\n\n \
              Campus-Transaction team\n".format(code)  # 内容
    success = True
    err = 'None'

    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = title
        msg['From'] = formataddr([sender_name, my_sender])
        msg['To'] = formataddr(["FK", my_user])

        server = smtplib.SMTP_SSL("smtp.163.com", 465)  # (host, port)
        server.login(my_sender, my_pass)  # 登录发送邮箱
        server.sendmail(my_sender, [email_address, ], msg.as_string())
        server.quit()
    except Exception as e:
        success = False
        err = str(e)

    return [success, err]


def check_email(EmailAddress):
    # 检查邮件：1.是否为空；2.是否是邮件格式；3.实在在mongodb内创建账户
    Success = True
    Error = ""
    if not EmailAddress:
        # 没有提供邮箱
        Success = False
        Error = "Did not provide email address."
        return Success, Error
    elif not is_email(EmailAddress):
        # 邮箱格式错误，直接报错
        Success = False
        Error = EmailAddress + " is not a email address!"
        return Success, Error

    UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
    if not UserInfo:
        # 此账户不存在
        Success = False
        Error = "Did not find account. Please try it again!"
        return Success, Error
    return Success, Error


def check_password(EmailAddress,Password):
    # 检查密码：1.是否为空； 2.账户是否存在； 3.账户是否设置密码； 4.密码是否正确；
    Success = True
    Error = ""

    if not Password:
        # 没有提供密码
        Success = False
        Error = "Did not provide password."
        return Success,Error

    UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
    if UserInfo:
        # 此账户已存在
        if not UserInfo.get('Password'):
            # 此账户没有设置密码
            Success = False
            Error = "This account has no password!"
        elif Password == UserInfo['Password']:
            # 密码正确
            Success = True
        else:
            # 密码错误
            Success = False
            Error = "Wrong password!"
    else:
        # 此账户不存在
        Success = False
        Error = "Did not find account. Please try it again!"
    return Success,Error


def check_post(PID):
    # 检查：1.PID是否为空, 2.PID是否格式正确； 3.帖子是否存在； 4.帖子是否被删除。
    Success = True
    Error = ""

    if not PID:
       # 没有提供post编号
        Success = False
        Error = "Did not provide PID."
        return Success,Error
    
    try:
        _id = ObjectId(PID)
    except:
        # PID格式不对
        Success = False
        Error = "Invalid PID!"
        return Success,Error

    Post = db.Posts.find_one({'_id': _id})
    if Post:
        # 该帖子存在
        if Post['Deleted']:
            # 帖子早已被删除
            Success = False
            Error = "Post already deleted!"
            return Success,Error
    else:
        # 该帖子不存在
        Success = False
        Error = 'PID does not exist!'
        return Success,Error

    return Success,Error
    

def get_list(content):    
    return datetime.strptime(content['CreateTime'], '%Y-%m-%d %H:%M:%S').timestamp()


def merge_lists(list1, list2, key):
    merged_list = list1 + list2
    seen = set()
    new_list = []
    for dict_ in merged_list:
        value = dict_[key]
        if value not in seen:
            seen.add(value)
            new_list.append(dict_)
    return new_list


# API below
app = Flask(__name__)
mongo = mongodb_init()
db = get_db(mongo, 'chen_db')


@app.route('/drop-table')
# http://localhost:5000/drop_table
def DropAllTable():
    return_data = {}

    TableName = request.args.get("TableName")
    if not TableName:
        # 没有指明TableName，全部删除
        db.UserInfos.drop()
        db.Messages.drop()
        db.Posts.drop()
        return_data["Success"] = True
    elif TableName == 'UserInfos':
        db.UserInfos.drop()
        return_data["Success"] = True
    elif TableName == 'Messages':
        db.Messages.drop()
        return_data["Success"] = True
    elif TableName == 'Posts':
        db.Posts.drop()
        return_data["Success"] = True
    else:
        return_data["Success"] = False
        return_data['Error'] = 'Can not find the table!'
    return return_data


@app.route('/email-no-exist', methods=["GET"])
# http://localhost:8080/email-no-exist?EmailAddress=1030920919@qq.com
def EmailNoExist():
    return_data = {}
    
    EmailAddress = request.args.get("EmailAddress")
    if not EmailAddress:
        # 没有提供邮箱
        return_data["Success"] = False
        return_data['Error'] = "Did not provide email address."
        return return_data
    elif not is_email(EmailAddress):
        # 邮箱格式错误，直接报错
        return_data["Success"] = False
        return_data['Error'] = EmailAddress + " is not a email address!"
        return return_data
    
    UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
    if UserInfo:
        # 此账户已存在
        if UserInfo.get("Password") is None:
            # 创建账户时候未设置密码,认为没创建账户，允许发送验证码
            return_data["Success"] = True
        else:
            # 有账户并设置密码，不允许此邮箱再创建账户
            return_data["Success"] = False
            return_data['Error'] = "This Email address already has an account!"
    else:
        # 账户未创建
        return_data["Success"] = True
    
    return return_data

@app.route('/email-validation', methods=["GET"])
# http://localhost:5000/email-validation?EmailAddress=1030920919@qq.com
# http://localhost:5000/email-validation?EmailAddress=1030920919@qq.com&InputCode=123456
# http://16.162.42.168/chen/email-validation?EmailAddress=1030920919@qq.com
def EmailValidation():
    return_data = {}

    EmailAddress = request.args.get("EmailAddress")
    if not EmailAddress:
        # 没有提供邮箱
        return_data["Success"] = False
        return_data['Error'] = "Did not provide email address."
        return return_data
    elif not is_email(EmailAddress):
        # 邮箱格式错误，直接报错
        return_data["Success"] = False
        return_data['Error'] = EmailAddress + " is not a email address!"
        return return_data

    InputCode = request.args.get("InputCode")
    if not InputCode:
        # 没有InputCode,且时间大于120s,向邮箱提供验证码
        UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
        if UserInfo:
            # 若账户信息已存在,则检查是否在120s以内已经发送过邮件了
            TimeAttribute = get_time_attribute('code')
            NewCodeTime = datetime.strptime(TimeAttribute["CodeTime"], '%Y-%m-%d %H:%M:%S')
            LastCodeTime = datetime.strptime(UserInfo["CodeTime"], '%Y-%m-%d %H:%M:%S')
            if (NewCodeTime - LastCodeTime).seconds < 120:
                # 距离上一次发送验证码的时间小于120s,不能发送
                return_data["Success"] = False
                return_data["Error"] = "Already send email, please try it later!"
                return return_data

        # 若账户信息不存在，则直接发送过邮件了
        code = randint(100000, 999999)  # 随机验证码
        success, error = send_valid_code(EmailAddress, code)  # 发送此验证码，得到返回

        if success:
            # 如果成功发送验证码，则更新账户信息
            if UserInfo:
                # 此账户已存在
                TimeAttribute = get_time_attribute('code')
                db.UserInfos.update_one({'EmailAddress': EmailAddress}, {"$set": TimeAttribute})
                db.UserInfos.update_one({'EmailAddress': EmailAddress}, {"$set": {'ValidCode': str(code)}})
            else:
                # 账户未创建
                NewUserInfo = {"EmailAddress": EmailAddress, "ValidCode": str(code)}
                TimeAttribute = get_time_attribute('create')
                NewUserInfo.update(TimeAttribute)  # 设置创建和修改时间
                db.UserInfos.insert_one(NewUserInfo)  # 向数据库插入此新账户
            return_data["Success"] = True
        else:
            # 发送验证码失败
            return_data["Success"] = False
            return_data["Error"] = "Send validation code error!"

    else:
        # 有InputCode，鉴定验证码对不对
        UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
        if UserInfo:
            # 此账户存在
            ValidCode = UserInfo['ValidCode']
            if InputCode == ValidCode:
                # 验证码正确
                return_data["Success"] = True
            else:
                # 验证码错误
                return_data["Success"] = False
                return_data["Error"] = "Wrong code!"
        else:
            # 账户未创建,却提供验证码：非法入侵
            return_data["Success"] = False
            return_data["Error"] = "Illegal access: Please stop doing again!"

    return return_data


@app.route('/set-reset-password', methods=['POST'])
# http://localhost:5000/set-reset-password
def SetResetPassword():
    return_data = {}

    EmailAddress = request.form.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Password = request.form.get("Password")
    NewPassword = request.form.get("NewPassword")
    Success, Error = check_password(EmailAddress,Password)
    if not Success:
        if Error == "This account has no password!":
            # 账户未设置密码，则设置密码
            if NewPassword:
                # 账户未设置密码，但同时提供新旧密码
                return_data["Success"] = False
                return_data["Error"] = "You should not provide new password!"
                return return_data
            # 设置密码
            db.UserInfos.update_one({'EmailAddress': EmailAddress}, {"$set": {'Password': Password}})
            return_data["Success"] = True
            return return_data
        else:
            # 密码检查不通过
            if Password is None and NewPassword:
                # 未提供旧密码，但提供新密码（忘记密码）
                UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
                NewCodeTime = datetime.strptime(get_time_attribute('code')["CodeTime"], '%Y-%m-%d %H:%M:%S')
                LastCodeTime = datetime.strptime(UserInfo["CodeTime"], '%Y-%m-%d %H:%M:%S')
                if (NewCodeTime - LastCodeTime).seconds <= 120:
                    # 若120s内有发送验证邮件,则同意设置新密码
                    db.UserInfos.update_one({'EmailAddress': EmailAddress}, {"$set": {'Password': NewPassword}}) # 设置新密码
                    return_data["Success"] = True
                    return return_data
                else:
                    # 若120s内没有发送验证邮件
                    return_data["Success"] = False
                    return_data["Error"] = "You should do email validation first!"
                    return return_data
            else:
                # 旧密码错误
                return_data["Success"] = Success
                return_data["Error"] = Error
                return return_data
    else:
        # 旧密码检查通过
        if not NewPassword:
            # 没有提供新密码
            return_data["Success"] = False
            return_data["Error"] = "Did not provide new password."
            return return_data
        db.UserInfos.update_one({'EmailAddress': EmailAddress}, {"$set": {'Password': NewPassword}})   # 设置新密码
        return_data["Success"] = True
        return return_data

    return return_data


@app.route('/create-account', methods=['POST'])
# http://localhost:5000/create-account
def CreateAccount():
    return_data = {}
    NewUserInfo = {}

    EmailAddress = request.json.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Password = request.json.get('Password')
    if not Password:
        # 没有提供密码
        return_data["Success"] = False
        return_data["Error"] = "Did not provide password."
        return return_data

    StudentID = request.json.get("StudentID")
    if StudentID:
        NewUserInfo['StudentID'] = StudentID
    FirstName = request.json.get("FirstName")
    if FirstName:
        NewUserInfo['FirstName'] = FirstName
    LastName = request.json.get("LastName")
    if LastName:
        NewUserInfo['LastName'] = LastName
    NickName = request.json.get("NickName")
    if NickName:
        NewUserInfo['NickName'] = NickName
    Birthday = request.json.get("Birthday")
    if Birthday:
        NewUserInfo['Birthday'] = Birthday
    Gender = request.json.get("Gender")
    if Gender:
        NewUserInfo['Gender'] = Gender
    Profile = request.json.get("Profile")
    if Profile:
        NewUserInfo['Profile'] = Profile
    Region = request.json.get("Region")
    if Region:
        NewUserInfo['Region'] = Region
    School = request.json.get("School")
    if School:
        NewUserInfo['School'] = School
    PhoneNumber = request.json.get("PhoneNumber")
    if PhoneNumber:
        NewUserInfo['PhoneNumber'] = PhoneNumber
    HeadPortrait = request.json.get("HeadPortrait")
    if HeadPortrait:
        NewUserInfo['HeadPortrait'] = HeadPortrait
    FavoriteFields = request.json.get("FavoriteFields")
    if FavoriteFields:
        NewUserInfo['FavoriteFields'] = FavoriteFields

    UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
    if not UserInfo.get('Password'):
       # 账户没有设置密码
        return_data["Success"] = False
        return_data["Error"] = "Account did not set password!"
        return return_data
    elif Password != UserInfo['Password']:
        # 密码不正确，不能修改，可能是
        return_data["Success"] = False
        return_data["Error"] = "Wrong password!"
        return return_data
    # 密码正确，可以更新账户信息
    db.UserInfos.update_one({'EmailAddress': EmailAddress}, {"$set": NewUserInfo})
    return_data["Success"] = True
    return return_data


@app.route('/login', methods=['POST'])
# http://localhost:5000/login
def Login():
    return_data = {}

    EmailAddress = request.form.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Password = request.form.get('Password')
    Success,Error = check_password(EmailAddress,Password)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    else:
        return_data["Success"] = Success
        return return_data
    return return_data


@app.route('/get-user-info', methods=['GET'])
# http://localhost:5000/get-user-info
def GetUserInfo():
    return_data = {}

    EmailAddress = request.args.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
    return_data["Success"] = True
    return_data['EmailAddress'] = UserInfo.get('EmailAddress')
    return_data['FirstName'] = UserInfo.get('FirstName')
    return_data['LastName'] = UserInfo.get('LastName')
    return_data['NickName'] = UserInfo.get('NickName')
    return_data['StudentID'] = UserInfo.get('StudentID')
    return_data['Birthday'] = UserInfo.get('Birthday')
    return_data['Gender'] = UserInfo.get('Gender')
    return_data['Profile'] = UserInfo.get('Profile')
    return_data['Region'] = UserInfo.get('Region')
    return_data['School'] = UserInfo.get('School')
    return_data['PhoneNumber'] = UserInfo.get('PhoneNumber')
    return_data['HeadPortrait'] = UserInfo.get('HeadPortrait')
    return_data['FavoriteFields'] = UserInfo.get('FavoriteFields')
    return return_data


@app.route('/send-message', methods=['POST'])
# http://localhost:5000/send-message
def SendMessage():
    return_data = {}

    Sender = request.json.get('Sender')
    Success, Error = check_email(Sender)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Receiver = request.json.get('Receiver')
    Success, Error = check_email(Receiver)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Content = request.json.get('Content')
    if not Content or (not Content.get('Text') and not Content.get('Image')):
        # 空消息
        return_data["Success"] = False
        return_data["Error"] = "Empty content!"
        return return_data
    else:
        # 不是空消息，为消息添加时间
        TimeAttribute = get_time_attribute('only create')
        Content.update(TimeAttribute)

    NewMessage = {}
    Message = db.Messages.find_one({'Sender': Sender, 'Receiver': Receiver})
    if Message:
        # 此聊天存在, 向后添加message并更新时间
        NewMessage['Contents'] = Message['Contents']
        NewMessage['Contents'].append(Content)
        TimeAttribute = get_time_attribute('update')
        NewMessage.update(TimeAttribute)  # 设置修改时间
        db.Messages.update_one({'Sender': Sender, 'Receiver': Receiver}, {"$set": NewMessage})
    else:
        # 此聊天不存在，创建新的Message实例
        NewMessage['Contents'] = []
        NewMessage['Contents'].append(Content)
        NewMessage['Sender'] = Sender
        NewMessage['Receiver'] = Receiver
        TimeAttribute = get_time_attribute('create withour code')
        NewMessage.update(TimeAttribute)  # 设置创建和修改时间
        db.Messages.insert_one(NewMessage)  # 向数据库插入此新聊天
         
    # 查看是否有回复，没有则设置自动回复
    NewMessage_2 = {}
    Message_reverse = db.Messages.find_one({'Sender': Receiver, 'Receiver': Sender })
    if not Message_reverse:
        # 此聊天不存在,添加自动回复
        newContent = {'Text': "Auto reply: please wait for response.",'Image': None}
        TimeAttribute = get_time_attribute('only create')
        newContent.update(TimeAttribute)
        NewMessage_2['Contents'] = []
        NewMessage_2['Contents'].append(newContent)
        NewMessage_2['Sender'] = Receiver
        NewMessage_2['Receiver'] = Sender
        TimeAttribute = get_time_attribute('create withour code')
        NewMessage_2.update(TimeAttribute)  # 设置创建和修改时间
        db.Messages.insert_one(NewMessage_2)  # 向数据库插入此新聊天
    
    return_data["Success"] = True
    return return_data


@app.route('/get-message', methods=['POST'])
# http://localhost:5000/get-message
def GetMessages():
    return_data = {}

    EmailAddress = request.form.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Password = request.form.get('Password')
    Success,Error = check_password(EmailAddress,Password)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Data = []
    # 邮箱及密码验证成功
    Sender = request.form.get('Sender')
    if Sender:
        # 获取来自指定用户的消息
        Messages = db.Messages.find({'Receiver': EmailAddress, "Sender": Sender})
    else:
        # 获取来自所有用户的消息
        Messages = db.Messages.find({'Receiver': EmailAddress})
        
    msgLen = 0
    for Message in Messages:
        msgLen += 1
        UserInfo_sender = db.UserInfos.find_one({'EmailAddress': Message['Sender']})
        NickName_sender = None
        HeadPortrait_sender = None
        if UserInfo_sender:
            # 发送者存在账户
            NickName_sender = UserInfo_sender.get('NickName')
            HeadPortrait_sender = UserInfo_sender.get("HeadPortrait")
        NewData = {"Sender": Message['Sender'], 'NickName': NickName_sender, "HeadPortrait": HeadPortrait_sender}
        Reply = db.Messages.find_one({'Sender': EmailAddress, "Receiver": Message['Sender']})
        # 分别标记
        for content1 in Message['Contents']:
            content1.update({"Direction": False})
        if Reply:
            for content2 in Reply['Contents']:
                content2.update({"Direction": True})
            Contents = Message['Contents'] + Reply['Contents']
        else:
            Contents = Message['Contents']
        # print("before:", Contents)
        # Contents = sorted(Contents, key = lambda date:get_list(date))
        Contents.sort(key = lambda x:x["CreateTime"])
        # Contents.sort(key = lambda x:x["CreateTime"], reverse=True)
        # print("after:", Contents)
        NewData.update({"Contents": Contents})
        Data.append(NewData)
    
    if msgLen == 0 and Sender:
            # 获取来自指定用户的消息，但之前没有过消息
            UserInfo_sender = db.UserInfos.find_one({'EmailAddress': Sender})
            if UserInfo_sender:
                # 发送者存在账户
                NickName_sender = UserInfo_sender.get('NickName')
                HeadPortrait_sender = UserInfo_sender.get("HeadPortrait")
            NewData = {"Sender": Sender, 'NickName': NickName_sender, "HeadPortrait": HeadPortrait_sender}
            Reply = db.Messages.find_one({'Sender': EmailAddress, "Receiver": Sender})
            if Reply:
                for content in Reply['Contents']:
                    content.update({"Direction": True})
                NewData.update({"Contents": Reply['Contents']})
            Data.append(NewData)
    
    return_data["Data"] = Data
    return_data["Success"] = True
    return return_data


@app.route('/new-post', methods=['POST'])
# http://localhost:5000/new-post
def NewPost():
    return_data = {}
    NewPost = {}

    PostOwner = request.json.get("PostOwner")
    Success, Error = check_email(PostOwner)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Title = request.json.get("Title")
    if Title:
        NewPost['Title'] = Title
    Text = request.json.get("Text")
    if Text:
        NewPost['Text'] = Text
    Images = request.json.get("Images")
    if Images:
        NewPost['Images'] = Images
    Price = request.json.get("Price")
    if Price:
        NewPost['Price'] = int(Price)
    Fields = request.json.get("Fields")
    if Fields:
        NewPost['Fields'] = Fields
    NewPost['Auction'] = request.json.get("Auction")
    NewPost['LostFound'] = request.json.get("LostFound")
    
    NewPost['PostOwner'] = PostOwner
    NewPost['Deleted'] = False
    TimeAttribute = get_time_attribute('create withour code')
    NewPost.update(TimeAttribute)   # 添加创建和更新时间

    _id = db.Posts.insert_one(NewPost).inserted_id # 添加新的post

    return_data["Success"] = True
    # return_data["PID"] = str(_id)

    return return_data


@app.route('/delete-post', methods=['POST'])
# http://localhost:5000/delete-post
def DeletePost():
    return_data = {}

    EmailAddress = request.form.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Password = request.form.get('Password')
    Success,Error = check_password(EmailAddress,Password)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    PID = request.form.get('PID')
    Success,Error = check_post(PID)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    # 检查是否是本人删帖
    Post = db.Posts.find_one({'_id': ObjectId(PID)})
    if EmailAddress == Post['PostOwner']:
        # 为本人删帖：将帖子的Deleted属性改为True
        db.Posts.update_one({'_id': ObjectId(PID)}, {"$set": {'Deleted':True}})
        # 更新更新时间
        TimeAttribute = get_time_attribute('update')
        db.Posts.update_one({'_id': ObjectId(PID)}, {"$set": TimeAttribute})
        return_data["Success"] = True
    else:
        # 不是本人删帖
        return_data["Success"] = False
        return_data["Error"] = 'You are not the owner of this post!'
        return return_data
   
    return return_data


@app.route('/user-posts', methods=['GET'])
# http://localhost:5000/user-posts?EmailAddress=1030920919@qq.com
def UserPosts():
    return_data = {}
    Posts = []
    
    EmailAddress = request.args.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    # 查照所有该用户没有被删除的帖子
    user_Posts = db.Posts.find({"PostOwner":EmailAddress, 'Deleted': {'$ne': True}}).limit(6)
    if user_Posts:
        for user_Post in user_Posts:
            NewPost = \
            {
                "PID": str(user_Post['_id']), \
                "PostOwner": user_Post.get("PostOwner"),\
                "CreateTime": user_Post.get('CreateTime'),\
                "Title": user_Post.get("Title"), \
                "Text": user_Post.get("Text"), \
                "Price": user_Post.get("Price"), \
                "Auction": user_Post.get("Auction"),\
                "LostFound": user_Post.get("LostFound"),\
                "Images": user_Post.get("Images"),\
                "Comments": user_Post.get('Comments')\
            }
            Posts.append(NewPost)
    
    return_data['Posts'] = Posts
    return_data["Success"] = True
    
    return return_data


@app.route('/post-comment', methods=['POST'])
# http://localhost:5000/post-comment
def PostComment():
    return_data = {}
    NewComment = {}

    Commenter = request.form.get("Commenter")
    Success, Error = check_email(Commenter)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    PID = request.form.get('PID')
    Success,Error = check_post(PID)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Text = request.form.get('Text')
    if not Text:
        # 没有评论
        return_data["Success"] = False
        return_data["Error"] = "No text provided!"
        return return_data
    else:
        # 有评论
        NewComment['Commenter'] = Commenter
        NewComment['Text'] = Text
        TimeAttribute = get_time_attribute('only create')
        NewComment.update(TimeAttribute)
        UserInfo = db.UserInfos.find_one({'EmailAddress': Commenter})
        # NewComment['NickName'] = UserInfo['NickName']
        NewComment['NickName'] = UserInfo.get('NickName', None)
        # NewComment['HeadPortrait'] = UserInfo['HeadPortrait']
        NewComment['HeadPortrait'] = UserInfo.get('HeadPortrait', None)
        
        Post = db.Posts.find_one({'_id': ObjectId(PID)})
        Comments = Post.get('Comments')
        if Comments:
            # 该帖子已有评论,在后面添加
            Comments.append(NewComment)
        else:
            # 该帖子暂无评论，添加评论
            Comments = []
            Comments.append(NewComment)
        db.Posts.update_one({'_id': ObjectId(PID)}, {"$set": {'Comments': Comments}})
        return_data["Success"] = True
        return return_data

    return return_data


@app.route('/get-posts', methods=['GET'])
# http://localhost:5000/get-posts
def GetPosts():
    '''
    # 文本索引结构:
    {
        "weights" : {
            "Title" : 3,
            "Text" : 2,
            "Fields" : 1
        },
        "name" : "TextIndex"
    }

    # db.Posts.create_index( [("Title":"text", pymongo.ASCENDING),("Text":"text", pymongo.ASCENDING)]) # 索引
    # db.Posts.create_index( { "Title": "text", "Text":"text"} ) # 索引
    
    indexs = db.Posts.list_indexes()
    for index in indexs:
        print(index)

    # mongodb 全文索引的特点：
        # 它主要匹配的是有意义的单词，忽略大小写，忽略单复数，忽略时态等。关于全文索引也有文档说明，请仔细阅读，它是跟普通索引完全不一样的一种索引形式。
        # 另外全文索引虽然一个表只能有一个，但是却可以为不同的字段设置不同的权重，最终计算出一个匹配度的得分。
    '''
    
    return_data = {}
    Posts=[]

    # 检查邮箱
    EmailAddress = request.args.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    # 检查数量
    Num = request.args.get("Num")
    if Num: # not null
        Num = int(Num)
        if Num <= 0 and Num > 10:
            return_data["Success"] = False
            return_data["Error"] = "Parameter Num is not in valid range."
            return return_data
    else:
        Num = 6 # default value
    
    Keyword = request.args.get('Keyword')
    if Keyword:
        # 用户提供了关键词：
        scored_Posts = db.Posts.find({"$text":{"$search": Keyword}, "Deleted": {"$ne": True}}, {"Score":{"$meta": "textScore"}}).limit(Num) # 返回最多十条未被删除的posts
    else:
        # 用户未提供关键词：
        UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
        FavoriteFields = UserInfo.get('FavoriteFields')
        if FavoriteFields:
            Fields = "" # 将用户所有的喜欢领域作为关键词检索
            for Field in FavoriteFields:
                Fields += ' ' + Field
            scored_Posts = db.Posts.find({"$text":{"$search": Fields}, "Deleted": {"$ne": True}},{"Score":{"$meta": "textScore"}}).limit(Num) # 返回最多十条未被删除的posts
            scored_Posts = sorted(scored_Posts, key=itemgetter('Score'), reverse=True) # 降序排序
        else:
            # 用户没有设置喜欢的领域,随机返回帖子
            count = db.Posts.count_documents({'Deleted': {'$ne': True}})
            if count > Num:
                scored_Posts = db.Posts.aggregate([ {'$match': {'Deleted': {'$ne': True}}}, {'$sample': {'size': Num}} ])
            else:
                scored_Posts = db.Posts.aggregate([ {'$match': {'Deleted': {'$ne': True}}}, {'$sample': {'size': count}} ])
    
    if scored_Posts:
        for scored_Post in scored_Posts:
            NewPost = \
            {
                "PID": str(scored_Post['_id']), \
                "PostOwner": scored_Post.get("PostOwner"),\
                "CreateTime": scored_Post.get('CreateTime'),\
                "Title": scored_Post.get("Title"), \
                "Text": scored_Post.get("Text"), \
                "Price": scored_Post.get("Price"),\
                "Auction": scored_Post.get("Auction"),\
                "LostFound": scored_Post.get("LostFound"),\
                "Images": scored_Post.get("Images"),\
                "Comments": scored_Post.get('Comments'),\
                "Score": scored_Post.get('Score')\
            }
            Posts.append(NewPost)

    return_data['Posts'] = Posts
    return_data["Success"] = True

    return return_data


@app.route('/click-post', methods=['GET'])
# http://localhost:8080/click-post?EmailAddress=1030920919@qq.com&PID=65a199aaa2c14c072766377a
def ClickPost():
    return_data = {}

    # 检查邮箱
    EmailAddress = request.args.get("EmailAddress")
    Success,Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    # 检查帖子
    PID = request.args.get('PID') # type: str
    Success,Error = check_post(PID)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    Post = db.Posts.find_one({'_id': ObjectId(PID)})
    Count = Post.get('Count')
    if Count:
        # 之前有计数
        Count = int(Count)
        Count += 1
    else:
        Count = 1
    db.Posts.update_one({'_id': ObjectId(PID)}, {"$set": {'Count':str(Count)}})
    
    UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
    if not UserInfo:
        # 此账户不存在
        Success = False
        Error = "Did not find account. Please try it again!"
        return Success, Error
    
    PostHistory = UserInfo.get('PostHistory')
    if PostHistory:
        # 该用户已有浏览记录
        if PostHistory[-1] != PID:
            PostHistory.append(PID)
    else:
        # 该用户没有浏览记录
        PostHistory = []
        PostHistory.append(PID)
    db.UserInfos.update_one({'EmailAddress': EmailAddress}, {"$set": {'PostHistory': PostHistory}})
    
    return_data["Success"] = True
    return return_data
    

@app.route('/get-post-history', methods=['GET'])
# http://localhost:8080/get-view-history?EmailAddress=1030920919@qq.com
def GetPostHistory():
    return_data = {}
    Posts=[]
    
    # 检查邮箱
    EmailAddress = request.args.get("EmailAddress")
    Success,Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    
    UserInfo = db.UserInfos.find_one({'EmailAddress': EmailAddress})
    if not UserInfo:
        # 此账户不存在
        Success = False
        Error = "Did not find account. Please try it again!"
        return Success, Error
    
    PostHistory_new = []
    hasInvalidPID = False
    PostHistory = UserInfo.get('PostHistory')
    if PostHistory:
        # 该用户已有浏览记录
        for PID in PostHistory:
            Post = db.Posts.find_one({'_id': ObjectId(PID), "Deleted": {"$ne": True}})
            if Post:
                NewPost = \
                {
                    "PID": str(Post['_id']), \
                    "PostOwner": Post.get("PostOwner"),\
                    "CreateTime": Post.get('CreateTime'),\
                    "Title": Post.get("Title"), \
                    "Text": Post.get("Text"), \
                    "Price": Post.get("Price"),\
                    "Auction": Post.get("Auction"),\
                    "LostFound": Post.get("LostFound"),\
                    "Images": Post.get("Images"),\
                    "Comments": Post.get('Comments'),\
                    "Score": Post.get('Score')\
                }
                Posts.append(NewPost)
                PostHistory_new.append(PID)
            else: 
                # not found PID in db.
                hasInvalidPID = True
        if hasInvalidPID:
            db.Posts.update_one({'_id': ObjectId(PID)}, {"$set": {'PostHistory':PostHistory_new}})
            
    return_data['Posts'] = Posts
    return_data["Success"] = True

    return return_data
@app.route('/edit-post', methods=['POST'])
def EditPost():
    return_data = {}
    EmailAddress = request.form.get("EmailAddress")
    Success, Error = check_email(EmailAddress)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    Password = request.form.get('Password')
    Success,Error = check_password(EmailAddress,Password)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data

    PID = request.form.get('PID')
    Success,Error = check_post(PID)
    if not Success:
        return_data["Success"] = Success
        return_data["Error"] = Error
        return return_data
    new_content = request.form.get('NewContent')
    PostOwner = request.json.get("PostOwner")
    Post = db.Posts.find_one({'_id': ObjectId(PID)})
    if Post:
        current_post=\
        {
            "PID": str(Post[_id]),\
            "PostOwner": Post.get("PostOwner"),\
            "CreateTime": Post.get('CreateTime'),\
            "Title": Post.get("Title"),\
            "Text": Post.get("Text"),\
            "Price": Post.get("Price"),\
            "Auction": Post.get("Auction"),\
            "LostFound": Post.get("LostFound"),\
            "Images": Post.get("Images"),\
            "Comments": Post.get('Comments'),\
            "Score": Post.get('Score')\
        }
        Title = request.json.get("Title")
        if Title:
            NewPost['Title'] = Title
        Text = request.json.get("Text")
        if Text:
            NewPost['Text'] = Text
        Images = request.json.get("Images")
        if Images:
            NewPost['Images'] = Images
        Price = request.json.get("Price")
        if Price:
            NewPost['Price'] = int(Price)
        Fields = request.json.get("Fields")
        if Fields:
            NewPost['Fields'] = Fields
        NewPost['Auction'] = request.json.get("Auction")
        NewPost['LostFound'] = request.json.get("LostFound")
        NewPost['PostOwner'] = PostOwner
        NewPost['Deleted'] = False
        TimeAttribute = get_time_attribute('create withour code')
        NewPost.update(TimeAttribute) 
        db.Posts.update_one({'_id': ObjectId(PID)}, {"$set": NewPost})
        return_data["Success"] = True
        return return_data


        





if __name__ == '__main__':
    # db.Posts.drop_index("Title_Text")
    app.run(host='localhost', port=8080, debug=True)
    
