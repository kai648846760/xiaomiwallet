# 用法:
# python3 manage.py list         # 查看所有账号
# python3 manage.py delete <别名> # 删除指定账号

import json
import sys
import os

CONFIG_PATH = "xiaomiconfig.json"

def load_accounts():
    """加载账号配置"""
    if not os.path.isfile(CONFIG_PATH):
        return []
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None

def save_accounts(accounts):
    """保存账号配置"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return False

def list_accounts():
    """列出所有账号"""
    accounts = load_accounts()
    if accounts is None: return

    if not accounts:
        print("ℹ️  当前没有任何账号。")
        return

    print(f"======== 共找到 {len(accounts)} 个账号 ========")
    for i, acc in enumerate(accounts):
        data = acc.get("data", {})
        us = data.get("us", "N/A")
        user_id = data.get("userId", "未登录")
        print(f"{i+1}. 别名: {us}, 小米ID: {user_id}")
    print("=" * 30)

def delete_account(us_to_delete):
    """根据别名删除账号"""
    accounts = load_accounts()
    if accounts is None: return

    new_accounts = []
    deleted = False
    for acc in accounts:
        if acc.get("data", {}).get("us") == us_to_delete:
            deleted = True
            continue # 跳过这个账号，不添加到新列表里
        new_accounts.append(acc)

    if deleted:
        if save_accounts(new_accounts):
            print(f"✅ 已成功删除账号 '{us_to_delete}'。")
    else:
        print(f"❌ 未找到别名为 '{us_to_delete}' 的账号。")

def print_usage():
    print("用法:")
    print("  python3 manage.py list         - 查看所有已添加的账号")
    print("  python3 manage.py delete <别名> - 删除一个指定的账号")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "list":
        list_accounts()
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ 错误: 'delete' 命令需要一个账号别名参数。")
            print_usage()
            return
        us_to_delete = sys.argv[2]
        delete_account(us_to_delete)
    else:
        print(f"❌ 未知命令: '{command}'")
        print_usage()

if __name__ == "__main__":
    main()