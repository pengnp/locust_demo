### 安装

pip  install  locust

如果运行过程中有报错**ValueError: greenlet.greenlet size changed, may indicate binary incompatibility. Expected 144 from C**，则 pip install greenlet==1.1.3 gevent==22.8.0

### 完整的locust案例

```python
# -*- coding: utf-8 -*-
from locust import *
from locust.runners import *
from gevent._semaphore import Semaphore
import time
import gevent

all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()


@events.spawning_complete.add_listener
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()


@events.test_stop.add_listener
def on_test_stop(environment):
    print('测试结束')


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print('测试开始')


def checker(environment):
    while environment.runner.state not in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        time.sleep(1)
        if environment.runner.stats.total.fail_ratio > environment.parsed_options.Error_rate:
            print(f"fail ratio was {environment.runner.stats.total.fail_ratio}, quitting")
            environment.runner.quit()


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
        gevent.spawn(checker, environment)


@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response,
                       context, exception, start_time, url, **kwargs):
    if exception:
        print(f"Request to {name} failed with exception {exception}")


@events.init_command_line_parser.add_listener
def extend_ui(parser):
    parser.add_argument("--Error-rate", type=float, default=0.05, help="失败率，并在测试超过设置阈值时停止运行")


@tag('User')
class UserTask(TaskSet):
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48",
        "cookie": "Hm_lvt_cb81fd54150b99e25d085d58bbaf4a07=1680855828,1681375073,1681698049,1682593292; gr_user_id=24fba58b-09b9-4d25-9877-013ea1384aa4; 9bc6807c25b59135_gr_last_sent_cs1=356418; 9bc6807c25b59135_gr_cs1=356418; jupyter-hub-token=; jupyterhub-session-id=7f98241807f340d1bcc9b3e763a7efbe; jupyterhub-hub-login='2|1:0|10:1683184287|20:jupyterhub-hub-login|44:Mjg2NWY0Mzg0NTgwNDM4ZjlmYTNmMzBiY2JiMTkwNGE=|e17276174bea02630c36cb78a78e3d90f3a010de5931959d879a11e2855f1743'; _xsrf=2|246d736d|307bf586ddeeb3c899c1c65415c79e62|1683184287; rqjwt=eyJhbGciOiAiSFM1MTIiLCAiaWF0IjogMTY4MzI1MDMyNiwgImV4cCI6IDE2ODU4NDIzMjZ9.eyJpZCI6IDM1NjQxOCwgInVzZXJuYW1lIjogIlx1NGUwYVx1NWYyNlx1NjcwOCIsICJlbWFpbCI6ICIzNTcwNzE2ODBAcXEuY29tIiwgImZ1bGxuYW1lIjogIlx1NGUwYVx1NWYyNlx1NjcwOCIsICJwaWN0dXJlIjogImh0dHBzOi8vcWNkbi5yaWNlcXVhbnQuY29tL2ltZy9hdmF0YXIvZGI5ZjE1MzgtMTk5Yi00OWU4LTk3ZmItYmQ4MjU4MDJhZjE2LnBuZyJ9.6OV3cRR39n_0Av-kTeH5oZte_shj7IPuOJV-I5DHEDwUDezW-CezGLK_1orIqrX3KHu1ueGMZmqe1HB4nrM_IA; sid=Re2SGA4rzPBzw3GqB3YM0AK708zn3Ku8|ce802108259ae985ce3706df898fb5f0e0c6b21e49992ea9a197062a17fef0afe31de1d748ca77c4dec1a1b4ca60cdd09550e4e1c9868dfb256b00d61c851158; Hm_lpvt_cb81fd54150b99e25d085d58bbaf4a07=1683250342; tgw_l7_route=006b76bf4a6398f05baf657858ca2891"
    }

    def on_start(self):
        print('加载中')
        all_locusts_spawned.wait()

    def on_stop(self):
        print('退出中')

    # @tag('cpt')
    @task(1)
    def user_1(self):
        print('User_1')
        time.sleep(3)

    @task(2)
    def user_2(self):
        print('User_2')
        time.sleep(3)


@tag('Animal')
class AnimalTask(TaskSet):

    def on_start(self):
        print('加载中')
        all_locusts_spawned.wait()

    def on_stop(self):
        print('退出中')

    # @tag('sbt')
    @task(1)
    def animal_1(self):
        print('Animal_1')
        time.sleep(3)

    @task(2)
    def animal_2(self):
        print('Animal_2')
        time.sleep(3)


class MyUser(FastHttpUser):
    tasks = {UserTask: 1, AnimalTask: 1}
    wait_time = between(0, 0)
    # wait_time = constant(10)
    host = "https://www.baidu.com/"


if __name__ == '__main__':
    import os
    os.system("locust -f demo.py --web-host=127.0.0.1 --tags Animal User")

```



### locust文件属性介绍

##### 用户类（User）

- **wait_time**

​			wait_time = between(0.5, 10) 	每个用户在每次任务执行之间等待 0.5 到 10 秒

​			wait_time = constant(10)	每个用户固定等待10s

- ##### host


​	host = "https://www.baidu.com/"	host 属性是要加载的主机的 URL 前缀

- **on_start**

```python
def on_start(self):
	print(test start)
```

每个用户运行前会执行此方法

- **on_stop**

```python
def on_stop(self):
	print(test stop)
```

每个用户停止后会执行此方法

##### 任务（Task）

- **task**

为用户添加任务

```python
class MyUser(User):
    wait_time = constant(1)

    @task
    def my_task(self):
        print("User instance (%r) executing my_task" % self)
```

**@task**采用可用于指定任务执行比率的可选权重参数。在 以下示例中，*选择任务 2* 的可能性是*任务 1* 的两倍：

```python
class MyUser(User):
    wait_time = between(5, 15)

    @task(3)
    def task1(self):
        pass

    @task(6)
    def task2(self):
        pass
```

##### **标签（tag）**

```
class MyUser(User):
    wait_time = between(5, 15)
	
	@tag('task1')
    @task(3)
    def task1(self):
        pass

    @task(6)
    def task2(self):
        pass
if __name__ == '__main__':
    import os
    os.system("locust -f demo.py --web-host=127.0.0.1 --tags task1")
```



##### 事件

- **test_start和test_stop**	测试开始时触发和测试结束时触发

  ```Python
  @events.test_start.add_listener
  def on_test_start(environment, **kwargs):
      if not isinstance(environment.runner, MasterRunner):
          print("Beginning test setup")
      else:
          print("Started test from Master node")
  
  @events.test_stop.add_listener
  def on_test_stop(environment, **kwargs):
      if not isinstance(environment.runner, MasterRunner):
          print("Cleaning up test data")
      else:
          print("Stopped test from Master node"
  ```

- **init**    初始化时触发

```Python
def checker(environment):
    while environment.runner.state not in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
        time.sleep(1)
        if environment.runner.stats.total.fail_ratio > environment.parsed_options.Error_rate:
            print(f"fail ratio was {environment.runner.stats.total.fail_ratio}, quitting")
            environment.runner.quit()


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
        gevent.spawn(checker, environment)
```

- **spawning_complete**	虚拟用户孵化完成时触发（集合点，感觉在分布式又或者设置了run_time的时候会失效）

```python
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()


@events.spawning_complete.add_listener
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
```

- **init_command_line_parser**   自定义UI

  ```python
  @events.init_command_line_parser.add_listener
  def _(parser):
      parser.add_argument("--my-argument", type=str, env_var="LOCUST_MY_ARGUMENT", default="", help="It's working")
      # Set `include_in_web_ui` to False if you want to hide from the web UI
      parser.add_argument("--my-ui-invisible-argument", include_in_web_ui=False, default="I am invisible")
      # Set `is_secret` to True if you want the text input to be password masked in the web UI
      parser.add_argument("--my-ui-password-argument", is_secret=True, default="I am a secret")
  
  
  @events.test_start.add_listener
  def _(environment, **kw):
      print(f"Custom argument supplied: {environment.parsed_options.my_argument}")
  
  
  class WebsiteUser(HttpUser):
      @task
      def my_task(self):
          print(f"my_argument={self.environment.parsed_options.my_argument}")
          print(f"my_ui_invisible_argument={self.environment.parsed_options.my_ui_invisible_argument}")
  ```

- **request_success**: 请求成功时触发。

- **request_failure**: 请求失败时触发。

- **user_count**: 虚拟用户数量发生变化时触发。

- **hatch_complete**: 虚拟用户孵化完成时触发。

- **report_to_master**: 当Worker节点将统计信息报告给Master节点时触发。

- **report_to_client**: 当Master节点将统计信息报告给客户端时触发。

- **worker_report**: 当Master节点收到Worker节点的统计信息报告时触发。

- **spawn_complete**: 当所有的虚拟用户都被孵化完成时触发。

- **spawning_started**: 当虚拟用户的孵化过程开始时触发。

- **spawning_more_users**: 每次增加虚拟用户时触发。

- **spawning_ended**: 当虚拟用户的孵化过程结束时触发。

- **request**: 每次请求发送之前触发。

  ```python
  @events.request.add_listener
  def my_request_handler(request_type, name, response_time, response_length, response,
                         context, exception, start_time, url, **kwargs):
      if exception:
          print(f"Request to {name} failed with exception {exception}")
      else:
          print(f"Successfully made a request to: {name}")
          print(f"The response was {response.text}")
  ```

- **response**: 每次请求得到响应之后触发。

- **quit**: 当Locust进程即将退出时触发。

- **worker_report**: 当Master节点收到Worker节点的统计信息报告时触发。

- **heartbeat**: 每个Slave节点和Master节点之间的心跳事件。

##### 请求

```python
with self.client.post("/", json={"foo": 42, "bar": None}, catch_response=True) as response:
    try:
        if response.json()["greeting"] != "hello":
            response.failure("Did not get expected value in greeting")
    except JSONDecodeError:
        response.failure("Response could not be decoded as JSON")
    except KeyError:
        response.failure("Response did not contain expected key 'greeting'")
```

### 分布式运行

要在主模式下启动蝗虫：

```python
locust -f my_locustfile.py --web-host=127.0.0.1 --master
```

然后在每个工作线程上（替换为主计算机的 IP，或者如果您的工作线程与主计算机在同一台计算机上，则完全省略该参数）：

```Python
locust -f my_locustfile.py --worker --master-host=127.0.0.1
```

`--master`

将蝗虫设置为主模式。Web 界面将在此节点上运行。

`--worker`

在辅助角色模式下设置蝗虫。

`--master-host=X.X.X.X`

可选择与 一起使用，以设置主节点的主机名/IP（默认值 至 127.0.0.1）`--worker`

`--master-port=5557`

（可选）与 一起使用以设置主节点的端口号（默认为 5557）。`--worker`

`--master-bind-host=X.X.X.X`

可选择与 一起使用。确定主节点的网络接口 将绑定到。默认为 *（所有可用接口）。`--master`

`--master-bind-port=5557`

可选择与 一起使用。确定主节点将采用哪些网络端口 听。默认值为 5557。`--master`

`--expect-workers=X`

使用 启动主节点时使用。然后，主节点将等待 X 工作线程 节点在测试开始之前已连接。`--headless`

##### 跨节点通讯

```Python
# 当工作者接收到类型为“test_users”的消息时激发
def setup_test_users(environment, msg, **kwargs):
    for user in msg.data:
        print(f"User {user['name']} received")
    environment.runner.send_message('acknowledge_users', f"Thanks for the {len(msg.data)} users!")

# 当主机接收到类型为“acknowledge_users”的消息时激发
def on_acknowledge(msg, **kwargs):
    print(msg.data)

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if not isinstance(environment.runner, MasterRunner):
        environment.runner.register_message('test_users', setup_test_users)
    if not isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message('acknowledge_users', on_acknowledge)

@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    if not isinstance(environment.runner, WorkerRunner):
        users = [
            {"name": "User1"},
            {"name": "User2"},
            {"name": "User3"},
        ]
        environment.runner.send_message('test_users', users)
```

### 参数化

```Python
import queue
class AnimalTask(TaskSet):

    def on_start(self):
        print(f'加载中')
        all_locusts_spawned.wait()

    def on_stop(self):
        print('退出中')

    @tag('sbt')
    @task(1)
    def animal_1(self):
        data = MyUser.queue_data.get()
        print(f'Animal_1: {data}')
        # MyUser.queue_data.put_nowait(data)  # 使用完的参数继续put到队列中，如果不put 等get完后性能测试则会停止
        time.sleep(3)

    @task(2)
    def animal_2(self):
        print('Animal_2')
        time.sleep(3)


class MyUser(FastHttpUser):
    tasks = {AnimalTask: 1}
    wait_time = between(0, 0)
    host = "https://www.ricequant.com/"
    queue_data = queue.Queue()
    for i in range(10):
        play_load = {
            'aaa': i
        }
        queue_data.put_nowait(play_load)
```

