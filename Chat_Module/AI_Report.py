from openai import OpenAI
from typing import *
import os
import json
from pathlib import Path
from Chat_Module.md2pdf import convert_markdown_to_pdf
from openai.types.chat import ChatCompletionMessage


class Kimi_Chat():
    def __init__(self, md_path='Report.md'):
        # 唯一的参数： md_path --- 指定将对话内容保存的Markdown文件名，默认为 Report.md

        # ''' 和Kimi对话的秘钥和url，通过 OpenAI API 实现对话 '''
        self.client = OpenAI(
            # -------------------  API秘钥  --------------------
            api_key="sk-thu2hv2tw3K9jlS6elyafAwBBzHk00paEHj9FCtlzLzLjuxI",
            base_url="https://api.moonshot.cn/v1",
        )

        ''' 用于记录对话的内容  '''
        self.messages = [
            {
                "role": "system",
                "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。\
                    接下来你将对车辆零部件缺陷检测的结果数据进行归纳和分析，并生成一份检测报告，\
                    为生产优化和决策支持提供依据",
            }
        ]
        self.md_path = md_path  # 定义Markdown文件路径

        # 确保Markdown文件存在，如果不存在则创建
        self.ensure_file_exists(self.md_path)

    def clear_message(self):
        ''' 用于记录对话的内容  '''
        self.messages = [
            {
                "role": "system",
                "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。\
                    接下来你将对车辆零部件缺陷检测的结果数据进行归纳和分析，并生成一份检测报告，\
                    为生产优化和决策支持提供依据",
            }
        ]

    # ''' 用于修改所要保存的Markdown文件名 '''
    def rename_markdown(self, file_name: str):
        """修改Markdown文件名"""
        if os.path.exists(self.md_path):
            os.rename(self.md_path, file_name + '.md')
        self.md_path = file_name

    # 确保Markdown文件存在
    def ensure_file_exists(self, file_path: str):
        """ 确保文件存在，如果不存在则创建 """
        if not os.path.exists(file_path):
            open(file_path, "w", encoding="utf-8").close()
        else:
            ''' 如果文件存在，则清空文件内容 '''
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")

    def chat(self, input_text: str) -> str:
        self.messages.append({"role": "user", "content": input_text})

        completion = self.client.chat.completions.create(
            model="moonshot-v1-auto",  # 基于输入的Token，自动选择合适的模型
            messages=self.messages,  # 对话的上下文，也就是提问的内容
            temperature=0.3,  # temperature参数，数值小的时候，模型只返回一个输出；但如果数值比较大，则会返回多个输出回复
        )

        answer_message = completion.choices[0].message
        self.messages.append(answer_message)  # 将回答加入到对话上下文中，从而实现类似网页那样的上下文提问

        return answer_message.content

    ''' 流式输出，但是用不到 '''

    def stream_chat(self, input_text: str) -> str:
        self.messages.append({"role": "user", "content": input_text})

        stream = self.client.chat.completions.create(
            model="moonshot-v1-auto",
            messages=self.messages,
            temperature=0.3,
            stream=True,
        )

        content = ""

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="")
                content += delta.content
        print("\n")
        self.messages.append({
            'role': 'assistant',
            'content': content
        })

    # 用于读取上传的文件，然后将其输入到对话内容中让模型解析
    def upload_files(self, files: List[str]):
        for file in files:
            file_path = Path(file).resolve()
            if not file_path.exists():
                print(f"Error: File {file_path} does not exist.")
                continue
            file_object = self.client.files.create(file=file_path, purpose='file-extract')
            file_content = self.client.files.content(file_id=file_object.id).text
            self.messages.append({
                'role': 'system',
                'content': file_content
            })

    # 用于读取文件并让模型分析，
    def chat_with_files(self, input_text: str, file_list: List[str]) -> str:
        self.upload_files(files=file_list)  # 将文件内容解析并作为提问输入

        self.messages.append({'role': 'user', 'content': input_text})

        completion = self.client.chat.completions.create(
            model="moonshot-v1-auto",
            messages=self.messages,
            temperature=0.3,
        )

        answer_message = completion.choices[0].message
        self.messages.append(answer_message)

        return answer_message.content

    def save_to_markdown(self):

        # 注意：这里是对文件进行续写，所以在使用过程中
        # 保存到Markdown的函数只调用一次就好
        with open(self.md_path, "a", encoding="utf-8") as md_file:
            for i, item in enumerate(self.messages):
                ''' 只保存模型回复的内容，不保存用户输入 '''
                if isinstance(item, ChatCompletionMessage):
                    # md_file.write(f"{self.format_markdown(item.content)}")
                    md_file.write(item.content)
                    md_file.write("\n\n---\n\n")

    def format_markdown(self, markdown_lines: str):
        format_lines = ""
        for line in markdown_lines:
            if line == '-':
                format_lines += ' '
            format_lines += line

        return format_lines

    # 将Markdown文件转换为PDF文件
    # 在做这个操作之前，需要先将对话内容保存到Markdown文件
    def convert_to_pdf(self, pdf_file: str):
        self.save_to_markdown()
        convert_markdown_to_pdf(self.md_path, pdf_file)


# 可以先试着跑一下这个主函数，试试功能
if __name__ == "__main__":
    markdown_file_name = 'final.md'
    kimi = Kimi_Chat(markdown_file_name)

    while True:
        op = (int)(input(
            '请输入选择:\n1. 聊天\n2. 上传文件聊天\n3. 将聊天记录转成MD文件\n4. 将聊天记录转成PDF文件\n5. 清空聊天记录\n6. 修改保存的文件名\n7. 退出\n'))

        if op == 1:
            question = input("请输入你的问题：")
            response = kimi.chat(question)
            print(response)
        elif op == 2:
            files = input("请输入文件名，用英文逗号隔开：")
            files = files.split(",")
            question = input("请输入你的问题：")
            response = kimi.chat_with_files(question, file_list=files)
            print(response)
        elif op == 3:
            kimi.save_to_markdown()
            print(f'聊天记录已保存到 {kimi.md_path}')
        elif op == 4:
            pdf_file = input("请输入PDF文件名：")
            kimi.convert_to_pdf(pdf_file=pdf_file)
            print(f'Markdown 文件已转换为 {pdf_file}')
        elif op == 5:
            kimi.clear_message()
            print("聊天记录已清空")
        elif op == 6:
            new_file_name = input("请输入新的文件名：")
            kimi.rename_markdown(new_file_name)
            print(f'文件名已更改为 {new_file_name}')
        else:
            break
