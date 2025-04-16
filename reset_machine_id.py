import os
import sys
import json
import uuid
import hashlib
import sqlite3
import shutil
import tempfile
import configparser
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, NoReturn
from dataclasses import dataclass

# 内置配置
DEFAULT_CONFIG = """
[WindowsPaths]
storage_path = %APPDATA%\\Cursor\\User\\globalStorage\\storage.json
sqlite_path = %APPDATA%\\Cursor\\User\\globalStorage\\state.vscdb
cursor_path = %LOCALAPPDATA%\\Programs\\Cursor\\resources\\app

[MacPaths]
storage_path = ~/Library/Application Support/Cursor/User/globalStorage/storage.json
sqlite_path = ~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
cursor_path = /Applications/Cursor.app/Contents/Resources/app

[LinuxPaths]
storage_path = ~/.config/cursor/User/globalStorage/storage.json
sqlite_path = ~/.config/cursor/User/globalStorage/state.vscdb
cursor_path = /usr/share/cursor/resources/app
"""

@dataclass
class SystemPaths:
    """系统路径配置类"""
    storage_path: str
    sqlite_path: str
    cursor_path: str

class ConfigManager:
    """配置管理类"""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self._load_default_config()

    def _load_default_config(self) -> None:
        """加载默认配置"""
        self.config.read_string(DEFAULT_CONFIG)

    def get_system_paths(self) -> SystemPaths:
        """获取系统路径配置"""
        if sys.platform == "win32":
            section = 'WindowsPaths'
        elif sys.platform == "darwin":
            section = 'MacPaths'
        elif sys.platform == "linux":
            section = 'LinuxPaths'
        else:
            raise NotImplementedError(f"不支持的操作系统: {sys.platform}")

        return SystemPaths(
            storage_path=os.path.expandvars(os.path.expanduser(self.config.get(section, 'storage_path'))),
            sqlite_path=os.path.expandvars(os.path.expanduser(self.config.get(section, 'sqlite_path'))),
            cursor_path=os.path.expandvars(os.path.expanduser(self.config.get(section, 'cursor_path')))
        )

class ProcessManager:
    """进程管理类"""
    @staticmethod
    def is_cursor_running() -> bool:
        """检查Cursor是否正在运行"""
        try:
            if sys.platform == "win32":
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq cursor.exe"], 
                                      capture_output=True, text=True)
                return "cursor.exe" in result.stdout
            else:
                cmd = "pgrep -f cursor" if sys.platform == "linux" else "pgrep -f Cursor"
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                return bool(result.stdout.strip())
        except Exception:
            return False

    @staticmethod
    def terminate_cursor() -> None:
        """终止Cursor进程"""
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/IM", "cursor.exe"], check=False)
            else:
                cmd = "pkill -f cursor" if sys.platform == "linux" else "pkill -f Cursor"
                subprocess.run(cmd.split(), check=False)
        except Exception as e:
            print(f"终止进程时出错: {str(e)}")

class IDGenerator:
    """ID生成器类"""
    @staticmethod
    def generate_new_ids() -> Dict[str, str]:
        """生成新的机器ID"""
        dev_device_id = str(uuid.uuid4())
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
            "storage.serviceMachineId": dev_device_id,
        }

class DatabaseManager:
    """数据库管理类"""
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path

    def update_ids(self, new_ids: Dict[str, str]) -> bool:
        """更新SQLite数据库中的机器ID"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            for key, value in new_ids.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO ItemTable (key, value) 
                    VALUES (?, ?)
                """, (key, value))

            conn.commit()
            return True
        except Exception as e:
            print(f"SQLite数据库更新失败: {str(e)}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

class StorageManager:
    """存储管理类"""
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """确保存储文件存在"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def backup_and_update(self, new_ids: Dict[str, str]) -> bool:
        """备份并更新存储文件"""
        try:
            # 创建备份
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.storage_path}.bak.{timestamp}"
            shutil.copy2(self.storage_path, backup_path)

            # 读取并更新配置
            with open(self.storage_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config.update(new_ids)

            # 保存新配置
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"存储文件更新失败: {str(e)}")
            return False

class MachineIDResetter:
    """机器ID重置主类"""
    def __init__(self):
        self.config_manager = ConfigManager()
        self.paths = self.config_manager.get_system_paths()
        self.process_manager = ProcessManager()
        self.id_generator = IDGenerator()
        self.db_manager = DatabaseManager(self.paths.sqlite_path)
        self.storage_manager = StorageManager(self.paths.storage_path)

    def logout_cursor(self) -> None:
        """注销Cursor账号"""
        print("\n第一步：注销Cursor账号")
        print("1. 打开Cursor")
        print("2. 点击左下角的账号图标")
        print("3. 选择'Sign Out'或'登出'")
        print("4. 确认登出")
        print("\n注意：")
        print("- 请确保完全登出账号，不要只是关闭窗口")
        print("- 登出后，您的账号将被注销")
        print("- 所有本地设置将被保留")
        input("\n完成上述步骤后，按回车键继续...")

    def exit_cursor(self) -> None:
        """优雅地退出Cursor程序"""
        print("\n第二步：退出Cursor程序")
        print("正在检查Cursor进程...")
        
        if self.process_manager.is_cursor_running():
            print("发现正在运行的Cursor进程，正在尝试优雅关闭...")
            print("请在10秒内保存您的工作...")
            time.sleep(10)
            
            self.process_manager.terminate_cursor()
            time.sleep(2)
            
            if self.process_manager.is_cursor_running():
                print("Cursor进程仍在运行，请手动关闭")
        
        input("\n确保Cursor已完全关闭后，按回车键继续...")

    def reset_machine_ids(self) -> bool:
        """重置机器ID"""
        print("\n第三步：重置机器ID")
        print("正在检查配置...")

        if not self.storage_manager.storage_path.exists():
            print(f"找不到配置文件: {self.storage_manager.storage_path}")
            return False

        if not os.access(self.storage_manager.storage_path, os.R_OK | os.W_OK):
            print("没有读写配置文件的权限")
            return False

        print("正在生成新的机器ID...")
        new_ids = self.id_generator.generate_new_ids()

        # 更新存储文件
        if not self.storage_manager.backup_and_update(new_ids):
            return False

        # 更新数据库
        if not self.db_manager.update_ids(new_ids):
            return False

        print("机器ID重置成功！")
        print("\n新的机器ID:")
        for key, value in new_ids.items():
            print(f"{key}: {value}")
        return True

    def show_login_instructions(self) -> None:
        """显示重新注册和登录的说明"""
        print("\n第四步：重新注册和登录Cursor")
        print("1. 访问Cursor官网 (https://cursor.sh)")
        print("2. 点击右上角头像，选择'Sign Out'注销账号")
        print("3. 点击'Sign Up'注册新账号")
        print("4. 选择注册方式：")
        print("   - Google账号（推荐）")
        print("   - GitHub账号")
        print("5. 完成注册后，打开Cursor客户端")
        print("6. 点击左下角的账号图标")
        print("7. 选择'Sign In'或'登录'")
        print("8. 使用新注册的账号登录")
        input("\n完成上述步骤后，按回车键退出程序...")

def main() -> None:
    try:
        print("\n" + "="*50)
        print("Cursor 机器ID重置工具")
        print("="*50)
        print("本工具将帮助您重置Cursor的机器ID")
        print("请按照以下步骤操作：")

        resetter = MachineIDResetter()
        resetter.logout_cursor()
        resetter.exit_cursor()
        
        if resetter.reset_machine_ids():
            resetter.show_login_instructions()
        else:
            print("\n重置过程失败，请检查错误信息并重试。")

    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
