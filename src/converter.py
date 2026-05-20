import os
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class ConversionWorker(QThread):
    # Signals to communicate with the GUI thread
    # Emits: (input_file, output_file, success, status_message)
    started = pyqtSignal(str)
    finished = pyqtSignal(str, str, bool, str)

    def __init__(self, pandoc_path, input_file, target_format, output_dir=None):
        super().__init__()
        self.pandoc_path = pandoc_path
        self.input_file = os.path.abspath(input_file)
        self.target_format = target_format.lower().strip(".")
        self.output_dir = output_dir

    def run(self):
        self.started.emit(self.input_file)

        # 1. Check if input file exists
        if not os.path.exists(self.input_file):
            self.finished.emit(self.input_file, "", False, "输入文件不存在")
            return

        # 2. Determine output path
        file_dir, file_name = os.path.split(self.input_file)
        base_name, _ = os.path.splitext(file_name)
        
        target_dir = self.output_dir if self.output_dir else file_dir
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir, exist_ok=True)
            except Exception as e:
                self.finished.emit(self.input_file, "", False, f"无法创建输出目录: {str(e)}")
                return

        output_file = os.path.join(target_dir, f"{base_name}.{self.target_format}")

        # If input and output are the same, reject to avoid overwriting source
        if self.input_file.lower() == output_file.lower():
            self.finished.emit(self.input_file, output_file, False, "输入和输出文件格式相同，已跳过")
            return

        # 3. Build pandoc command
        # Basic conversion command: pandoc "input" -o "output"
        cmd = [self.pandoc_path, self.input_file, "-o", output_file]

        # Handle PDF conversions specifically
        # Pandoc requires a PDF engine like weasyprint, wkhtmltopdf, pdflatex, or typst.
        # We can try to specify typst (since it's lightweight and often built-in or easily available)
        # or weasyprint. Let's try to let pandoc decide first. If it fails, we will suggest installing engines.
        if self.target_format == "pdf":
            # We can try typst or wkhtmltopdf if available, but let pandoc run its default.
            # If user has typst on PATH, we can append --pdf-engine=typst, or let pandoc try.
            pass

        # 4. Execute Subprocess
        try:
            # Hide the cmd window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0 # SW_HIDE

            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo,
                timeout=60 # 1 minute timeout per file
            )

            if process.returncode == 0:
                self.finished.emit(self.input_file, output_file, True, "转换成功")
            else:
                stderr_text = process.stderr.strip()
                error_msg = stderr_text if stderr_text else "Pandoc 发生未知错误"
                
                # Check for PDF engine missing error and make it friendly
                if self.target_format == "pdf" and ("pdf-engine" in error_msg or "pdflatex" in error_msg or "wkhtmltopdf" in error_msg):
                    error_msg = "PDF 转换失败: 未检测到 PDF 引擎。请安装 wkhtmltopdf / WeasyPrint / LaTeX 并确保其在环境变量中，或者在命令行执行 `winget install Typst.Typst`。"

                self.finished.emit(self.input_file, output_file, False, error_msg)

        except subprocess.TimeoutExpired:
            self.finished.emit(self.input_file, output_file, False, "转换超时（限时60秒）")
        except Exception as e:
            self.finished.emit(self.input_file, output_file, False, f"执行异常: {str(e)}")
