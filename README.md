## beta版已经可用，下面是说明

### 运行环境
- Python
- Sqlite
- waitress

### 运行方法
1. 修改配置文件config.py中的数据库路径和密钥（如果你需要也可以修改端口号，wsgi会默认监听当前ip）
``` Python
Debug = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database_path.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'your_secret_key'
PORT = 80
```
1. 在cmd中运行
   ``` cmd
   pip install flask flask-sqlalchemy
   flask-login schedule waitress
   ```
2. 运行
   ``` cmd
   python wsgi.py
   ```
   当你看见备份已启动时，证明程序已经运行
   访问http://your-ip-address（你可以使用Ipv4或Ipv6）

---

## 基础功能实现

- 商品管理（此处不显示商品价格）
  - [x] 商品基本信息以及价格体系（进货价，零售价，会员价.....）
  - [x] 添加商品
  - [x] 删除商品
  - [ ] 修改商品 （弃用）
  - [x] 入库
  - [x] 出库
  - [ ] 支持撤销操作
  - [x] 历史记录
- 库存管理
  - [ ] 借还货（保留备用）
  - [ ] 报表生成
  - [ ] 统计
  - [ ] 盘点
- 下单
  - [ ] 下单表生成
  - [ ] 采购商品（下单）
  - [ ] 物流信息（暂留）
- [x] 用户登录
- 设置
  - [ ] 用户管理
  - [ ] 商品管理
  - [ ] 下单管理
  - [ ] 发信配置
  - [ ] 数据库管理

---

> 本程序特别简单，其目的是方便家中的商品统计，简化步骤，整合多个环节
> 本人技术并不好，因此其中存在各种奇怪的代码和调用方法，后续会逐步修正

> 写到一半才发现没创建虚拟环境（😓）

---

注意：templates中模板报错请忽略，可能是js代码中包含jinjia语法