- 前置提醒：由于Markdown文件转pdf需要依赖一些特殊的库以及和Kimi对话的需求，所以最好提前 **pip install pdfkit markdown openai weasyprint** 。如果在运行的时候出现了关于weasyprint库的报错，那是因为没有下载C相关的依赖环境，可以参考：https://doc.courtbouillon.org/weasyprint/stable/first_steps.html# 
根据Windows用户的步骤先安装MSYS2，然后在MSYS2窗口里面运行 **pacman -S mingw-w64-x86_64-pango**（如果第一次出现报错，再运行一次就行）。结束之后在anaconda环境下或者终端里面运行 **python -m weasyprint --info**，如果输出weasyprint库的相关信息就说明安装成功。
然后在**md2pdf.py**中，需要设置wkhtmltopdf的路径，在zip里面提供了wkhtmltopdf的安装包，直接安装就行

---

## Kimi_Chat 类

负责实现与Kimi模型对话的功能，包括：**直接文本对话**、**上传文件对话**、**清空对话内容**、**Markdown文件重命名**、**对话内容保存为Markdown**、**Markdown转PDF** 等功能

### Kimi_Chat 类的初始化

唯一需要指定的参数为：**md_path**  -->  所要保存的Markdown文件的路径
- 使用示例：**kimi = Kimi_Chat("./test.md")**
- **参数介绍：self.messages** 。 这个变量用于**存储对话内容**，每次对话都会将新的对话内容添加到这个变量中，这样每次对话都会保留之前的对话记录。该列表里面存储的是一个字典，字典里面有：role和content，其中role表示角色（**比如：system、user、assistant**），其中assistant表示模型的回复，content表示对话内容。
- **参数介绍：self.client**。调用OpenAI的API，进行对话，其中需要设置api秘钥和url。

### 直接文本对话
**Kimi_Chat.chat(input_text)**

- input_text：输入的文本

调用函数时，需要指定输入的文本 **input_text**，就类似于我们和kimi聊天的对话一样
- 使用示例：**Kimi_Chat.chat("你好，请做个自我介绍")**

### 上传文件对话
**Kimi_Chat.chat_with_files(input_text, file_path)**

- input_text：输入的文本
- file_path：上传的文件路径，可以上传多个文件，按照main函数那边将字符串split一下变成列表list就可以。需要注意的是，文件如果在当前目录下，可以直接写文件名（比如:test.txt），否则最好需要写绝对路径

### 清空对话内容
由于是使用API调用与Kimi模型进行对话，所有不能自动实现像在网页上聊天一样，每次对话都会保留之前的对话记录。
为了模拟保留之前对话内容的效果，在Kimi_Chat类中使用**self.messages**来存储每一次对话的内容，这样每次Kimi在思考的时候都会考虑到先前的对话内容。（具体实现可以看Kimi_Chat.chat()函数里面的代码）

如果需要清空对话内容，只需要调用 **Kimi_Chat.clear_message()** 即可，这样会将对话过程的信息重置到最初的状态。

### Markdown文件重命名
如果需要将Markdown文件重命名，只需要调用 **Kimi_Chat.rename_markdown(new_name)** 即可，此时不仅会修改类中的md_path，也会将原本的Markdown文件重命名。

- 使用示例：**Kimi_Chat.rename_markdown("test2.md")**

### 对话内容保存为Markdown
用于将对话的内容保存的Markdown文件，用于后续将Markdown文件转成PDF。
值得注意的是，在保存对话内容的时候，**只保留模型的回复内容**，也就是客户的提问不会保存；同时由于每次保留回复内容都是从上下文中提取对话内容，所以如果调用了一次保存内容函数，那么最好后面就不要再调用，否则可能出现保存的内容出现重复的情况。

- 使用示例：**Kimi_Chat.save_to_markdown()**

### Markdown转PDF
用于将Markdown文件转成PDF文件，方便后续进行打印或者下载。但是由于使用代码进行文件格式的转换，存在一些问题：列表标号混乱的情况。这部分还在解决中。。。。。

- 使用示例：**Kimi_Chat.convert_to_pdf()**
