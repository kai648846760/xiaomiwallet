#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iOS平台专用启动脚本

为iOS平台提供优化的启动逻辑，确保应用在iOS设备上正确初始化和运行。
包含错误处理和平台特定的配置。
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def ios_main():
    """iOS平台的主函数入口点"""
    try:
        # 尝试导入Flet
        import flet as ft
        
        try:
            # 尝试导入GUI模块
            import gui
            
            def ios_app_main(page: ft.Page):
                """iOS平台的应用主函数包装器"""
                try:
                    # 设置iOS平台特定的页面属性
                    page.title = "小米钱包每日任务"
                    page.theme_mode = ft.ThemeMode.SYSTEM
                    page.padding = 10
                    page.scroll = ft.ScrollMode.AUTO
                    
                    # iOS平台特定设置
                    page.adaptive = True  # 启用自适应UI
                    
                    # 调用原始GUI主函数
                    gui.main(page)
                    
                except Exception as e:
                    # 如果GUI启动失败，显示错误信息
                    error_text = ft.Text(
                        f"iOS应用启动失败：{str(e)}",
                        color=ft.colors.RED,
                        size=16,
                        text_align=ft.TextAlign.CENTER
                    )
                    
                    retry_button = ft.ElevatedButton(
                        "重试",
                        on_click=lambda _: page.window_close(),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    )
                    
                    page.add(
                        ft.Column([
                            error_text,
                            retry_button
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    )
                    page.update()
                    print(f"iOS应用启动错误: {e}")
            
            # 启动Flet应用
            ft.app(target=ios_app_main)
            
        except ImportError as gui_error:
            print(f"❌ 无法导入GUI模块: {gui_error}")
            # 创建简单的错误显示应用
            def fallback_main(page: ft.Page):
                page.title = "导入错误"
                error_text = ft.Text(
                    f"无法导入GUI模块：{str(gui_error)}\n\n请检查应用安装是否完整。",
                    color=ft.colors.RED,
                    size=14,
                    text_align=ft.TextAlign.CENTER
                )
                page.add(ft.Column([error_text], alignment=ft.MainAxisAlignment.CENTER))
                page.update()
            
            ft.app(target=fallback_main)
            
    except ImportError as flet_error:
        print(f"❌ 无法导入Flet模块: {flet_error}")
        print("请确保Flet已正确安装在iOS环境中")
        sys.exit(1)
    except Exception as e:
        print(f"❌ iOS应用启动时发生未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ios_main()