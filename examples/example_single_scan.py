# -*- coding: utf-8 -*-
"""
此示例演示了如何使用 acunetix_sdk 添加单个网站，
使用全量规则进行扫描，等待扫描结果，并最终获取结果。
"""
import os
import time
from acunetix_sdk import AcunetixClient
from acunetix_sdk.models import Target, Scan

# Acunetix API 连接信息
# 请替换为您的实际 Acunetix API URL 和 API Key
# 建议从环境变量或安全配置文件中读取这些敏感信息
ACUNETIX_URL = os.environ.get("ACUNETIX_URL", "YOUR_ACUNETIX_API_URL")
ACUNETIX_API_KEY = os.environ.get("ACUNETIX_API_KEY", "YOUR_ACUNETIX_API_KEY")

# 要扫描的目标网站信息
TARGET_URL = "http://testphp.vulnweb.com"  # 请替换为要扫描的实际 URL
TARGET_DESCRIPTION = "用于SDK示例的测试网站"

# 全量扫描配置文件的 ID (通常是固定的)
FULL_SCAN_PROFILE_ID = "11111111-1111-1111-1111-111111111111"

def main():
    """
    主函数，执行添加目标、扫描并获取结果的流程。
    """
    if ACUNETIX_URL == "YOUR_ACUNETIX_API_URL" or ACUNETIX_API_KEY == "YOUR_ACUNETIX_API_KEY":
        print("错误：请在代码中或环境变量中设置 ACUNETIX_URL 和 ACUNETIX_API_KEY。")
        print("例如：")
        print("export ACUNETIX_URL='https://your.acunetix.host:3443'")
        print("export ACUNETIX_API_KEY='your_api_key'")
        return

    print(f"正在连接到 Acunetix API: {ACUNETIX_URL}...")
    client = AcunetixClient(base_url=ACUNETIX_URL, api_key=ACUNETIX_API_KEY)

    try:
        # 1. 添加目标网站
        print(f"正在添加目标: {TARGET_URL}...")
        new_target_data = Target(address=TARGET_URL, description=TARGET_DESCRIPTION)
        created_target = client.targets.create(new_target_data)
        target_id = created_target.target_id
        print(f"目标添加成功，ID: {target_id}")

        # 2. 启动扫描
        print(f"正在为目标 {target_id} 启动全量扫描...")
        scan_data = Scan(
            target_id=target_id,
            profile_id=FULL_SCAN_PROFILE_ID,
            schedule={
                "disable": False,
                "start_date": None,  #立即开始
                "time_sensitive": False
            }
        )
        created_scan = client.scans.create(scan_data)
        scan_id = created_scan.scan_id
        print(f"扫描启动成功，扫描 ID: {scan_id}")

        # 3. 等待扫描完成
        print(f"正在等待扫描 {scan_id} 完成...")
        while True:
            scan_session = client.scans.get_scan_session(scan_id=scan_id)
            scan_status = scan_session.status
            print(f"扫描 {scan_id} 当前状态: {scan_status}")
            if scan_status.lower() in ["completed", "aborted", "failed"]:
                break
            time.sleep(30)  # 每30秒检查一次状态

        print(f"扫描 {scan_id} 已完成，状态: {scan_status}")

        if scan_status.lower() == "completed":
            # 4. 获取扫描结果 (漏洞列表)
            print(f"正在获取扫描 {scan_id} 的漏洞信息...")
            # 注意：SDK 可能需要一个方法来直接获取扫描的漏洞，
            # 这里我们先获取扫描的最新会话的漏洞
            # 通常，扫描完成后，会有一个 scan_session_id 关联到漏洞
            # 我们需要找到这个 scan_session_id
            # 或者，如果 API 支持按 scan_id 过滤漏洞，则更好

            # 获取与此扫描相关的最新扫描会话
            scan_info = client.scans.get(scan_id)
            if not scan_info.current_session:
                print(f"扫描 {scan_id} 没有找到当前会话信息，无法获取漏洞。")
                return

            scan_session_id = scan_info.current_session.scan_session_id
            print(f"获取到扫描会话 ID: {scan_session_id} 用于查询漏洞。")

            vulnerabilities = client.vulnerabilities.list(scan_session_id=scan_session_id)
            if vulnerabilities.vulnerabilities:
                print(f"\n发现 {len(vulnerabilities.vulnerabilities)} 个漏洞:")
                for vuln in vulnerabilities.vulnerabilities:
                    print(f"  - 名称: {vuln.vuln_name}")
                    print(f"    严重性: {vuln.severity}")
                    print(f"    状态: {vuln.status}")
                    print(f"    详情链接: {vuln.details_link}") # 假设有这个字段，具体看 Vulnerability model
                    print(f"    确认状态: {'已确认' if vuln.confidence > 50 else '未确认'}") # 假设 confidence > 50 为已确认
                    print("-" * 20)
            else:
                print("未发现漏洞。")
        else:
            print(f"扫描未成功完成 (状态: {scan_status})，不获取漏洞。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 清理操作（可选）：例如删除创建的目标
        if 'target_id' in locals() and target_id:
            try:
                # print(f"\n正在删除目标 {target_id}...")
                # client.targets.delete(target_id)
                # print(f"目标 {target_id} 删除成功。")
                print(f"\n示例运行完毕。如果需要，请手动删除在 Acunetix 中创建的目标 {target_id}。")
            except Exception as e:
                print(f"删除目标 {target_id} 时发生错误: {e}")
        else:
            print("\n示例运行完毕。")


if __name__ == "__main__":
    main()
