import os
import shutil
import PyInstaller.__main__

def build():
    print("=== 开始打包 PandocFlow ===")
    
    # Target entry point
    entry_point = os.path.join("src", "main.py")
    if not os.path.exists(entry_point):
        print(f"错误: 找不到入口文件 {entry_point}")
        return

    # Define build parameters
    args = [
        entry_point,
        "--name=PandocFlow",
        "--onefile",
        "--noconsole",
        "--clean",
        "--paths=src",
        "--icon=src/default.ico",
        "--add-data=src/default.ico;src",
    ]

    print(f"正在运行 PyInstaller，参数: {args}")
    try:
        PyInstaller.__main__.run(args)
        print("\n=== 打包完成 ===")
        
        # Verify the file is generated
        exe_path = os.path.join("dist", "PandocFlow.exe")
        if os.path.exists(exe_path):
            print(f"可执行文件成功输出至: {os.path.abspath(exe_path)}")
            # Also copy it to the root of the project workspace for easier user access
            dest_root_path = os.path.join(".", "PandocFlow.exe")
            shutil.copy2(exe_path, dest_root_path)
            print(f"已将可执行文件复制到当前根目录: {os.path.abspath(dest_root_path)}")
        else:
            print("打包失败: 未在 dist/ 目录中检测到生成的 exe 文件。")
            
    except Exception as e:
        print(f"打包过程中遇到异常: {str(e)}")

if __name__ == "__main__":
    build()
