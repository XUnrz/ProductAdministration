import os,shutil,threading,time,schedule,datetime,config
from flask import current_app

# 创建备份目录
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_database():
    """备份数据库文件"""
    try:
        # 获取当前时间戳
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # SQLite数据库文件路径
        db_uri = config.SQLALCHEMY_DATABASE_URI
        if db_uri.startswith('sqlite:///'):
            db_path = 'instance/'+db_uri.replace('sqlite:///', '')
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
            
            # 如果数据库文件不存在于instance目录下，则使用config中的DB变量
            if not os.path.exists(db_path) and hasattr(config, 'DB'):
                db_path = config.DB
        else:
            return "不支持的数据库类型"
        
        if os.path.exists(db_path):
            # 创建备份文件名
            backup_filename = f"backup_{timestamp}.db"
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            
            # 复制数据库文件到备份目录
            shutil.copy2(db_path, backup_path)
            
            # 保留最近7天的备份
            cleanup_old_backups()
            
            return f"数据库备份成功: {backup_filename}" 
        else:
            return "数据库文件不存在，无法备份"
    except Exception as e:
        return f"数据库备份失败: {str(e)}"

def cleanup_old_backups():
    """清理7天前的备份文件"""
    try:
        # 获取7天前的时间戳
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        
        # 遍历备份目录中的文件
        for filename in os.listdir(BACKUP_DIR):
            file_path = os.path.join(BACKUP_DIR, filename)
            if os.path.isfile(file_path):
                # 检查文件修改时间
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    print(f"已删除旧备份文件: {filename}")
    except Exception as e:
        print(f"清理旧备份文件失败: {str(e)}")

def run_backup_scheduler():
    """运行备份调度器"""
    # 每天凌晨2点执行备份
    schedule.every().day.at("02:00").do(backup_database)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

# 手动备份
def manual_backup():
    return backup_database()

def start_backup_thread():
    # 启动备份调度线程
    # 检查自动备份状态
    try:
        import backup_config
        if backup_config.AUTO_BACKUP:
            backup_thread = threading.Thread(target=run_backup_scheduler, daemon=True)
            backup_thread.start()
            return "备份已启动"
        else:
            return "自动备份已禁用"
    except Exception as e:
        return f"启动备份失败: {str(e)}"
    
def stop_backup_thread():
    # 停止备份调度线程
    try:
        import backup_config
        backup_config.AUTO_BACKUP = False
        return "备份已停止"
    except Exception as e:
        return f"停止备份失败: {str(e)}"