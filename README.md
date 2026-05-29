# QQ机器人 - 消息统计系统

## 功能概述

这是一个基于NapCat的QQ机器人，主要功能包括：

1. **群聊消息统计**：统计关注用户在群聊中的消息数量
2. **私聊指令处理**：支持 `/register` 和 `/select` 指令
3. **自动数据保存**：每分钟自动保存数据到磁盘
4. **关注列表管理**：管理需要统计的用户

## 目录结构

```
qqrobot/
├── main.py              # 主程序（极简）
├── config.py           # 配置文件
├── configs/            # 配置文件目录（自动生成）
│   └── follows.txt     # 关注用户列表（自动生成）
├── messages/           # 用户消息数据目录（自动生成）
├── function/           # 功能模块
│   ├── __init__.py
│   ├── message_handler.py  # 消息处理器
│   ├── websocket_server.py # WebSocket服务器
│   ├── utils.py           # 工具函数
│   └── reverse.py        # 原有功能
└── simple/             # 示例消息文件
    ├── groupmessage_reverse_simple.json
    └── privatemessage_reverse_simple.json
```

## 安装和运行

### 1. 安装依赖

```bash
pip install websockets
```

### 2. 配置NapCat

确保NapCat已正确配置并运行，WebSocket服务器地址为：`ws://localhost:9001`

### 3. 运行机器人

```bash
python main.py
```

## 使用说明

### 消息处理流程

1. **群聊消息**：
   - 检查发送者是否在 `configs/follows.txt` 关注列表中
   - 如果在，则记录该用户在当天的消息数量
   - 每分钟自动保存到 `messages/{用户QQ}.json` 文件

2. **私聊消息**：
   - 支持三个指令：
     - `/register`：关注当前用户，将其QQ号添加到 `configs/follows.txt`
     - `/select`：查询当前用户最近7天在各群聊的消息数量
     - `/help`：显示所有可用指令的帮助信息
   - 其他消息：自动回复可用指令列表

### 数据格式

#### 用户数据文件 (`messages/{用户QQ}.json`)
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

#### 关注列表文件 (`configs/follows.txt`)
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

## 注意事项

1. 确保NapCat的WebSocket服务器已正确配置
2. 首次运行会自动创建 `messages/`、`configs/` 目录和 `configs/follows.txt` 文件
3. 数据每分钟自动保存，程序异常退出时可能会丢失最近1分钟的数据
4. 关注列表修改后立即生效，无需重启程序
5. 私聊发送任何非指令消息都会收到可用指令提示

## 故障排除

1. **连接失败**：检查NapCat是否运行，Token是否正确
2. **数据未保存**：检查 `messages/` 目录权限
3. **指令无效**：检查私聊消息格式是否正确
4. **统计不准确**：检查用户是否在关注列表中

## 扩展功能

如需添加新功能，可以在 `function/` 目录下创建新的模块，然后在 `message_handler.py` 中集成。