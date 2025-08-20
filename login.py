# 依赖: qrcode, requests
# 适用: 任何 Linux 环境
# 用法: python3 login.py <账号别名>
# 例如: python3 login.py my_account_1

import requests
import time
import json
import os
import sys
import qrcode  # 导入 qrcode 库
from typing import List, Dict

CONFIG_PATH = "xiaomiconfig.json"

class XiaomiAccount:
    def __init__(self, us, user_id=None, pass_token=None, security_token=None):
        self.us = us.strip()
        self.user_id = user_id
        self.pass_token = pass_token
        self.security_token = security_token

    @staticmethod
    def load_accounts() -> List[Dict]:
        """加载账号配置"""
        if not os.path.isfile(CONFIG_PATH):
            return []
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON格式错误: {e.msg}，请检查 {CONFIG_PATH} 文件。")
            return []
        except Exception as e:
            print(f"❌ 读取配置文件时发生未知错误: {str(e)}")
            return []

    @classmethod
    def from_json(cls, us):
        accounts = cls.load_accounts()
        for acc in accounts:
            if acc.get("data", {}).get("us") == us.strip():
                data = acc.get("data", {})
                return cls(
                    us=data.get("us"),
                    user_id=data.get("userId"),
                    pass_token=data.get("passToken"),
                    security_token=data.get("securityToken")
                )
        return None

    def save_to_json(self):
        """更新或添加账号数据到 xiaomiconfig.json"""
        accounts = self.load_accounts()
        updated = False
        for acc in accounts:
            if acc.get("data", {}).get("us") == self.us:
                acc["data"].update({
                    "us": self.us,
                    "userId": str(self.user_id) if self.user_id else None,
                    "passToken": self.pass_token,
                    "securityToken": self.security_token
                })
                updated = True
                break
        
        if not updated:
            new_account = {
                "data": {
                    "us": self.us,
                    "userId": str(self.user_id) if self.user_id else None,
                    "passToken": self.pass_token,
                    "securityToken": self.security_token
                }
            }
            accounts.append(new_account)
            
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=4, ensure_ascii=False)
            print(f"✅ 账号 '{self.us}' 数据已成功保存至 {CONFIG_PATH}！")
            return True
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return False

    def login(self):
        """处理单个账号的扫码登录"""
        print(f"\n======== 开始为账号 '{self.us}' 进行扫码登录 ========")
        
        login_data = self.get_login_qr()
        if not login_data or login_data.get("code") != 0:
            print("❌ 获取二维码失败，请检查网络或稍后再试。")
            return

        self.log_show_qr(login_data)

    def get_login_qr(self):
        """获取登录二维码信息"""
        url = "https://account.xiaomi.com/longPolling/loginUrl"
        querystring = {
            "_group": "DEFAULT", "_qrsize": "240", "qs": "?callback=https%3A%2F%2Faccount.xiaomi.com%2Fsts%3Fsign%3DZvAtJIzsDsFe60LdaPa76nNNP58%253D%26followup%3Dhttps%253A%252F%252Faccount.xiaomi.com%252Fpass%252Fauth%252Fsecurity%252Fhome%26sid%3Dpassport&sid=passport&_group=DEFAULT",
            "bizDeviceType": "", "callback": "https://account.xiaomi.com/sts?sign=ZvAtJIzsDsFe60LdaPa76nNNP58=&followup=https://account.xiaomi.com/pass/auth/security/home&sid=passport",
            "_hasLogo": "false", "theme": "", "sid": "passport", "needTheme": "false", "showActiveX": "false", "serviceParam": "{\"checkSafePhone\":false,\"checkSafeAddress\":false,\"lsrp_score\":0.0}",
            "_locale": "zh_CN", "_sign": "2&V1_passport&BUcblfwZ4tX84axhVUaw8t6yi2E=", "_dc": str(int(time.time() * 1000))
        }
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            response_text = response.text
            if "&&&START&&&" in response_text:
                return json.loads(response_text.split("&&&START&&&", 1)[-1].strip())
            return response.json()
        except requests.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            return None
        except json.JSONDecodeError:
            print("❌ 解析服务器响应失败。")
            return None

    def log_show_qr(self, login_data):
        qr_url = login_data.get("qr")
        if not qr_url:
            print("❌ 未能从响应中获取二维码URL。")
            return
            
        print("📱 请使用小米手机APP扫描下方二维码登录：")
        qr = qrcode.QRCode(border=1)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr.print_tty()
        
        print(f"如果二维码显示不正常，也可浏览器打开此链接: {qr_url}")
        
        lp_url = login_data.get("lp")
        timeout = login_data.get("timeout", 300)
        login_result = self.check_login_status(lp_url, timeout)
        
        if login_result:
            print("\n🎉 登录成功! 获取到以下凭证:")
            print(f"  - 小米 User ID: {login_result['user_id']}")
            self.user_id = login_result["user_id"]
            self.security_token = login_result["security_token"]
            self.pass_token = login_result["pass_token"]
            self.save_to_json()
        else:
            print("\n❌ 登录失败或超时。")

    def check_login_status(self, lp_url, timeout=300):
        """检查登录状态并显示倒计时"""
        start_time = time.time()
        end_time = start_time + timeout
        
        status_messages = { 700: "等待扫码", 701: "已扫码, 请在手机上确认", 702: "二维码已过期", 0: "登录成功" }
        last_status_msg = ""

        while time.time() < end_time:
            remaining = int(end_time - time.time())
            print(f"\r⏳ 二维码有效时间剩余 {remaining} 秒... 正在检查扫码状态...", end="", flush=True)
            
            try:
                # <<< 修改点 1: 大幅增加超时时间，从5秒增加到60秒 >>>
                # 这给予服务器足够的时间来响应长轮询请求
                response = requests.get(lp_url, timeout=60)
                response_text = response.text
                if "&&&START&&&" in response_text:
                    response_text = response_text.split("&&&START&&&", 1)[-1].strip()
                result = json.loads(response_text)
                
                status_code = result.get("code", -1)
                status_msg = status_messages.get(status_code, f"未知状态: {status_code}")
                
                # <<< 修改点 2: 仅在状态变化时打印新行，避免刷屏 >>>
                if status_msg != last_status_msg:
                    print(f"\nℹ️  状态更新: {status_msg}")
                    last_status_msg = status_msg

                if status_code == 0:
                    return {
                        "user_id": result.get("userId"),
                        "security_token": result.get("ssecurity"),
                        "pass_token": result.get("passToken")
                    }
                if status_code == 702:
                    return None
                    
            # <<< 修改点 3: 更精细的异常处理 >>>
            except requests.exceptions.Timeout:
                # 这个超时是客户端设置的60秒超时，说明服务器一直没响应，是正常的，继续轮询
                print("\r⏳ 二维码有效时间剩余 {remaining} 秒... 等待扫码中...      ", end="", flush=True)
                continue # 继续下一次循环
            except requests.exceptions.RequestException as e:
                # 其他网络问题，例如DNS解析失败，连接被拒绝等
                print(f"\n❌ 网络连接错误: {e}，将在3秒后重试...")
                time.sleep(3)
                continue
            except KeyboardInterrupt:
                print("\n🚫 用户手动中断登录。")
                return None
            except Exception as e:
                print(f"\n❌ 检查登录状态时发生未知错误: {e}")
                time.sleep(3) # 发生未知错误时，稍等一下再重试

        print("\n⌛ 二维码已过期。")
        return None

def main():
    """主执行函数"""
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("❌ 错误: 必须提供一个账号别名。")
        print("用法: python3 login.py <你的账号别名>")
        print("例如: python3 login.py zhangsan")
        return

    us = sys.argv[1].strip()
    print(f"本次操作的账号别名为: '{us}'")
    
    account = XiaomiAccount.from_json(us)
    if account and account.pass_token:
        choice = input(f"ℹ️  账号 '{us}' 已存在，是否要覆盖并重新登录? (y/N): ").lower()
        if choice != 'y':
            print("🚫 已取消操作。")
            return
            
    if not account:
        account = XiaomiAccount(us)
        
    account.login()

if __name__ == "__main__":
    main()