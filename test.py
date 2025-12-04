import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class SpectrophotometerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("分光光度计数据处理 AI小程序")
        self.root.geometry("1000x600")
        
        # 初始化数据
        self.data = [
            (50, 0.120),
            (55, 0.206),
            (60, 0.338),
            (65, 0.460),
            (70, 0.547),
            (75, 0.641),
            (80, 0.725)
        ]
        
        self.create_widgets()
        self.init_plot()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置权重 - 左侧1/3，右侧2/3
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # 左侧
        main_frame.columnconfigure(1, weight=2)  # 右侧
        main_frame.rowconfigure(0, weight=1)
        
        # 左侧框架
        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 数据表格
        self.tree = ttk.Treeview(left_frame, columns=('浓度', '吸光度'), show='headings', height=7)
        self.tree.heading('浓度', text='浓度含量(%)')
        self.tree.heading('吸光度', text='吸光度(A)')
        self.tree.column('浓度', width=100, anchor='center')
        self.tree.column('吸光度', width=100, anchor='center')
        
        # 设置表格样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 设置表格头部样式 - 绿色背景
        style.configure('Treeview.Heading', 
                       background='#4CAF50', 
                       foreground='white',
                       font=('SimHei', 12, 'bold'))
        
        # 设置表格内容样式
        style.configure('Treeview',
                       background='white',
                       fieldbackground='white',
                       font=('SimHei', 10),
                       rowheight=20)
        
        # 设置按钮样式 - 绿色背景
        style.configure('TButton',
                       background='#4CAF50',
                       foreground='white',
                       font=('SimHei', 12, 'bold'),
                       padding=(10, 5))
        
        style.map('TButton',
                 background=[('active', '#45a049')])
        
        # 添加初始数据
        for item in self.data:
            self.tree.insert('', 'end', values=item)
        
        # 允许编辑表格
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 按钮框架
        button_frame = ttk.Frame(left_frame, padding="10")
        
        # 按钮
        self.btn_create = ttk.Button(button_frame, text="建立坐标", command=self.create_coordinate)
        self.btn_plot = ttk.Button(button_frame, text="绘制图像", command=self.plot_data)
        self.btn_fit = ttk.Button(button_frame, text="数据拟合", command=self.fit_data)
        self.btn_reset = ttk.Button(button_frame, text="复位清屏", command=self.reset_screen)
        
        # 布局左侧组件
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 按钮布局
        self.btn_create.grid(row=0, column=0, padx=5, pady=5)
        self.btn_plot.grid(row=0, column=1, padx=5, pady=5)
        self.btn_fit.grid(row=1, column=0, padx=5, pady=5)
        self.btn_reset.grid(row=1, column=1, padx=5, pady=5)
        
        # 设置左侧框架权重
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        # 右侧框架
        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标题标签 - 放在右上角
        title_label = ttk.Label(right_frame, text="分光光度计数据处理\nAI小程序", 
                               font=('SimHei', 16, 'bold'), justify='center')
        title_label.grid(row=0, column=0, sticky=(tk.E), pady=(0, 10))
        
        # 创建图表框架
        chart_frame = ttk.Frame(right_frame)
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建图表
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置右侧框架权重
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
    
    def init_plot(self):
        # 初始化图表
        self.ax.set_xlabel('浓度含量(%)', fontproperties='SimHei', fontsize=12)
        self.ax.set_ylabel('吸光度(A)', fontproperties='SimHei', fontsize=12)
        # 使用细密的网格线
        self.ax.grid(True, linestyle='-', alpha=0.3)
        # 设置坐标轴范围
        self.ax.set_xlim(45, 85)
        self.ax.set_ylim(-0.05, 0.8)
        # 设置刻度
        self.ax.set_xticks(np.arange(50, 85, 5))
        self.ax.set_yticks(np.arange(0, 0.8, 0.1))
        self.canvas.draw()
    
    def on_double_click(self, event):
        # 编辑表格数据
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑数据")
        edit_window.geometry("300x150")
        
        # 获取当前值
        current_value = self.tree.item(item, 'values')[int(column[1])-1]
        
        # 创建标签和输入框
        ttk.Label(edit_window, text=f"请输入新的{'浓度' if column == '#1' else '吸光度'}值:").pack(pady=10)
        entry = ttk.Entry(edit_window)
        entry.pack(pady=5)
        entry.insert(0, str(current_value))
        entry.focus()
        
        def save_edit():
            try:
                new_value = float(entry.get())
                values = list(self.tree.item(item, 'values'))
                values[int(column[1])-1] = new_value
                self.tree.item(item, values=values)
                
                # 更新数据
                index = self.tree.index(item)
                self.data[index] = tuple(values)
                
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
        
        # 保存按钮
        ttk.Button(edit_window, text="保存", command=save_edit).pack(pady=10)
    
    def create_coordinate(self):
        # 建立坐标（重置图表）
        self.ax.clear()
        self.ax.set_xlabel('浓度含量(%)', fontproperties='SimHei', fontsize=12)
        self.ax.set_ylabel('吸光度(A)', fontproperties='SimHei', fontsize=12)
        # 使用细密的网格线
        self.ax.grid(True, linestyle='-', alpha=0.3)
        
        # 设置固定的坐标轴范围
        self.ax.set_xlim(45, 85)
        self.ax.set_ylim(-0.05, 0.8)
        
        # 设置刻度
        self.ax.set_xticks(np.arange(50, 85, 5))
        self.ax.set_yticks(np.arange(0, 0.8, 0.1))
        
        self.canvas.draw()
        messagebox.showinfo("提示", "坐标已建立")
    
    def plot_data(self):
        # 绘制数据
        if not self.data:
            messagebox.showwarning("警告", "没有数据可绘制")
            return
        
        # 清除之前的散点和线条
        self.ax.clear()
        self.init_plot()
        
        # 绘制新的散点
        concentrations = [d[0] for d in self.data]
        absorbances = [d[1] for d in self.data]
        self.ax.scatter(concentrations, absorbances, color='blue', s=60, marker='o', edgecolors='black')
        
        self.canvas.draw()
        messagebox.showinfo("提示", "图像绘制完成")
    
    def fit_data(self):
        # 数据拟合
        if not self.data or len(self.data) < 2:
            messagebox.showwarning("警告", "数据不足，无法进行拟合")
            return
        
        concentrations = np.array([d[0] for d in self.data])
        absorbances = np.array([d[1] for d in self.data])
        
        # 线性拟合
        z = np.polyfit(concentrations, absorbances, 1)
        p = np.poly1d(z)
        
        # 计算相关系数
        correlation = np.corrcoef(concentrations, absorbances)[0, 1]
        
        # 清除之前的内容
        self.ax.clear()
        self.init_plot()
        
        # 绘制散点
        self.ax.scatter(concentrations, absorbances, color='blue', s=60, marker='o', edgecolors='black')
        
        # 绘制拟合线
        x_fit = np.linspace(min(concentrations), max(concentrations), 100)
        y_fit = p(x_fit)
        self.ax.plot(x_fit, y_fit, "r-", linewidth=2)
        
        self.canvas.draw()
        messagebox.showinfo("提示", f"数据拟合完成\n拟合方程: y={z[0]:.4f}x+{z[1]:.4f}\n相关系数: r={correlation:.4f}")
    
    def reset_screen(self):
        # 复位清屏
        self.ax.clear()
        self.init_plot()
        
        # 重置数据
        self.data = [
            (50, 0.120),
            (55, 0.206),
            (60, 0.338),
            (65, 0.460),
            (70, 0.547),
            (75, 0.641),
            (80, 0.725)
        ]
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 重新添加初始数据
        for item in self.data:
            self.tree.insert('', 'end', values=item)
        
        messagebox.showinfo("提示", "已复位清屏")

def main():
    root = tk.Tk()
    app = SpectrophotometerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
