from locust import *
from gevent._semaphore import Semaphore
import queue

# all_locusts_spawned = Semaphore()
# all_locusts_spawned.acquire()


# @events.spawning_complete.add_listener
# def on_hatch_complete(**kwargs):
#     all_locusts_spawned.release()


#  创建工作类
class Demo(TaskSet):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"
    }

    def on_start(self):
        print('用户加载')
        # all_locusts_spawned.wait()

    def on_stop(self):
        print('用户退出')

    @tag('user')
    @task(1)
    def users_api(self):
        # 请求接口
        with self.client.get(url='v1/auth/users', headers=self.headers, params={
            'pageNo': 1,
            'pageSize': 9,
            'accessToken': "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY4NDA4NjE2Nn0.qTYJkS4srF56O1EeNOJ5kml72lJtUV-b2HNfUWKdQZg"
        }, catch_response=True) as res:
            # 断言
            if res.status_code != 200:
                res.failure('状态码错误')
            res = res.json()
            if res['pageItems'][0]['username'] != "nacos":
                res.failure('字段值不匹配')

    @tag('add_user')
    @task(1)
    def aaa(self):
        data = MyUser.queue_data.get()
        with self.client.post('v1/auth/users', headers=self.headers, params={
            "accessToken": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTY4NDA4NjE2Nn0.qTYJkS4srF56O1EeNOJ5kml72lJtUV-b2HNfUWKdQZg"
        }, data=data) as res:
            if res.status_code != 200:
                res.failure('状态码错误')
            res = res.json()
            if res['data'] != "create user ok!":
                res.failure('字段值不匹配')
        # 去数据库删除添加好的数据
        MyUser.queue_data.put_nowait(data)


# 管理和运行
class MyUser(FastHttpUser):
    wait_time = constant(0)
    tasks = [Demo]
    host = 'http://istress.itesti.cn/'
    queue_data = queue.Queue()
    user_list = [['ppp', '123'], ['aaa', '456'], ['ddd', '789']]
    for info in user_list:
        play_load = {
            'username': info[0],
            'password': info[1]
        }
        queue_data.put_nowait(play_load)


if __name__ == '__main__':
    import os
    os.system('locust -f demo.py --web-host=127.0.0.1 --tags user')