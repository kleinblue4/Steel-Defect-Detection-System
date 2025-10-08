import markdown
import subprocess
import os

# 设置 wkhtmltopdf 的路径
path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'  # 请替换为你的实际路径


# 将 Markdown 文件转换为 HTML
def markdown_to_html(markdown_file):
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    html = markdown.markdown(markdown_text)
    # 添加字符编码声明
    html_with_encoding = f'<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>{html}</body></html>'
    return html_with_encoding


# 将 HTML 内容保存到本地文件
def save_html_to_file(html_content, html_file):
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


# 使用 wkhtmltopdf 命令将 HTML 文件转换为 PDF 文件
def html_to_pdf(html_file, output_pdf):
    options = [
        '--encoding', 'UTF-8',
        '--quiet',
        '--enable-local-file-access',
        '--custom-header', 'Accept-Encoding', 'gzip',
        '--no-outline',
        '--minimum-font-size', '16',
    ]
    command = [path_to_wkhtmltopdf] + options + [html_file, output_pdf]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"wkhtmltopdf 命令执行失败: {e}")
        raise


# 主函数
def convert_markdown_to_pdf(markdown_file, output_pdf):
    if not os.path.exists(markdown_file):
        print(f"错误: 文件 {markdown_file} 不存在")
        return

    html_content = markdown_to_html(markdown_file)
    html_file = 'tmp.html'
    save_html_to_file(html_content, html_file)
    html_to_pdf(html_file, output_pdf)
    print(f"转换完成! PDF 文件已保存为 {output_pdf}")


if __name__ == "__main__":
    # 调用示例
    markdown_file = 'final.md'  # 输入Markdown文件路径
    output_pdf = 'final.pdf'  # 输出的PDF文件路径
    convert_markdown_to_pdf(markdown_file, output_pdf)
