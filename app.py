from flask import Flask, render_template, request, redirect, url_for, flash
import config, ProductORM, UsersORM, HistoryORM
import datetime, backup
from extension import init_ext
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config.from_object(config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录！'
db = init_ext(app)
with app.app_context():
    db.create_all()

# 默认启用自动备份
print(backup.start_backup_thread())


# 用户回调函数
@login_manager.user_loader
def load_user(user_id):
    """根据用户id获取用户"""
    return UsersORM.Users.query.get(int(user_id))


# 主页
@app.route('/')
@login_required
def index():
    # 请求数据库，获取信息
    products = ProductORM.Product.query.all()
    # 商品种类，数量，总价值
    kinds = len(products)
    total_price = sum([(product.price1 * product.quantity) for product in products])
    quantity = sum([product.quantity for product in products])
    # 检查欠货信息（即商品库存为负数）,多个商品库存不足时显示为xxx,xxx库存不足
    # 检查库存不足
    alert1 = ''
    alert2 = ''
    for product in products:
        if product.quantity < 0:
            alert1 += product.name + ' '
        if product.quantity == 0:
            alert2 += product.name + ' '
    # 显示库存不足信息
    if alert1 and alert2:
        flash(alert1 + '已欠货')
        flash(alert2 + '已无库存')
    elif alert1:
        flash(alert1 + '已欠货')
    else:
        flash(alert2 + '已无库存')
    return render_template('index.html', kinds=kinds, quantity=quantity, price=total_price)


# 登录页
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = UsersORM.Users.query.filter_by(username=username).first()
        # 查询用户状态，如果是disabled则禁止登陆
        if user and user.type == 'disabled':
            flash('用户被禁用！')
            return redirect(url_for('login'))
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！')
            return redirect(url_for('login'))
    return render_template('login.html')


# 退出
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# 商品列表
@app.route('/product')
@login_required
def product():
    # 读取商品数据
    products = ProductORM.Product.query.all()
    # 解析数据
    products_lst = []
    for product in products:
        products_lst.append({
            'id': product.id,
            'name': product.name,
            'price1': product.price1,
            'price2': product.price2,
            'price3': product.price3,
            'price4': product.price4,
            'price5': product.price5,
            'price6': product.price6,
            'quantity': product.quantity
        })
    # print(products_lst)
    return render_template('product.html', products=products)


# 库存管理
@app.route('/stock/statistic')
@login_required
def stock():
    # 读取商品数据
    products = ProductORM.Product.query.all()
    # 获取商品总数和总金额
    kinds = len(products)
    total_quantity = sum([product.quantity for product in products])
    total_price = sum([(product.price1 * product.quantity) for product in products])
    # 获取当月销售数据，利用history数据库查询本月的出库数量
    current_month = datetime.datetime.now().month
    sell_products = ProductORM.Product.query.filter(
        HistoryORM.History.time >= datetime.datetime(datetime.datetime.now().year, current_month, 1)).all()
    # 计算本月销售数量和金额
    sell_quantity = sum([product.quantity for product in sell_products])
    # 此处无法计算total_price，需要结合客户类型
    # sell_price = sum([(product.price1 * product.quantity) for product in sell_products])
    # print(products_lst)
    return render_template('statistic.html', products=products, total_quantity=total_quantity, total_price=total_price,
                           kinds=kinds)


# 盘点
@app.route('/stock/history')
@login_required
def stock_history():
    # 获取商品出入库历史记录
    history = HistoryORM.History.query.all()
    # 筛选type为in和out
    history = [history for history in history if (history.type == 'in' or history.type == 'out')]
    print(history)
    return render_template('history.html', history=history)
# 数据查询
@app.route('/stock/history/search')
@login_required
def stock_history_search():
    # 获取需要查询的时间段
    start = request.args.get('start')
    end = request.args.get('end')
    start = datetime.datetime.strptime(start, '%Y-%m-%d')
    end = datetime.datetime.strptime(end, '%Y-%m-%d')
    print(start, end)
    history = HistoryORM.History.query.filter(HistoryORM.History.time >= start, HistoryORM.History.time <= end).all()
    print(history)
    # 解析history为json
    history = [{
        'id': history.id,
        'product_id': history.product_id,
        'product_name': history.product_name,
        'time': history.time,
        'type': history.type,
        'amount': history.amount
    } for history in history]
    return {
        'status': 'success',
        'code': 200,
        'data': history
    }



# 下单
@app.route('/purchace')
@login_required
def purchace():
    # 获取所有商品
    products = ProductORM.Product.query.all()
    # 获取所有客户（暂时没用）
    # customers = UsersORM.Users.query.filter_by(type='customer').all()
    return render_template('purchace.html', products=products)


# 设置部分
# 用户管理
@app.route('/settings/user_managment')
@login_required
def user():
    # 获取所有用户
    users = UsersORM.Users.query.all()
    return render_template('user.html', users=users)


# 客户管理
@app.route('/settings/customer_managment')
@login_required
def customer():
    # 此处先查询数据库中的客户数据，如果没有则连接wcferry获取，此处先pass
    return render_template('customer.html')


# 个人信息
@app.route('/settings/profile')
@login_required
def profile():
    return render_template('profile.html')


# 备份管理
@app.route('/settings/backup')
@login_required
def settings_backup():
    import backup_config
    return render_template('backup.html', config=backup_config)


# 在线升级（更新后台上载完整zip包，支持连接ota服务器升级和上传zip升级）
'''
模拟更新程序位于/update中
'''


@app.route('/settings/update', methods=['POST', 'GET'])
def settings_update():
    if request.method == 'POST':  # 前端请求
        pass
    elif request.method == 'GET':  # 后端回传请求
        return render_template('update.html', ver=config.app_ver)


# 添加商品(私有api)
@app.route('/product/add', methods=['POST'])
@login_required
def product_add():
    # 处理数据，加入数据库
    data = request.get_json()
    try:
        # 查询数据库中是否有该商品，由该商品返回错误，无该商品则添加
        name = data.get('name')
        price1 = data.get('price1')
        price2 = data.get('price2')
        price3 = data.get('price3')
        price4 = data.get('price4')
        price5 = data.get('price5')
        price6 = data.get('price6')
        quantity = data.get('stock')
        product = ProductORM.Product.query.filter_by(name=name).first()
        if product:
            return {
                'status': "error",
                'message': "商品已存在",
                'code': 400
            }
        else:
            # 创建商品
            product = ProductORM.Product(name=name, quantity=quantity, price1=price1,
                                         price2=price2, price3=price3, price4=price4,
                                         price5=price5, price6=price6)
            # 保存数据以产生id
            product.save()
            # 创建历史记录
            history = HistoryORM.History(datetime.datetime.now(), product.id, product.name, current_user.id, 'new', 0)
            # 保存数据
            history.save()
            return {
                'status': "success",
                'message': "添加成功",
                'code': 200
            }
    except Exception as r:
        # print(r)
        return {
            'status': "error",
            'message': "参数错误",
            'code': -1
        }


# 删除商品(私有api)
@app.route('/product/delete', methods=['POST'])
@login_required
def product_delete():
    data = request.get_json()
    try:
        id = data.get('id')
        product = ProductORM.Product.query.filter_by(id=id).first()
        if product:
            with app.app_context():
                history = HistoryORM.History(datetime.datetime.now(), product.id, product.name, current_user.id,
                                             'delete', 0)
                history.save()
                product = ProductORM.Product.query.filter_by(id=id).first()
                product.delete()
            return {
                'status': "success",
                'message': "删除成功",
                'code': 200
            }
        else:
            return {
                'status': "error",
                'message': "商品不存在",
                'code': 400
            }
    except Exception as e:
        return {
            'status': "error",
            'message': "参数错误",
            'code': -1
        }


# 入库(私有api)
@app.route('/product/in', methods=['POST'])
@login_required
def product_in():
    data = request.get_json()
    try:
        product = ProductORM.Product.query.filter_by(id=data['id']).first()
        if product:
            product.quantity += int(data['num'])
            product.save()
            history = HistoryORM.History(datetime.datetime.now(), data['id'], product.name, current_user.id, 'in',
                                         int(data['num']))
            history.save()
            return {
                'status': "success",
                'message': "入库成功",
                'code': 200
            }
        else:
            return {
                'status': "error",
                'message': "商品不存在",
                'code': 400
            }
    except Exception as e:
        print(e)
        return {
            'status': -1,
            'message': "error",
            'msg': str(e),
        }


# 出库(私有api)
@app.route('/product/out', methods=['POST'])
@login_required
def product_out():
    data = request.get_json()
    try:
        product = ProductORM.Product.query.filter_by(id=data['id']).first()
        if product:
            product.quantity -= int(data['num'])
            product.save()
            history = HistoryORM.History(time=datetime.datetime.now(), product_id=product.id, product_name=product.name,
                                         user_id=current_user.id, type="out", amount=int(data['num']))
            history.save()
            return {
                'status': "success",
                'message': "出库成功",
                'code': 200
            }
        else:
            return {
                'status': "error",
                'message': "商品不存在",
                'code': 400
            }
    except Exception as e:
        print(e)
        return {
            'status': -1,
            'message': "error",
            'msg': str(e),
        }


# 删除用户(私有api)
@app.route('/settings/user_managment/delete_user', methods=['POST'])
@login_required
def delete_user():
    data = request.get_json()
    try:
        user_id = data['id']

        # 禁止用户删除自己
        if current_user.id == user_id:
            return {
                'status': "error",
                'message': "不能删除当前登录用户",
                'code': 400
            }

        user = UsersORM.Users.query.filter_by(id=user_id).first()
        if user:
            # 先删除用户，再返回成功消息
            try:
                user.delete()
                return {
                    'status': "success",
                    'message': "删除成功",
                    'code': 200  # 修正状态码
                }
            except Exception as e:
                return {
                    'status': "error",
                    'message': "删除失败：" + str(e),
                    'code': 500
                }
        else:
            return {
                'status': "error",
                'message': "用户不存在",
                'code': 404
            }
    except Exception as e:
        print(e)
        return {
            'status': "error",
            'message': "参数错误",
            'msg': str(e),
            'code': 400
        }


# 新建用户(私有api)
@app.route('/settings/user_managment/new_user', methods=['POST'])
@login_required
def new_user():
    data = request.get_json()
    try:
        if data:
            if UsersORM.Users.query.filter_by(username=data['username']).first():
                return {
                    'status': "error",
                    'message': "用户已存在",
                    'code': 200
                }
            user = UsersORM.Users(username=data['username'], password=data['password'], type=data['type'])
            user.save()
            return {
                'status': "success",
                'message': "添加成功",
                'code': 400
            }
    except Exception as e:
        print(e)
        return {
            'status': "error",
            'message': "参数错误",
            'msg': str(e),
            'code': -1
        }


# 商品管理页的撤销操作
@app.route('/product/undo', methods=['POST'])
@login_required
def undo():
    if request.method == 'POST':
        # 查询历史记录数据库中最后一次的出库或者入库操作
        # 仅可以撤回该用户的操作
        history = HistoryORM.History.query.filter_by(user_id=current_user.id).order_by(
            HistoryORM.History.id.desc()).first()
        # 检查是否有历史记录
        if history is None:
            return {
                'code': -2
            }
        # 撤销库存
        product = ProductORM.Product.query.filter_by(id=history.product_id).first()
        # 检查历史记录为出库还是入库
        if history.type == 'out':
            product.quantity = product.quantity + history.amount
        else:
            product.quantity = product.quantity - history.amount
        product.update()
        # 删除该条记录
        history.delete()
        return {
            'code': 200,
            'status': 'success',
            'message': '撤销成功'
        }


# 用户修改用户名和密码
@app.route('/settings/profile/change', methods=['POST'])
@login_required
def change_user():
    data = request.get_json()
    print(data)
    try:
        # 利用id查询该用户的信息
        user = UsersORM.Users.query.filter_by(id=current_user.id).first()
        # 校验用户名或密码是否修改
        if data['username'] != user.username or data['password'] != user.password:
            # 修改用户名和密码
            user.username = data['username']
            user.password = data['password']
            user.save()
            return {
                'status': "success",
                'message': "修改成功",
                'code': 400
            }
        else:
            return {
                'status': "error",
                'message': "用户名或密码未修改",
                'code': 200
            }
    except Exception as e:
        print(e)
        return {
            'status': "error",
            'message': "参数错误",
            'msg': str(e),
            'code': -1
        }


# 手动备份
@app.route('/settings/auto_backup/manual_backup', methods=['POST'])
@login_required
def start_manual_backup():
    try:
        info = backup.manual_backup()
        msg = info
        print(msg)
        return {
            'status': "success",
            'message': "已执行命令",
            'code': 400
        }
    except Exception as e:
        print(e)
        return {
            'status': "error",
            'message': "内部错误",
            'code': -1
        }


# 启动定时备份
@app.route('/settings/auto_backup/enable', methods=['POST'])
@login_required
def start_auto_backup():
    try:
        # 检查是否启动
        import backup_config
        # 修改配置文件
        backup_config.AUTO_BACKUP = True
        info = backup.start_backup_thread()
        print(info)
        return {
            'status': "success",
            'message': "已执行命令",
            'code': 400
        }
    except Exception as e:
        print(e)
        return {
            'status': "error",
            'message': "内部错误",
            'code': -1
        }


# 关闭定时备份
@app.route('/settings/auto_backup/disable', methods=['POST'])
@login_required
def stop_auto_backup():
    try:
        import backup_config
        # 修改配置文件
        backup_config.AUTO_BACKUP = False
        info = backup.stop_backup_thread()
        print(info)
        return {
            'status': "success",
            'message': "已执行命令",
            'code': 400
        }
    except Exception as e:
        print(e)
        return {
            'status': "error",
            'message': "内部错误",
            'code': -1
        }


if __name__ == '__main__':
    app.run(port=config.PORT, host=config.HOST, debug=config.Debug)
