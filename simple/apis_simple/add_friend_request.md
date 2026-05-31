# 处理加好友请求

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /set_friend_add_request:
    post:
      summary: 处理加好友请求
      deprecated: false
      description: 同意或拒绝加好友请求
      tags:
        - 用户接口
        - 用户接口
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                flag:
                  description: 加好友请求的 flag (需从上报中获取)
                  type: string
                approve:
                  description: 是否同意请求
                  anyOf:
                    - type: string
                    - type: boolean
                remark:
                  description: 添加后的好友备注
                  type: string
              required:
                - flag
              x-apifox-orders:
                - flag
                - approve
                - remark
              x-apifox-ignore-properties: []
            examples:
              Default:
                value:
                  flag: flag_12345
                  approve: true
                  remark: 新朋友
                summary: 默认请求示例
      responses:
        '200':
          description: 业务响应
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/BaseResponse'
                  - type: object
                    required:
                      - data
                    properties:
                      data:
                        type: 'null'
                        description: 业务数据
                    x-apifox-orders:
                      - data
                    x-apifox-ignore-properties: []
              examples:
                Success:
                  summary: 成功响应
                  value:
                    status: ok
                    retcode: 0
                    data: {}
                    message: ''
                    wording: ''
                    stream: normal-action
                Error_1400:
                  summary: 请求参数错误或业务逻辑执行失败
                  value:
                    status: failed
                    retcode: 1400
                    data: null
                    message: 请求参数错误或业务逻辑执行失败
                    wording: 请求参数错误或业务逻辑执行失败
                    stream: normal-action
                Error_1401:
                  summary: 权限不足
                  value:
                    status: failed
                    retcode: 1401
                    data: null
                    message: 权限不足
                    wording: 权限不足
                    stream: normal-action
                Error_1404:
                  summary: 资源不存在
                  value:
                    status: failed
                    retcode: 1404
                    data: null
                    message: 资源不存在
                    wording: 资源不存在
                    stream: normal-action
          headers: {}
          x-apifox-name: 成功
      security: []
      x-apifox-folder: 用户接口
      x-apifox-status: released
      x-run-in-apifox: https://app.apifox.com/web/project/5348325/apis/api-226656932-run
components:
  schemas:
    BaseResponse:
      type: object
      x-schema-id: BaseResponse
      properties:
        status:
          type: string
          description: 状态 (ok/failed)
        retcode:
          type: number
          description: 返回码
        data:
          type: string
        message:
          type: string
          description: 消息
        wording:
          type: string
          description: 提示
        stream:
          type: string
          description: 流式响应
          enum:
            - stream-action
            - normal-action
      required:
        - status
        - retcode
      x-apifox-orders:
        - status
        - retcode
        - data
        - message
        - wording
        - stream
      x-apifox-ignore-properties: []
      x-apifox-folder: ''
  securitySchemes: {}
servers: []
security: []

```