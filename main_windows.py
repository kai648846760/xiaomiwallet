#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows平台专用启动脚本

为Windows平台提供优化的启动逻辑，解决编码问题和确保应用正确初始化。
包含Windows特定的错误处理和编码设置。
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def windows_main():
    """Windows平台的主函数入口点"""
    try:
        # 尝试导入Flet
        import flet as ft
        
        try:
            # 尝试导入GUI模块
            import gui
            
            def windows_app_main(page: ft.Page):
                """Windows平台的应用主函数包装器"""
                try:
                    # 设置Windows平台特定的页面属性
                    page.title = "小米钱包每日任务"
                    page.theme_mode = ft.ThemeMode.SYSTEM
                    page.padding = 10
                    page.scroll = ft.ScrollMode.AUTO
                    
                    # Windows平台特定设置
                    page.window_width = 800
                    page.window_height = 600
                    page.window_min_width = 600
                    page.window_min_height = 400
                    page.window_resizable = True
                    
                    # 调用原始GUI主函数
                    gui.main(page)
                    
                except Exception as e:
                    # 如果GUI启动失败，显示错误信息
                    error_text = ft.Text(
                        f"Windows应用启动失败：{str(e)}",
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
                    print(f"Windows应用启动错误: {e}")
            
            # 启动Flet应用
            ft.app(target=windows_app_main)
            
        except ImportError as gui_error:
            print(f"❌ 无法导入GUI模块: {gui_error}")
            # 创建简单的错误显示应用
            def fallback_main(page: ft.Page):
                page.title = "导入错误"
                page.window_width = 500
                page.window_height = 300
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
        print("请确保Flet已正确安装在Windows环境中")
        input("按回车键退出...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Windows应用启动时发生未知错误: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    windows_main()