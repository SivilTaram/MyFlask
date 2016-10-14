# -*- coding: utf-8 -*-
"""
Created on Sun Oct 09 13:02:05 2016

@author: SivilTaram
"""

import requests

class MoocMember:
    
    client = None

    def __init__(self,_email,_pass):
        self.client = requests.Session()
        # get cookies
        res = self.client.get("http://mooc.buaa.edu.cn/login")
        login_info = {'email':_email,'password':_pass}
        csrf_token = res.cookies['csrftoken']
        cookies = 'csrftoken=%s;sessionid=%s' %(csrf_token,res.cookies['sessionid'])
        
        # login_header
        login_header = {'Referer':'http://mooc.buaa.edu.cn/login',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
                        'Cookie':cookies,
                        'X-CSRFToken':csrf_token,
                        'X-Requested-With':'XMLHttpRequest'}
                  
        # reponse for login
        login_res = self.client.post('http://mooc.buaa.edu.cn/login_ajax',
                                data=login_info,
                                headers=login_header)
        if login_res.status_code == requests.codes.ok:
            print login_res.text
    
    def CreateDiscuss(self,title,body):
        
        forum_body = body
        forum_title = title
        
        forum_csrf_token = self.client.cookies['csrftoken']
        forum_cookies = 'csrftoken=%s;sessionid=%s;' %(forum_csrf_token,self.client.cookies['sessionid'])
        
        forum_header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
                        'Cookie':forum_cookies,
                        'Host':'mooc.buaa.edu.cn',
                        'X-CSRFToken':forum_csrf_token,
                        'X-Requested-With':'XMLHttpRequest'}
        
        forum_info = {'anonymous':'false',
                      'anonymous_to_peers':'false',
                      'auto_subscribe':'true',
                      'body':forum_body,
                      'group_id':'',
                      'thread_type':'discussion',
                      'title':forum_title}
        
        #create post response
        create_res = self.client.post('http://mooc.buaa.edu.cn/courses/BUAA/M_E06B2150/2015_T1/discussion/i4x-BUAA-M_E06B2150-course-2015_T9/threads/create?ajax=1',
                                 data = forum_info,
                                 headers = forum_header)
        
        if create_res.status_code == requests.codes.ok:
            print 'success!'
        else:
            print 'fail!'
