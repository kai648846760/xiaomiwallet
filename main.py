# main.py

"""
小米钱包每日任务主执行脚本 (最终 Bug 修复版)。

本脚本基于用户提供的有效版本进行代码风格和结构的规范化重构，
并修复了因 URL 清理、会话管理不当以及 API 参数遗漏导致的 Bug。
核心业务逻辑、API URL 及参数与原始有效版本保持完全一致，
以确保功能的稳定性和兼容性。

功能：
1. 读取 `xiaomiconfig.json` 中的所有账号配置。
2. 为每个账号获取临时 Cookie。
3. 严格按照原始逻辑，自动完成小米钱包的每日浏览任务。
4. 将执行结果日志回写到配置文件中。
5. （可选）如果配置了飞书 Webhook，则发送执行结果通知。
"""

import json
import os
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
import urllib3

# --- 全局常量 ---
CONFIG_FILE = "xiaomiconfig.json"
API_HOST = "m.jr.airstarfinance.net"

# 任务接口使用的移动端 User-Agent
USER_AGENT_MOBILE = (
    'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001; '
    'AppBundle/com.mipay.wallet; AppVersionName/6.89.1.5275.2323; AppVersionCode/20577595; '
    'MiuiVersion/stable-V816.0.13.0.UMNCNXM; DeviceId/alioth; NetworkType/WIFI; '
    'mix_version; WebViewVersion/118.0.0.0) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Version/4.0 Mobile Safari/5.36 XiaoMi/MiuiBrowser/4.3'
)
# 获取 Cookie 时使用的桌面端 User-Agent (与原始版本保持一致)
USER_AGENT_DESKTOP = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
)


# 禁用 HTTPS InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- 辅助功能模块 ---

def send_feishu_notification(webhook_url: str, message: str) -> None:
    """通过指定的飞书 Webhook URL 发送文本消息。"""
    if not webhook_url:
        return

    headers = {'Content-Type': 'application/json'}
    payload = {"msg_type": "text", "content": {"text": message}}

    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("StatusCode") == 0:
            print("  ✅ 飞书通知已成功发送。")
        else:
            error_msg = response_json.get('StatusMessage', '未知错误')
            print(f"  ⚠️ 飞书通知发送失败，响应: {error_msg}")
    except requests.RequestException as e:
        print(f"  ❌ 发送飞书通知时发生网络错误: {e}")
    except Exception as e:
        print(f"  ❌ 发送飞书通知时发生未知错误: {e}")


def generate_notification(account_id: str, rnl_instance: 'RNL', us: str) -> str:
    """根据任务执行结果生成格式化的日志/通知消息。"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    msg = (
        f"【小米钱包每日任务报告】\n"
        f"✨ 账号别名：{us}\n"
        f"✨ 小米ID：{account_id}\n"
        f"📊 当前可兑换视频天数：{rnl_instance.total_days}\n\n"
        f"📅 {current_date} 任务记录\n"
        f"{"-" * 25}"
    )

    if not rnl_instance.today_records:
        msg += "\n  今日暂无新增奖励记录"
    else:
        for record in rnl_instance.today_records:
            record_time = record.get("createTime", "未知时间")
            value = record.get("value", 0)
            days = int(value) / 100
            msg += f"\n| ⏰ {record_time}\n| 🎁 领到视频会员，+{days:.2f}天"

    if rnl_instance.error_info:
        msg += f"\n\n⚠️ 执行异常：{rnl_instance.error_info}"

    msg += f"\n{"=" * 25}"
    return msg


# --- 核心业务逻辑模块 ---

class ApiRequest:
    """封装 API 请求，统一管理会话、Cookie 和请求头。"""
    def __init__(self, cookies: Union[str, Dict[str, str]]):
        self.session = requests.Session()
        self.base_headers = {'Host': API_HOST, 'User-Agent': USER_AGENT_MOBILE}
        self.update_cookies(cookies)

    @staticmethod
    def _parse_cookies(cookies_str: str) -> Dict[str, str]:
        """将 Cookie 字符串解析为字典。"""
        return {
            k.strip(): v for k, v in
            (item.split('=', 1) for item in cookies_str.split(';') if '=' in item)
        }

    def update_cookies(self, cookies: Union[str, Dict[str, str]]) -> None:
        """更新会话中的 Cookie。"""
        if not cookies:
            return
        dict_cookies = self._parse_cookies(cookies) if isinstance(cookies, str) else cookies
        self.session.cookies.update(dict_cookies)
        self.base_headers['Cookie'] = '; '.join([f"{k}={v}" for k, v in dict_cookies.items()])

    def request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发送一个 HTTP 请求。"""
        headers = {**self.base_headers, **kwargs.pop('headers', {})}
        try:
            resp = self.session.request(method.upper(), url, verify=False, headers=headers, timeout=15, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            # 这里的 error_info 是 RNL 类的属性，不应在此处设置
            print(f"  [Request Error] {e}")
            return None
        except (json.JSONDecodeError, AttributeError):
            print(f"  [JSON Parse Error] 无法解析服务器响应: {getattr(resp, 'text', 'No Response Text')[:100]}")
            return None

    def get(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发送 GET 请求。"""
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发送 POST 请求。"""
        return self.request('POST', url, **kwargs)


class RNL:
    """
    封装小米钱包任务的具体业务逻辑。
    所有方法的行为和逻辑均与原始有效版本保持一致。
    """
    def __init__(self, api_request: ApiRequest):
        self.api = api_request
        self.activity_code = '2211-videoWelfare'
        self.t_id: Optional[str] = None
        self.total_days: str = "未知"
        self.today_records: List[Dict[str, Any]] = []
        self.error_info: str = ""

    def get_task_list(self) -> Optional[List[Dict[str, Any]]]:
        """获取任务列表。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/getTaskList"
        try:
            response = self.api.post(url, data={'activityCode': self.activity_code})
            if response and response.get('code') == 0:
                target_tasks = [
                    task for task in response['value']['taskInfoList']
                    if '浏览组浏览任务' in task.get('taskName', '')
                ]
                return target_tasks
            self.error_info = f"获取任务列表失败：{response}"
            return None
        except Exception as e:
            self.error_info = f'获取任务列表时发生异常：{e}'
            return None

    def get_task(self, task_code: str) -> Optional[str]:
        """通过 taskCode 获取 userTaskId。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/getTask"
        # ▼▼▼ 核心 Bug 修复：恢复 'jrairstar_ph' 魔法参数 ▼▼▼
        data = {
            'activityCode': self.activity_code,
            'taskCode': task_code,
            'jrairstar_ph': '98lj8puDf9Tu/WwcyMpVyQ=='
        }
        # ▲▲▲ 核心 Bug 修复 ▲▲▲
        try:
            response = self.api.post(url, data=data)
            if response and response.get('code') == 0:
                return response['value']['taskInfo']['userTaskId']
            self.error_info = f'获取任务信息失败：{response}'
            return None
        except Exception as e:
            self.error_info = f'获取任务信息时发生异常：{e}'
            return None

    def complete_task(self, task_id: str, t_id: str, brows_click_url_id: str) -> Optional[str]:
        """完成浏览任务。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/completeTask"
        # ▼▼▼ 核心 Bug 修复：恢复所有必要的 URL 参数 ▼▼▼
        params = {
            'activityCode': self.activity_code,
            'app': 'com.mipay.wallet',
            'isNfcPhone': 'true',
            'channel': 'mipay_indexicon_TVcard',
            'deviceType': '2',
            'system': '1',
            'visitEnvironment': '2',
            'userExtra': '{"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}',
            'taskId': task_id,
            'browsTaskId': t_id,
            'browsClickUrlId': brows_click_url_id,
            'clickEntryType': 'undefined',
            'festivalStatus': '0'
        }
        # ▲▲▲ 核心 Bug 修复 ▲▲▲
        try:
            response = self.api.get(url, params=params)
            if response and response.get('code') == 0:
                return response.get('value')
            self.error_info = f'完成任务失败：{response}'
            return None
        except Exception as e:
            self.error_info = f'完成任务时发生异常：{e}'
            return None

    def receive_award(self, user_task_id: str) -> None:
        """领取奖励。"""
        url = f"https://{API_HOST}/mp/api/generalActivity/luckDraw"
        # 恢复所有必要的 URL 参数
        params = {
            'activityCode': self.activity_code,
            'userTaskId': user_task_id,
            'app': 'com.mipay.wallet',
            'isNfcPhone': 'true',
            'channel': 'mipay_indexicon_TVcard',
            'deviceType': '2',
            'system': '1',
            'visitEnvironment': '2',
            'userExtra': '{"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}',
        }
        try:
            response = self.api.get(url, params=params)
            if response and response.get('code') != 0:
                self.error_info = f'领取奖励失败：{response}'
        except Exception as e:
            self.error_info = f'领取奖励时发生异常：{e}'

    def query_user_info_and_records(self) -> bool:
        """查询用户总奖励和今日记录。"""
        base_url = f"https://{API_HOST}/mp/api/generalActivity/"
        params = {
            'activityCode': self.activity_code,
            'app': 'com.mipay.wallet',
            'deviceType': '2',
            'system': '1',
            'visitEnvironment': '2',
            'userExtra': '{"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}'
        }
        try:
            total_res = self.api.get(f"{base_url}queryUserGoldRichSum", params=params)
            if not total_res or total_res.get('code') != 0:
                self.error_info = f'获取兑换视频天数失败：{total_res}'
                return False
            self.total_days = f"{int(total_res.get('value', 0)) / 100:.2f}天"

            record_params = {**params, 'pageNum': 1, 'pageSize': 20}
            record_res = self.api.get(f"{base_url}queryUserJoinList", params=record_params)
            if not record_res or record_res.get('code') != 0:
                self.error_info = f'查询任务完成记录失败：{record_res}'
                return False

            self.today_records = []
            current_date = datetime.now().strftime("%Y-%m-%d")
            for item in record_res.get('value', {}).get('data', []):
                if item.get('createTime', '').startswith(current_date):
                    self.today_records.append(item)
            return True
        except Exception as e:
            self.error_info = f'获取任务记录时发生异常：{e}'
            return False

    def run_main_workflow(self) -> bool:
        """执行任务的主流程，逻辑与原始有效版本完全一致。"""
        if not self.query_user_info_and_records():
            return False
        
        for i in range(2):
            print(f"  - 开始第 {i + 1} 轮任务...")
            tasks = self.get_task_list()
            if not tasks:
                print("  - 未找到可执行的任务列表，可能今日任务已完成。")
                break
            
            task = tasks[0]
            try:
                self.t_id = task['generalActivityUrlInfo']['id']
            except (KeyError, TypeError):
                pass
            
            if not self.t_id:
                print("  - 无法获取任务 t_id，中断执行。")
                return False

            task_id = task['taskId']
            task_code = task['taskCode']
            brows_click_url_id_from_api = task['generalActivityUrlInfo']['browsClickUrlId']

            time.sleep(random.randint(10, 15))

            user_task_id = self.complete_task(
                task_id=task_id,
                t_id=self.t_id,
                brows_click_url_id=brows_click_url_id_from_api
            )

            time.sleep(random.randint(2, 4))

            if not user_task_id:
                user_task_id = self.get_task(task_code=task_code)
                time.sleep(random.randint(2, 4))
            
            if user_task_id:
                self.receive_award(user_task_id=user_task_id)
            else:
                print("  - 未能获取 user_task_id，无法领取本轮奖励。")

            time.sleep(random.randint(2, 4))
        
        print("  - 所有任务轮次执行完毕，正在刷新最终数据...")
        self.query_user_info_and_records()
        return True


# --- 主流程控制模块 ---

def get_session_cookies(pass_token: str, user_id: str) -> Optional[str]:
    """
    使用长效凭证 (passToken) 获取用于访问任务 API 的临时会话 Cookie。
    此函数的核心 URL 和 Headers 严格与原始有效版本保持一致。
    """
    login_url = (
        'https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts'
        '%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net'
        '%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse'
        '%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity'
        '%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue'
        '%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q'
        '%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket'
    )
    
    headers = {
        'user-agent': USER_AGENT_DESKTOP,
        'cookie': f'passToken={pass_token}; userId={user_id};'
    }
    
    session = requests.Session()
    try:
        session.get(url=login_url, headers=headers, verify=False, timeout=10)
        cookies = session.cookies.get_dict()
        
        c_user_id = cookies.get('cUserId')
        service_token = cookies.get('serviceToken')

        if c_user_id and service_token:
            return f"cUserId={c_user_id}; jrairstar_serviceToken={service_token}"
        
        print("  - 获取的 Cookie 不完整，可能 passToken 已失效。")
        return None
    except requests.RequestException as e:
        print(f"  - 获取 Cookie 时网络请求失败: {e}")
        return None


def process_account(account_data: Dict[str, Any]) -> str:
    """处理单个账号的完整任务流程。"""
    us = account_data.get('us')
    user_id = account_data.get('userId')
    pass_token = account_data.get('passToken')
    
    if not all([us, user_id, pass_token]):
        return f"账号 '{us or '未知'}' 配置不完整，已跳过。"
    
    print(f"\n>>>>>>>>>> 正在处理账号: {us} (ID: {user_id}) <<<<<<<<<<")
    
    session_cookies = get_session_cookies(pass_token, user_id)
    api_request = ApiRequest(session_cookies)
    rnl = RNL(api_request)
    
    if not session_cookies:
        rnl.error_info = "获取会话 Cookie 失败，请重新运行 login.py 刷新凭证。"
    else:
        print("  - 会话 Cookie 获取成功。")
        try:
            rnl.run_main_workflow()
        except Exception as e:
            rnl.error_info = f"执行主程序时发生未知异常: {e}"
            print(f"  ❌ {rnl.error_info}")
            
    return generate_notification(user_id, rnl, us)


def main():
    """程序主入口函数。"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            accounts_config = [] if not content else json.loads(content)
        assert isinstance(accounts_config, list), "配置文件根节点应为列表"
    except (FileNotFoundError, json.JSONDecodeError, AssertionError) as e:
        print(f"❌ 读取或解析配置文件 '{CONFIG_FILE}' 失败: {e}")
        return

    if not accounts_config:
        print(f"ℹ️  配置文件 '{CONFIG_FILE}' 中没有账号，程序退出。")
        return


    print(f"\n======= 开始执行小米钱包每日任务 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) =======")
    
    updated_config = []
    
    for account in accounts_config:
        data = account.get('data', {})
        notification = process_account(data)
        print(notification)
        
        data['log'] = notification.strip()
        account['data'] = data
        updated_config.append(account)
        
        feishu_webhook = data.get('feishu_webhook')
        if feishu_webhook:
            print("  - 检测到飞书 Webhook 配置，正在尝试推送...")
            send_feishu_notification(feishu_webhook, notification)
        delay = random.randint(0, 15)
        print(f"随机延迟 {delay} 秒后执行，以避免集中请求...")
        time.sleep(delay)

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_config, f, indent=4, ensure_ascii=False)
        print(f"\n✅ 所有账号日志已成功更新至 '{CONFIG_FILE}'")
    except Exception as e:
        print(f"❌ 写入日志到 '{CONFIG_FILE}' 时发生错误: {e}")

    print("\n======= 小米钱包每日任务执行完毕 =======")


if __name__ == "__main__":
    main()