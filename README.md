### 项目简介
该项目用于查询LeetCode用户每日提交数，并支持将结果发送到指定地址。 

### 项目说明
- 获取LeetCode用户提交数据
- 将结果发送到指定终端
- 支持github action定时执行，发送监控消息
- 支持docker部署，实现自定义时间发送监控消息

### 目前支持的消息终端：
- ✅指定webhook url
- ✅telegram bot


### 使用方法
1.克隆项目

`git clone https://github.com/HMYDK/leetcode-monitor.git`

2.创建独立的 Python 环境并安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

3.修改 users 列表，添加要查询的用户

`修改config.json文件中的users列表`

`users` 支持多个力扣中国站用户名，例如：

```json
"users": [
  {
    "username": "gracious-leavittnie",
    "display_name": "Alexcat"
  },
  {
    "username": "friend-user-slug",
    "display_name": "朋友昵称"
  }
]
```

`username` 用于查询力扣中国站，`display_name` 只用于结果展示。也继续支持原有的用户名字符串写法。

4.默认使用 `"channel_type": "console"`，只在终端和 GitHub Actions 摘要中输出，不需要 webhook。

5.运行脚本

```bash
python monitor.py
```

6.借助 GitHub Actions 定时执行程序

- 将本项目放到你自己的 GitHub 仓库。
- 在仓库的 **Actions** 页面启用 workflow。
- 可在 **Daily Job** 中点击 **Run workflow** 手动测试。
- 默认每天 15:55 UTC（中国时间 23:55）运行；GitHub 定时任务可能略有延迟。
- 此控制台模式不需要 GitHub Secrets，结果可在每次 workflow 的运行摘要和日志中查看。



### 注意事项
- LeetCode官方API可能会限制请求频率，请勿频繁调用
- 只有启用钉钉或 Telegram 消息时才需要相应配置。不要将 webhook、Token、Cookie 或密码提交到公开仓库；应使用 GitHub Actions Secrets。

### 示例输出
![image](https://github.com/HMYDK/leetcode-monitor/assets/27269137/9867d903-2b67-413c-b67f-463fa51fce37)


### 贡献
欢迎大家对项目进行贡献，包括：
- 提出新的功能建议
- 修复代码中的bug
- 完善项目文档

### 许可
本项目采用MIT开源许可证，欢迎自由使用和修改。
