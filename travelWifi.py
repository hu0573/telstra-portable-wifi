#!/usr/bin/env python
# coding: utf-8

# In[37]:


import base64
import requests
import xml.etree.ElementTree as ET
import time


# In[38]:


class travelWifi:
    def __init__(self,ipAddress="192.168.1.1",username="admin",password="admin"):
        self.ipAddress = "http://" + ipAddress if "http://" not in ipAddress else ipAddress
        self.username = username
        self.password = password
        
    def login_to_router(self):
        # Base64 encode the password
        encoded_password = base64.b64encode(self.password.encode()).decode()

        # Create the login request XML data
        login_data = f"""
        <request>
            <Username>{self.username}</Username>
            <Password>{encoded_password}</Password>
        </request>
        """

        headers = {'Content-Type': 'application/xml'}
        login_url = f'{self.ipAddress}/api/user/login'
        response = requests.post(login_url, data=login_data, headers=headers)

        # Check the login response
        root = ET.fromstring(response.text)
        if root.tag == 'error':
            return False, root.find('code').text
        return True, None

    def reboot_router(self):
        self.login_to_router()
        # 构建重启请求的XML数据
        reboot_data = """
        <request>
            <Control>1</Control>
        </request>
        """
        # 添加请求头以指定XML数据格式
        headers = {'Content-Type': 'application/xml'}
        reboot_url = f'{self.ipAddress}/api/device/control'
        response = requests.post(reboot_url, data=reboot_data, headers=headers)

        # 检查响应
        if response.status_code == 200:
            print('重启成功')
        else:
            print(f'重启失败: {response.status_code}')
        print(response.text)
        
    def receive_sms(self,headers={'Content-Type': 'application/xml'}):
        """
        Retrieve the list of SMS messages from the router.
        """
        self.login_to_router()
        # Construct the XML request data
        sms_list_data = """
        <request>
            <PageIndex>1</PageIndex>
            <ReadCount>20</ReadCount>
            <BoxType>1</BoxType>
            <SortType>0</SortType>
            <Ascending>0</Ascending>
            <UnreadPreferred>0</UnreadPreferred>
        </request>
        """
        # Make the API call to get the list of SMS messages
        get_sms_url = f'{self.ipAddress}/api/sms/sms-list'
        response = requests.post(get_sms_url, data=sms_list_data, headers=headers)

        # Parse the response XML to extract SMS details
        root = ET.fromstring(response.text)
        messages = []
        for message in root.find('Messages').findall('Message'):
            msg_details = {
                'Status': message.find('Smstat').text,
                'Index': message.find('Index').text,
                'Phone': message.find('Phone').text,
                'Content': message.find('Content').text,
                'Date': message.find('Date').text,
                'Type': message.find('SmsType').text
            }
            messages.append(msg_details)
        return messages
        
    def send_sms(self,phone_number, message_content, headers={'Content-Type': 'application/xml'}):
        """
        Send an SMS using the provided phone number and message content.
        """
        self.login_to_router()
        # Construct the XML request data
        sms_data = f"""
        <request>
            <Index>-1</Index>
            <Phones>
                <Phone>{phone_number}</Phone>
            </Phones>
            <Sca></Sca>
            <Content>{message_content}</Content>
            <Length>{len(message_content)}</Length>
            <Reserved>1</Reserved>
            <Date>{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}</Date>
        </request>
        """

        # Send the SMS
        send_sms_url = f'{self.ipAddress}/api/sms/send-sms'
        response = requests.post(send_sms_url, data=sms_data, headers=headers)

        # Return the response for further analysis
        return response.text
