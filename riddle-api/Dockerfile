# 使用PHP官方镜像作为基础镜像
FROM php:8.1-fpm-alpine

# 设置工作目录
WORKDIR /var/www/html

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

# 安装系统依赖
RUN apk update && apk add --no-cache \
    nginx \
    supervisor \
    git \
    curl \
    libzip-dev \
    zip \
    openssl \
    ca-certificates \
    gettext-dev \
    libintl \
    && apk add --no-cache --virtual .build-deps \
    icu-dev \
    && (grep -q 'www-data' /etc/group || addgroup -g 82 -S www-data) && (grep -q 'www-data' /etc/passwd || adduser -u 82 -D -S -G www-data www-data)

# 安装PHP扩展 - iconv和tokenizer在php:8.1-fpm-alpine中已经内置，不需要单独安装
RUN docker-php-ext-install \
    zip \
    pdo \
    pdo_mysql \
    intl

# 配置内存限制
RUN echo 'memory_limit = 512M' > /usr/local/etc/php/conf.d/memory.ini

# 安装Composer并设置配置
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer config -g process-timeout 3600 \
    && composer config -g discard-changes true

# 复制项目文件
COPY . .

# 安装项目依赖（只安装生产环境依赖，增加重试机制和超时设置）
RUN composer install --no-dev --optimize-autoloader --prefer-dist --no-scripts --no-progress --no-interaction --ignore-platform-reqs

# 设置正确的文件权限
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html/storage \
    && chmod -R 755 /var/www/html/vendor

# 创建vendor目录的挂载后初始化脚本
RUN mkdir -p /var/www/html/vendor && chown -R www-data:www-data /var/www/html/vendor && chmod -R 755 /var/www/html/vendor

# 配置PHP-FPM
RUN mkdir -p /usr/local/etc/php-fpm.d/
COPY --chown=www-data:www-data ./.docker/php-fpm/www.conf /usr/local/etc/php-fpm.d/www.conf

# 配置Nginx
RUN mkdir /etc/nginx/conf.d/ && mkdir /etc/supervisor/
COPY --chown=nginx:nginx ./.docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx ./.docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# 配置Supervisor
COPY ./.docker/supervisor/supervisord.conf /etc/supervisor/supervisord.conf

# 暴露80端口
EXPOSE 8000

# 创建必要的目录
RUN mkdir -p /var/log/supervisor

# 使用初始化脚本启动服务
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]