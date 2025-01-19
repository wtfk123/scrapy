import tkinter as tk

# 创建主窗口
root = tk.Tk()

# 创建标签和输入框
input_label = tk.Label(root, text="请输入文本:")
input_label.pack()
input_box = tk.Entry(root)
input_box.pack()

# 创建一个按钮来获取输入框中的文本
def get_input():
    text = input_box.get()
    print("输入框中的文本是:", text)

button = tk.Button(root, text="获取输入", command=get_input)
button.pack()

# 启动主循环
root.mainloop()