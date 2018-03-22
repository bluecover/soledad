# SOLAR :: 好规划
 
[![CI Status](http://www.tuluu.com/ci/projects/1/status.png?ref=master)](http://www.tuluu.com/guihua/solar/builds?scope=all)
            
> 每个计算机的环境不同，所以安装方式也不同，如果有错误，请到 
> [#技术-研发](https://guihua.bearychat.com/messages/技术-研发) 提问。

> 提交 Merge Request 时，如果需要和 master 分支一样运行 webtest 集成测试，
> 请将分支名命名为 `webtest`。

## 开发环境

### 安装前端全局依赖

- [Node.js](http://nodejs.org/download/): `brew install node.js`
- [phantomjs](http://phantomjs.org) `brew cask install tonyseek/phantomjs/phantomjs-sakura`

### 安装后端全局依赖

- [Python 2.7](https://www.python.org/downloads/release/python-279/): `brew install python`
- [Upgrate 雷自给](https://pip.pypa.io/): `pip install -U setuptools pip`
- [Virtualenv](https://virtualenv.pypa.io): `pip install -U virtualenv`
- [MySQL](https://mariadb.com): `brew install mariadb`
- [CouchDB](http://couchdb.apache.org/): `brew install couchdb`
- [Beanstalkd](http://kr.github.io/beanstalkd/): `brew install beanstalkd`
- [Redis](http://redis.io): `brew install redis`

````sh
docker create --name solar-db-data -v /var/lib/mysql busybox:1 echo solar db data
docker run --name solar-db -e MYSQL_ROOT_PASSWORD=solaradmin -e MYSQL_DATABASE=guihua -e MYSQL_USER=guihua -e MYSQL_PASSWORD=guihua --volumes-from=solar-db-data -p 33065:3306 -d lcgc/mariadb:10.1.8
````

### 安装项目本地依赖

    $ cd /path/to/solar
    $ virtualenv -p python2.7 venv
    $ . venv/bin/activate
    $ make install-deps

### 准备环境变量

    $ cp .env.example .env
    $ vim .env

### 启动系统服务

    $ brew tap homebrew/services
    $ brew services list
    $ brew services start beanstalkd
    $ brew services start mariadb
    $ brew services start couchdb
    $ brew services start redis

或安装 LaunchRocket 图形化工具:

    $ brew install caskroom/cask/brew-cask  # 先安装 Homebrew Cask
    $ brew cask install launchrocket

### 准备数据库和填充测试数据

    $ make initdb fillup

### 启动进程

    $ . venv/bin/activate
    $ honcho start

Honcho 运行中如果有一个子进程退出，其他依赖服务也会同步退出，以确保环境干净。

如果遇到 Honcho 刚启动即退出的情况，可以看输出的信息诊断，或逐一用 `honcho run`
试运行 `Procfile` 里的各个服务。

### Shell 调试

    $ . venv/bin/activate
    $ honcho run python manage.py shell

### 测试

    $ . venv/bin/activate
    $ make lint
    $ make unittest
    $ make webtest

### 反向代理

使用 [pow](http://pow.cx) 可以让开发环境拥有 `www.guihua.dev` 形式的 URL。

    $ brew install pow
    $ mkdir -p ~/Library/Application\ Support/Pow/Hosts
    $ ln -s ~/Library/Application\ Support/Pow/Hosts ~/.pow
    $ sudo pow --install-system
    $ pow --install-local
    $ sudo launchctl load -w /Library/LaunchDaemons/cx.pow.firewall.plist
    $ launchctl load -w ~/Library/LaunchAgents/cx.pow.powd.plist

此后 `$HOME/.pow` 中放置反向代理的端口信息。例如 `echo 5000 > ~/.pow/www.guihua`
后，`www.guihua.dev` 则被反向代理到 `127.0.0.1:5000` (开发服务器监听的地址)。

结合 [xip](http://xip.io) 可允许局域网中的其他主机访问服务。

    $ ifconfig en0 inet
    inet 192.168.1.71 netmask 0xffffff00 broadcast 192.168.1.255
    $ curl -L http://www.guihua.192.168.1.71.xip.io  # 局域网地址

公司内部的 [skydns-me](http://skydns-me.tuluu.com) 也同样可用。

除 `pow` 外，另一个公网代理服务 [ngrok](http://www.tunnel.mobi)
可将本地服务代理到公网供外部访问。这个方案速度更慢，适用于远程联调。


## 配置管理

项目本地依赖、数据库表结构等应用配置信息应该和应用代码一样被版本控制。
当它们出现变化时，变更的内容也应该被提交到版本库。

### Python 依赖管理

Python 依赖存放在三个文本文件中:

- `requirements.in`: 运行时依赖
- `requirements-dev.in`: 开发工具
- `requirements-testing.in`: 测试工具和测试环境依赖

管理依赖时，应该编辑 `requierments*.in` 文件并运行 `make compile-deps` 以更新
`requirements*.txt`，然后**将变更提交入版本库**。

生产环境应该被假设只安装 `requirements.txt` 中的依赖。

### Node.js 依赖管理

Node.js 依赖存放在 `package.json` 中。使用 `npm install --save foo` 或
`npm install --save-dev bar` 可以在安装包的同时将变更写入 `package.json`。

### 数据库表结构管理

    $ mysql -uroot haoguihua < database/schema.sql  # 覆盖内存表
    $ mysqldump $MYSQL_OPTS -d --add-drop-table haoguihua > database/schema.sql

如果只需要提交部分文件，可以借助 `git add -p database/schema.sql` 中 `-p` 参数的帮助。
如果需要生成数据表迁移文件，可安装 [sqlt-diff](http://blog.johngoulah.com/tag/sqltranslator/)
并导出好表结构再在 `git add database/schema.sql` 之后运行 `make migrate-tables`。

### Gulp 任务管理

当执行 `honcho start` 启动任务时，在开发阶段，前端任务中不包含 svg 转成 png 图片格式任务。
若有需要，可手动执行 `gulp svg2png` 以生成对应 2 倍大小的 png 图片「路径和名称都和 svg 文件一致」。
