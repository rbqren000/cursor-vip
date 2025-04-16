# Cursor 机器ID重置工具

一个简单易用的工具，帮助您重置 Cursor IDE 的机器ID，支持 Windows、macOS 和 Linux。

## 🚀 快速开始

1. 确保已安装 Python 3.6+
2. 下载 Cursor IDE：
   - [Linux (.deb)](https://github.com/adysec/cursor/releases/latest) - 支持 Ubuntu 24.04 AMD64
   - [Windows](https://cursor.com)
   - [macOS](https://cursor.com)
3. 运行重置工具：
   ```bash
   python reset_machine_id.py
   ```
4. 按照提示完成操作

## ✨ 特性

- ✅ 全平台支持（Windows/macOS/Linux）
- 🔒 自动备份原始配置
- 🛡️ 安全的数据处理
- 📦 零依赖，开箱即用
- 📝 详细的操作指引

## 📋 使用步骤

1. **注销账号**
   - 打开 Cursor
   - 点击左下角账号图标
   - 选择"Sign Out"或"登出"

2. **退出程序**
   - 确保 Cursor 完全退出
   - 程序会自动检查并关闭进程

3. **重置ID**
   - 程序自动生成新ID
   - 备份原始配置
   - 更新必要文件

4. **重新登录**
   - 访问 [Cursor官网](https://cursor.com)
   - 注册新账号
   - 使用新账号登录

## ⚠️ 注意事项

- 运行前请确保 Cursor 已完全退出
- 建议提前备份重要数据
- 如遇权限问题，请使用管理员/root权限运行

## 🔧 技术说明

### 默认配置路径

<details>
<summary>Windows</summary>

```ini
storage_path = %APPDATA%\Cursor\User\globalStorage\storage.json
sqlite_path = %APPDATA%\Cursor\User\globalStorage\state.vscdb
cursor_path = %LOCALAPPDATA%\Programs\Cursor\resources\app
```
</details>

<details>
<summary>macOS</summary>

```ini
storage_path = ~/Library/Application Support/Cursor/User/globalStorage/storage.json
sqlite_path = ~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
cursor_path = /Applications/Cursor.app/Contents/Resources/app
```
</details>

<details>
<summary>Linux</summary>

```ini
storage_path = ~/.config/cursor/User/globalStorage/storage.json
sqlite_path = ~/.config/cursor/User/globalStorage/state.vscdb
cursor_path = /usr/share/cursor/resources/app
```
</details>

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。 
