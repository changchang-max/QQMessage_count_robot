# QQ机器人 - 消息统计系统

## 功能概述

这是一个基于NapCat的QQ机器人，主要功能包括：

1. **群聊消息统计**：统计关注用户在群聊中的消息数量
2. **私聊指令处理**：支持 `/register`、`/select`、`/help` 指令
3. **自动通过好友申请**：自动通过所有好友申请请求
4. **心跳检测与邮件提醒**：超时5分钟未收到有效消息时，通过QQ邮箱发送邮件提醒
5. **自动数据保存**：每分钟自动保存数据到磁盘
6. **关注列表管理**：管理需要统计的用户

## 目录结构

```
qqrobot/
├── main.py              # 主程序（极简）
├── config.py           # 配置文件
├── environment.env     # 环境变量配置文件（邮件提醒相关）
├── data/               # 数据目录（自动生成）
│   ├── configs/        # 配置文件目录（自动生成）
│   │   └── follows.txt # 关注用户列表（自动生成）
│   ├── logs/           # 日志文件目录（自动生成）
│   └── messages/       # 用户消息数据目录（自动生成）
├── function/           # 功能模块
│   ├── __init__.py
│   ├── message_handler.py      # 消息处理器
│   ├── websocket_server.py     # WebSocket服务器
│   ├── heartbeat_monitor.py    # 心跳检测与邮件提醒模块
│   ├── apply_add_friend.py     # 自动通过好友申请模块
│   ├── utils.py                # 工具函数
│   ├── logger.py               # 异步日志模块
│   └── reverse.py              # 原有功能
└── simple/             # 示例消息文件
    ├── groupmessage_reverse_simple.json
    ├── privatemessage_reverse_simple.json
    └── addfriend_reverse_simple.json
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install websockets python-dotenv
```

### 2. 配置环境变量

复制 `environment.env.example` 为 `environment.env`，并填写以下配置：

```env
# NapCat配置
NAPCAT_TOKEN=your_napcat_token_here

# QQ邮箱配置（用于心跳检测邮件提醒）
QQ_EMAIL_SENDER=your_qq_email@qq.com
QQ_EMAIL_RECEIVER=recipient_email@qq.com
QQ_EMAIL_AUTH_CODE=your_qq_email_auth_code
```

获取QQ邮箱授权码：
1. 登录QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
2. 开启POP3/SMTP服务，获取授权码

### 3. 配置NapCat

确保NapCat已正确配置并运行，WebSocket服务器地址为：`ws://localhost:9001`

### 3. 运行机器人

```bash
python main.py
```

## 使用说明

### 消息处理流程

1. **群聊消息**：
   - 检查发送者是否在 `data/configs/follows.txt` 关注列表中
    - 如果在，则记录该用户在当天的消息数量
    - 每分钟自动保存到 `data/messages/{用户QQ}.json` 文件

2. **私聊消息**：
   - 支持三个指令：
     - `/register`：关注当前用户，将其QQ号添加到 `data/configs/follows.txt`
     - `/select`：查询当前用户最近7天在各群聊的消息数量
     - `/help`：显示所有可用指令的帮助信息
   - 其他消息：自动回复可用指令列表

### 数据格式

#### 用户数据文件 (`data/messages/{用户QQ}.json`)
```json
{
  "2026-05-29": {
    "459134559": {
      "group_name": "小阳人、Yr、。",
      "count": 123
    }
  },
  "2026-05-30": {
    "459134559": {
      "group_name": "小阳人、Yr、。",
      "count": 456
    }
  }
}
```

#### 关注列表文件 (`data/configs/follows.txt`)
```
3338366373
2774118934
```

### 指令示例

1. **关注指令**：
   ```
   用户：/register
   机器人：关注成功！
   ```

2. **查询指令**：
   ```
   用户：/select
   机器人：
   2026-05-29
     小阳人、Yr、。  消息数：123
   2026-05-28
     小阳人、Yr、。  消息数：456
   ```

3. **帮助指令**：
   ```
   用户：/help
   机器人：
   可用指令：
   
   /register - 关注当前用户，开始统计您的群聊消息
   /select   - 查询您最近7天在各群聊的消息数量
   /help     - 显示此帮助信息
   
   说明：
   1. 发送 /register 后，机器人会开始统计您在群聊中的消息
   2. 发送 /select 可以查看您的消息统计
   3. 统计每分钟自动保存一次
   ```

4. **其他消息**（自动提示指令）：
   ```
   用户：你好，机器人
   机器人：
   可用指令：
   
   /register - 关注当前用户，开始统计您的群聊消息
   /select   - 查询您最近7天在各群聊的消息数量
   /help     - 显示此帮助信息
   
   说明：
   1. 发送 /register 后，机器人会开始统计您在群聊中的消息
   2. 发送 /select 可以查看您的消息统计
   3. 统计每分钟自动保存一次
   ```

## 配置说明

修改 `config.py` 文件可以调整以下设置：

- `WS_HOST`：WebSocket服务器监听地址
- `WS_PORT`：WebSocket服务器端口
- `WS_TOKEN`：NapCat认证Token
- `SAVE_INTERVAL`：数据保存间隔（秒）
- `QUERY_DAYS`：查询天数
- `DEBUG`：调试模式开关
- `EMAIL_SENDER`：QQ邮箱发送者地址（从环境变量读取）
- `EMAIL_RECEIVER`：邮件接收者地址（从环境变量读取）
- `EMAIL_AUTH_CODE`：QQ邮箱授权码（从环境变量读取）

## 心跳检测与邮件提醒机制

### 工作原理

1. **心跳消息**：NapCat定期发送 `meta_event` 类型的心跳消息（约30秒一次）
2. **超时检测**：系统持续监测最后收到有效消息的时间
3. **阈值设定**：超过5分钟未收到任何消息视为连接异常
4. **邮件提醒**：检测到超时时，通过QQ邮箱发送报警邮件

### 邮件内容示例

```
主题：QQ机器人连接异常提醒

内容：
QQ机器人连接状态异常！
最后收到消息时间：2026-05-31 21:53:40
当前时间：2026-05-31 22:00:00
超时时间：6分钟20秒

建议检查：
1. NapCat服务是否正常运行
2. 网络连接是否正常
3. 防火墙设置是否阻止连接
```

### 配置要求

1. **必须正确配置** `environment.env` 中的邮箱相关配置
2. 确保发送邮箱已开启SMTP服务
3. 使用正确的QQ邮箱授权码

## 注意事项

1. 确保NapCat的WebSocket服务器已正确配置
2. 首次运行会自动创建 `data/` 目录及其子目录 `data/messages/`、`data/configs/` 和 `data/configs/follows.txt` 文件
3. 数据每分钟自动保存，程序异常退出时可能会丢失最近1分钟的数据
4. 关注列表修改后立即生效，无需重启程序
5. 私聊发送任何非指令消息都会收到可用指令提示
6. 所有好友申请会自动通过
7. 心跳检测邮件提醒需要正确配置QQ邮箱信息

## 故障排除

1. **连接失败**：检查NapCat是否运行，Token是否正确
2. **数据未保存**：检查 `data/messages/` 目录权限
3. **指令无效**：检查私聊消息格式是否正确
4. **统计不准确**：检查用户是否在关注列表中
5. **心跳检测邮件未发送**：
   - 检查 `environment.env` 配置是否正确
   - 确认QQ邮箱已开启SMTP服务
   - 验证邮箱授权码是否正确
   - 检查网络连接和防火墙设置
6. **好友申请未自动通过**：
   - 检查 `post_type` 是否为 `"request"`
   - 检查 `request_type` 是否为 `"friend"`
   - 确认消息中是否包含有效的 `flag` 字段
7. **心跳检测误报**：
   - NapCat可能暂时停止发送心跳消息
   - 检查NapCat日志确认是否正常运行
   - 网络波动可能导致短暂连接中断

## 版本历史

### v0.0.2 (2026-05-31)
- 新增自动通过好友申请功能
- 新增心跳检测与邮件提醒机制
- 优化日志系统，异步写入日志文件
- 添加配置文件和环境变量支持
- 脱敏所有敏感数据，添加.gitignore

### v0.0.1 (2026-05-31)
- 实现基础消息统计功能
- 支持关注指令 (`/register`)
- 支持查询指令 (`/select`)
- 支持帮助指令 (`/help`)
- 自动数据保存与缓存机制

## 扩展功能

如需添加新功能，可以在 `function/` 目录下创建新的模块，然后在 `message_handler.py` 中集成。