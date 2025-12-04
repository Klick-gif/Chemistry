import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import linregress, pearsonr
import mplcursors
import sys


class AbsorbanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("分光光度计法数据处理AI小程序")
        self.root.state('zoomed')  # 全屏

        # 固定数据
        self.percentages = np.array([50, 55, 60, 65, 70, 75, 80], dtype=float)
        self.absorbances = np.array([0.120, 0.206, 0.338, 0.460, 0.547, 0.641, 0.725], dtype=float)
        self.qifen = 80.81 * self.absorbances - 1.076

        self.step = 0
        self.cursor = None  # 用于追踪mplcursors对象
        self.coordinates_drawn = False  # 用于跟踪是否已经绘制了坐标
        self._make_layout()
        self._populate_table()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _make_layout(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabel', background='#ffffff', font=('KaiTi', 28))
        style.configure('Treeview', font=('KaiTi', 32, 'bold'), background='white', fieldbackground='white', rowheight=80,
                borderwidth=1, relief='solid', highlightthickness=1, highlightcolor='gray')
        style.configure('Treeview.Heading', font=('KaiTi', 35, 'bold'), background='#5baf33', relief='solid', borderwidth=1, padding=(0, 22), foreground='white')

        # 设置表格布局
        style.layout('Treeview', [
            ('Treeview.treearea', {'sticky': 'nswe', 'border': '1'})
        ])
        
        style.layout('Treeview.Item', [
            ('Treeitem.padding', {'sticky': 'nswe', 'children': [
                ('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
                ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                ('Treeitem.text', {'side': 'left', 'sticky': ''})
            ]})
        ])
        style.configure('TButton', font=('KaiTi', 40, 'bold'), background='#9ed287', padding=(-20, 20))
        # style.map('TButton', background=[('active', '#4caf50')])
        
        # 左侧1, 右侧4 (表格占1/5)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=20)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)

        # # 添加标题
        # title_label = ttk.Label(left, text="分光光度计法数据处理", font=('KaiTi', 32, 'bold'), 
        #                        foreground='#1b5e20', background='#f0f7f0')
        # title_label.grid(row=0, column=0, pady=(0, 20))

        self.table = ttk.Treeview(left, columns=("pct", "abs"), show="headings", height=15)
        self.table.heading("pct", text="漆酚含量(%)")
        self.table.heading("abs", text="吸光度(A)")

        # 设置交替行颜色
        self.table.tag_configure('odd', background='#f0f7f0')
        self.table.tag_configure('even', background='#d2e4ce')
       
        for col, width in [("pct", 50), ("abs", 50)]:
            self.table.column(col, anchor="center", width=width)
        self.table.grid(row=1, column=0, sticky="nsew", pady=10)

        btn_frame1 = ttk.Frame(left)
        btn_frame1.grid(row=2, column=0, pady=10)
        for i, txt in enumerate(["建立坐标", "绘制图像"], start=1):
            b = ttk.Button(btn_frame1, text=txt, command=lambda i=i: self.on_button(i), width=12, style='Round.TButton')
            b.grid(row=0, column=i - 1, padx=12, pady=10)
        btn_frame2 = ttk.Frame(left)
        btn_frame2.grid(row=3, column=0, pady=10)
        for i, txt in enumerate(["数据拟合", "复位清屏"], start=3):
            b = ttk.Button(btn_frame2, text=txt, command=lambda i=i: self.on_button(i), width=12, style='Round.TButton')
            b.grid(row=0, column=i - 1, padx=12, pady=10)

        right = ttk.Frame(self.root, padding=20)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # 创建一个框架来包含公式和相关系数标签
        info_frame = ttk.Frame(right)
        info_frame.grid(row=0, column=0, sticky="w")


        self.title1 = ttk.Label(info_frame, text="分光光度计法数据处理", font=('KaiTi', 45, 'bold'), foreground="#cf0002", background='#ffffff')
        self.title1.grid(row=0, column=1, sticky="w", padx=260, pady=0)
        self.tilte2 = ttk.Label(info_frame, text="\tAI小程序", font=('KaiTi', 45, 'bold'), foreground="#cf0002", background='#ffffff')
        self.tilte2.grid(row=1, column=1, sticky="w", padx=200, pady=0)

        self.fig, self.ax = plt.subplots(figsize=(10, 9), dpi=100)
        # 调整图形边距
        self.fig.subplots_adjust(left=0.08, right=0.95, bottom=0.15, top=0.98)
        # 初始只显示网格，不显示坐标轴标签
        self.ax.grid(True, linestyle=':')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        # 设置坐标轴范围
        self.ax.set_xlim(45, 85)
        self.ax.set_ylim(0, 0.9)

        # 设置网格和刻度
        self.ax.grid(True, linestyle='-', linewidth=1.5, color='gray', alpha=0.7)
        self.ax.set_xticks(np.arange(45, 90, 5))
        self.ax.set_yticks(np.arange(0, 1.0, 0.1))
        # 移除图形边框
        for spine in ['top', 'right', 'bottom', 'left']:
            self.ax.spines[spine].set_visible(False)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().grid(row=3, column=0, sticky="nsew")

    def _populate_table(self):
        for i, (p, a) in enumerate(zip(self.percentages, self.absorbances)):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.table.insert("", "end", values=(f"{p:.0f}%", f"{a:.3f}"), tags=(tag,))

    def _clear_cursor(self):
        """清理mplcursors对象"""
        if self.cursor is not None:
            try:
                self.cursor.remove()
            except:
                pass
            self.cursor = None

    def show_custom_messagebox(self, title, message):
        """创建自定义的大字体消息框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("650x500")
        dialog.resizable(False, False)
        dialog.configure(background='#f0f7f0')

        # 居中显示
        dialog.transient(self.root)
        dialog.grab_set()

        # 设置对话框位置居中
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (650 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"650x500+{x}+{y}")

        # 创建消息标签
        message_label = ttk.Label(dialog, text=message, font=('KaiTi', 30),
                                  justify='center', background='#f0f7f0')
        message_label.pack(expand=True, fill='both', padx=20, pady=20)

        # 确定按钮
        ok_button = ttk.Button(dialog, text="确定",
                               command=dialog.destroy,
                               style='Custom.TButton')
        ok_button.pack(pady=10)

        # 设置按钮样式
        style = ttk.Style()
        style.configure('Custom.TButton', font=('KaiTi', 20), background='#2e7d32')

        # 绑定回车键
        dialog.bind('<Return>', lambda e: dialog.destroy())
        dialog.focus_set()

    def establish_coordinates(self):
        """建立坐标轴和标签"""
        # 设置坐标轴颜色和粗细
        self.ax.spines['bottom'].set_color('green')
        self.ax.spines['left'].set_color('green')
        self.ax.spines['bottom'].set_linewidth(3)
        self.ax.spines['left'].set_linewidth(3)

        
        # 设置坐标轴标签
        self.ax.set_xlabel("漆酚含量(%)", fontsize=32, fontname='KaiTi', color='green', weight='bold')
        self.ax.set_ylabel("吸光度(A)", fontsize=32, fontname='KaiTi', color='green', weight='bold')
        # 设置刻度颜色
        self.ax.tick_params(axis='both', which='both', colors='green', width=3)
        self.ax.xaxis.label.set_color('green')
        self.ax.yaxis.label.set_color('green')
        # 设置坐标轴范围
        self.ax.set_xlim(45, 85)
        self.ax.set_ylim(0, 0.9)
        self.ax.set_xticks(np.arange(45, 90, 5))
        self.ax.set_yticks(np.arange(0, 1.0, 0.1))
        self.ax.tick_params(labelsize=14)
        self.coordinates_drawn = True
        self.ax.grid(True, linestyle='-', linewidth=1.5, color='gray', alpha=0.5)
        self.canvas.draw()

    def on_button(self, idx):
        # 每次绘图前先清理之前的cursor
        self._clear_cursor()

        if idx == 1:
            self.step = 1
            self.ax.cla()
            # 重新设置坐标轴
            for spine in ['top', 'right']:
                self.ax.spines[spine].set_visible(False)
            self.ax.spines['bottom'].set_visible(True)
            self.ax.spines['left'].set_visible(True)
            self.establish_coordinates()  # 调用坐标轴设置方法
            self.canvas.draw()
        elif idx == 2 and self.step >= 1:
            self.step = 2
            self.ax.cla()
            self.ax.scatter(self.percentages, self.absorbances, s=200, color='#1e3799')
            self.establish_coordinates()
            self.canvas.draw()
        elif idx == 3 and self.step >= 2:
            self.step = 3
            self.ax.cla()
            self.ax.scatter(self.percentages, self.absorbances, s=200, color='#1e3799')
            m, b = linregress(self.percentages, self.absorbances)[:2]

            # 计算相关系数
            r, _ = pearsonr(self.percentages, self.absorbances)

            y_fit = m * np.array([46.0, 84.0]) + b
            line, = self.ax.plot(np.array([46.0, 84.0]), y_fit, linestyle='-', color='#eb3b5a', linewidth=4)
            formula = f"拟合公式：A = {m:.4f}x - {abs(b):.4f}"
            correlation = f"相关系数：r = {r:.3f}"

            # 仅在拟合曲线上启用提示
            self.cursor = mplcursors.cursor(line, hover=0)
            # 增加线条的检测厚度，方便触发
            line.set_picker(True)
            line.set_pickradius(30)  # 增加可点击范围

            @self.cursor.connect("add")
            def on_add(sel):
                x, y = sel.target
                sel.annotation.set_text(f"x={x:.0f}%\ny={y:.3f}")

                if x > 75:
                    # 右上区域，气泡显示在左下
                    sel.annotation.set_position((x - 6, y - 0.3))
                elif x < 54:
                    sel.annotation.set_position((x - 3, y + 0.1))
                else:
                    # 设置气泡位置：左上角偏移
                    sel.annotation.set_position((x - 8, y + 0.085))  # 向左向上偏移

                sel.annotation.get_bbox_patch().set(
                    fc="white",
                    ec="darkred",  # 深红色边框
                    lw=2,  # 加粗边框线宽
                    boxstyle="round,pad=0.65"  # 增加padding
                )
                sel.annotation.set_fontsize(50)  # 数值大小翻倍
                sel.annotation.set_color("darkred")  # 深红色文字
                sel.annotation.set_weight("bold")  # 加粗文字
                sel.annotation.arrow_patch.set(
                    arrowstyle="->",  # 标准箭头样式
                    fc="darkred",  # 深红色填充
                    ec="darkred",  # 深红色边框
                    alpha=0.8,  # 稍微提高透明度
                    lw=3,  # 增加线宽让箭头更粗
                    mutation_scale=200  # 增大箭头大小，让箭头更长更明显
                )
                sel.annotation.draggable(False)

            self.establish_coordinates()
            self.canvas.draw()
            self.show_custom_messagebox("拟合成功",
                                        f"线性拟合完成\n\n{formula}\n\n{correlation}\n\n点击拟合线查看具体数值")
        elif idx == 4:
            self.step = 0
            self.ax.cla()
            # 初始只显示网格，不显示坐标轴标签
            self.ax.grid(True, linestyle=':')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.ax.set_xticklabels([])
            self.ax.set_yticklabels([])
            # 设置坐标轴范围
            self.ax.set_xlim(45, 85)
            self.ax.set_ylim(0, 0.9)

            # 设置网格和刻度
            self.ax.grid(True, linestyle='-', linewidth=1.5, color='gray', alpha=0.7)
            self.ax.set_xticks(np.arange(45, 90, 5))
            self.ax.set_yticks(np.arange(0, 1.0, 0.1))
            # 移除图形边框
            for spine in ['top', 'right', 'bottom', 'left']:
                self.ax.spines[spine].set_visible(False)
            self.canvas.draw()


    def on_closing(self):
        """窗口关闭时的清理工作"""
        try:
            # 清理mplcursors
            self._clear_cursor()

            # 清理matplotlib资源
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()

            if hasattr(self, 'fig'):
                plt.close(self.fig)

            # 清理所有matplotlib图形
            plt.close('all')

        except Exception as e:
            print(f"清理资源时出错: {e}")
        finally:
            # 销毁tkinter窗口
            self.root.quit()
            self.root.destroy()


if __name__ == "__main__":
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示问题
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    root = tk.Tk()
    app = AbsorbanceApp(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        # 确保程序完全退出
        sys.exit(0)
