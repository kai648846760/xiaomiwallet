#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android平台专用启动脚本
解决Android应用闪退问题的入口点
"""

import sys
from pathlib import Path

# 确保当前目录在Python路径中
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    import flet as ft
    
    try:
        # 导入GUI模块
        import gui
        
        def android_main(page: ft.Page):
            """Android平台的主函数包装器"""
            try:
                # 设置Android平台特定的页面属性
                page.title = "小米钱包每日任务"
                page.theme_mode = ft.ThemeMode.SYSTEM
                page.padding = 10
                page.scroll = ft.ScrollMode.AUTO
                
                # Android平台特定设置
                page.adaptive = True  # 启用自适应UI
                
                # 调用原始GUI主函数
                gui.main(page)
                
            except Exception as e:
                # 如果GUI启动失败，显示错误信息
                error_text = ft.Text(
                    f"Android应用启动失败：{str(e)}",
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
                print(f"Android应用启动错误: {e}")
        
        if __name__ == "__main__":
            # Android平台启动
            ft.app(target=android_main)
            
    except ImportError as gui_error:
        print(f"导入GUI模块失败: {gui_error}")
        
        def fallback_main(page: ft.Page):
            """备用主函数，当GUI模块导入失败时使用"""
            page.title = "小米钱包每日任务 - 启动失败"
            error_text = ft.Text(
                f"应用启动失败：无法导入GUI模块\n错误信息：{str(gui_error)}",
                color=ft.colors.RED,
                size=16
            )
            page.add(error_text)
            page.update()
        
        if __name__ == "__main__":
            ft.app(target=fallback_main)
            
except ImportError as flet_error:
    print(f"无法导入Flet模块: {flet_error}")
    print("请确保已正确安装Flet依赖")
    # 如果连Flet都无法导入，则无法创建GUI应用
    sys.exit(1)