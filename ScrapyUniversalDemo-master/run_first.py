import subprocess
from pymongo import MongoClient
import tkinter as tk

# 创建MongoDB的连接
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库和集合
db = client['testdb']
collection = db['test1']

# 创建主窗口
root = tk.Tk()

# 创建标签和输入框
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10)
input_label = tk.Label(input_frame, text="请输入网址或网站名称：")
input_label.pack(side="left", padx=5)
input_box = tk.Entry(input_frame, width=25, font=("Arial", 14))
input_box.pack(side="left", padx=5)
input_box.focus()
input_value = ''
# 创建一个按钮来获取输入框中的文本
def get_input():
    global input_value
    input_value = input_box.get()
    print("输入框中的文本是:", input_value)
    root.destroy()
    
button = tk.Button(root, text="获取输入", command=get_input)
button.pack()

# 启动主循环
root.mainloop()

# 查询文档
results = collection.find({"$or": [{"网址":input_value}, {"网站名":input_value}]})
try:
    for result in results:
        json_data = result['json名']
        subprocess.run(['python', 'run.py', json_data], shell=True)
except KeyError:
    pass
# # 输出结果
# try:
#     for result in results:
#         json_data = result['json名']
#         print(json_data)
#         subprocess.run(['python', 'run.py', json_data], shell=True)
# except KeyError:
#     pass