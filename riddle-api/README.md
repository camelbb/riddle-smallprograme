# 小程序 API 服务

这是一个基于 Lumen 框架开发的小程序 API 服务，提供谜语相关的接口功能。

## 项目环境要求

- PHP 8.0+  
- Composer  
- MySQL 数据库  
- 扩展要求：PDO、OpenSSL、Mbstring

## 安装步骤

1. 克隆代码与安装依赖
```bash
# 克隆项目代码
git clone [项目仓库地址]
cd api-smallprogram
# 安装依赖
composer install
```

2. 新建.env文件
复制 `.env.example` 文件并重命名为 `.env`，然后根据实际情况修改数据库配置

3. 导入数据库
使用提供的 `riddle.sql` 文件导入数据库：
```bash
mysql -u username -p database_name < riddle.sql
```

## 服务启动

### 方法一：使用 PHP 内置服务器（开发环境）
```bash
php -S localhost:8000 -t public
```
服务将在 `http://localhost:8000` 启动。

### 方法二：使用 Nginx（生产环境）
配置 Web 服务器，将根目录指向 `public` 文件夹，如：
```
server {
    listen 8080;
    server_name localhost;
    root /var/www/html/public;

    index index.php index.html index.htm;

    location / {
        try_files $uri $uri/ /index.php$is_args$args;
    }

    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    # 防止直接访问.env文件
    location ~ /\.env {
        deny all;
        return 404;
    }

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

## 方法三：Docker容器化部署
在.Docker文件夹，用于存放【容器部署】时所需的配置文件
```
# 创建镜像
docker build -t riddle-api .

# 启动容器 方式1
docker run -d -p 8000:80 riddle-api

# 启动容器 方式2（需先按照docker-composer）
docker-compose -f docker-compose.yml up -d
```

## API 接口文档

### 1. 获取谜语类型列表（支持分页）

**请求方法**：GET  
**请求路径**：`/api/riddles/types`  
**请求参数**：
- `page`：页码，默认 1
- `page_size`：每页数量，默认 20，最大 100

**响应示例**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "total": 788,
    "page": 1,
    "page_size": 10,
    "total_pages": 79,
    "list": [
      {
        "id": 1,
        "type": "植物",
        "update_time": "2025-10-15 11:27:21"
      },
      {
        "id": 2,
        "type": "科技名词",
        "update_time": "2025-10-15 11:29:08"
      }
    ]
  }
}
```

### 2. 根据谜语类型ID获取谜语列表（支持分页）

**请求方法**：GET  
**请求路径**：`/api/riddles/list`  
**查询参数**：
- `type_id`：谜语类型ID（必填）
- `page`：页码，默认 1
- `page_size`：每页数量，默认 20，最大 100

**响应示例**（成功）：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "total": 434,
    "page": 1,
    "page_size": 5,
    "total_pages": 87,
    "list": [
      {
        "id": 1,
        "riddle_type_id": 1,
        "riddle": "脱了衣服见头发，拨开头发就见牙。打一植物",
        "answer": "玉米",
        "update_time": "2025-10-15 11:27:21"
      }
    ]
  }
}

**响应示例**（缺少必填参数）：

```json
{
  "code": 400,
  "message": "type_id parameter is required",
  "data": null
}

**响应示例**（无效 type_id）：

```json
{
  "code": 400,
  "message": "Invalid type_id",
  "data": null
}
```

### 3. 根据谜语 ID 获取谜语详情

**请求方法**：GET  
**请求路径**：`/api/riddles/info`  
**查询参数**：
- `id`：谜语 ID（必填，整数，> 0）

**响应示例**（成功）：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "riddle": "脱了衣服见头发，拨开头发就见牙。打一植物",
    "answer": "玉米",
    "riddle_type_id": 1,
    "riddle_type": "植物",
    "update_time": "2025-10-15 11:27:21"
  }
}
```

**响应示例**（谜语不存在）：

```json
{
  "code": 404,
  "message": "Riddle not found",
  "data": null
}
```

**响应示例**（无效 ID）：

```json
{
  "code": 400,
  "message": "Invalid riddle id",
  "data": null
}

**响应示例**（缺少必填参数）：

```json
{
  "code": 400,
  "message": "id parameter is required",
  "data": null
}
```

### 4. 随机获取指定类型的谜语（排行榜接口）

**请求方法**：GET  
**请求路径**：`/api/riddles/rank`  
**查询参数**：
- `riddle_type`：谜语类型ID（必填，整数，> 0）
- `count`：返回数量，默认 5，最大 50

**响应示例**（成功）：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "list": [
      {
        "id": 1,
        "riddle_type_id": 1,
        "riddle": "脱了衣服见头发，拨开头发就见牙。打一植物",
        "answer": "玉米",
        "update_time": "2025-10-15 11:27:21"
      },
      {
        "id": 5,
        "riddle_type_id": 1,
        "riddle": "小时青青肚里空，长大头发蓬蓬松。姐姐撑船不离它，哥哥钓鱼拿手中。",
        "answer": "竹子",
        "update_time": "2025-10-15 11:27:21"
      }
    ]
  }
}
```

**响应示例**（缺少必填参数）：

```json
{
  "code": 400,
  "message": "riddle_type parameter is required",
  "data": null
}
```

**响应示例**（无效 riddle_type）：

```json
{
  "code": 400,
  "message": "Invalid riddle_type",
  "data": null
}
```

## 错误响应格式

当请求失败时，API 将返回统一的错误响应格式：

```json
{
  "code": 400,
  "message": "错误消息",
  "data": null
}
```

常见错误码：
- 400：请求参数错误
- 404：请求的资源不存在
- 500：服务器内部错误

## 项目结构

```
api-smallprogram/
├── app/                 # 应用核心代码
│   ├── Http/Controllers/  # 控制器
│   ├── Models/           # 数据模型
│   └── Providers/        # 服务提供者
├── bootstrap/           # 应用引导文件
├── config/              # 配置文件
├── public/              # 公共目录（入口文件）
├── routes/              # 路由定义
├── storage/             # 存储目录
└── vendor/              # Composer 依赖
```

## 开发说明

1. **添加新路由**：在 `routes/web.php` 文件中定义
2. **创建新控制器**：在 `app/Http/Controllers/` 目录下创建
3. **数据库操作**：使用 Lumen 内置的 Eloquent ORM
4. **日志查看**：日志文件位于 `storage/logs/` 目录