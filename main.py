from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QRadioButton, QButtonGroup
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtWidgets import QPlainTextEdit
import time

import sys
import ui_MyUI

msg = ""


class Job:
    def __init__(self, Length, JobID):
        self.Length = Length
        self.JobName = JobID

    def StatusLog(self, AllOrDeall=1):
        global msg
        msg += f"{self.JobName}"
        if AllOrDeall < 0:
            msg += "释放"
        else:
            msg += f"申请{self.Length}K内存"
        msg += "成功\n"


class Managerment:
    def __init__(self, totalsize, AlgMode):
        self.total_size = totalsize
        self.memory = [(0, self.total_size, None)]  # 初始时整个内存都是一个空闲分区
        self.JobQueue = [Job(110, "作业1"), Job(132, "作业2"), Job(131, "作业3"), Job(-110, "作业1"), Job(123, "作业4"),
                         Job(-132, "作业2"), Job(148, "作业5"), Job(-131, "作业3"), Job(120, "作业6"),
                         Job(-123, "作业4"), Job(147, "作业7"), Job(107, "作业8")]
        self.AlgMode = AlgMode

    def First_allocate(self, Job):
        for i, (start, end, p_id) in enumerate(self.memory):
            if end - start >= Job.Length and p_id is None:  # 找到第一个足够大的空闲分区
                self.memory.insert(i + 1, (start + Job.Length, end, None))  # 切割剩余的空闲分区
                self.memory[i]=(start,start+Job.Length,Job.JobName)
                Job.StatusLog()
                return True

        return False  # 找不到合适的空闲分区，返回False表示分配失败

    def First_deallocate(self, Job):

        for i, (start, end, p_id) in enumerate(self.memory):
            if p_id == Job.JobName:  # 找到已分配给该进程的分区
                self.memory[i] = (start, end, None)  # 将该分区标记为空闲
                self.merge_free_blocks()  # 尝试合并相邻的空闲分区
                Job.StatusLog(-1)
                break

    def Best_allocate(self, Job):
        best_fit_index = -1
        best_fit_size = float('inf')

        for i, (start, end, p_id) in enumerate(self.memory):
            if (end - start >= Job.Length) and (end - start < best_fit_size) and p_id is None:
                best_fit_index = i
                best_fit_size = end - start

        if best_fit_index != -1:  # 找到合适的空闲分区
            start, end, _ = self.memory[best_fit_index]
            self.memory[best_fit_index]= (start, start + Job.Length, Job.JobName)
            self.memory.insert(best_fit_index + 1, (start + Job.Length, end, None))  # 切割剩余的空闲分区
            Job.StatusLog()
            return True

        return False  # 找不到合适的空闲分区，返回False表示分配失败

    def Best_deallocate(self, Job):
        for i, (start, end, p_id) in enumerate(self.memory):
            if p_id == Job.JobName:  # 找到已分配给该进程的分区
                self.memory[i] = (start, end, None)  # 将该分区标记为空闲
                self.merge_free_blocks()  # 尝试合并相邻的空闲分区
                Job.StatusLog(-1)
                break

    def merge_free_blocks(self):
        i = 0
        while i < len(self.memory) - 1:
            start1,_, p1_id = self.memory[i]
            _,end2, p2_id = self.memory[i + 1]
            if p1_id is None and p2_id is None:  # 如果相邻两个分区都是空闲分区
                self.memory[i] = (start1, end2, None)  # 合并两个分区
                self.memory.pop(i + 1)
            else:
                i += 1


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, Managerment):
        super().__init__()
        self.Managerment = Managerment
        self.ui = ui_MyUI.Ui_MainWindow()
        self.ui.setupUi(self)


        self.ui.Alg_1.setChecked(True)
        self.ui.plainTextEdit.setPlainText('640')
        self.ui.plainTextEdit_2.setPlainText('7')
        button_group = self.ui.buttonGroup
        button_group.setExclusive(True)  # 设置为互斥模式
        button_group.buttonClicked.connect(self.setmode)

        self.ui.configureBtn.setText('开始')
        self.ui.configureBtn.clicked.connect(self.StartManage)
        self.ui.resetBtn.clicked.connect(self.reset)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.DrawUI)
        self.timer.start()

    def setmode(self):
        if self.ui.Alg_1.isChecked():
            self.Managerment.AlgMode = "首次适应算法"
        elif self.ui.Alg_2.isChecked():
            self.Managerment.AlgMode = "最佳适应算法"

    def reset(self):
        self.Managerment.total_size = 640
        self.Managerment.memory=[(0,self.Managerment.total_size,None)]
        global msg
        msg=""
        self.repaint()

    def DrawUI(self):
        self.ui.plainTextEdit.setPlainText(f"{self.Managerment.total_size}")
        self.ui.textEdit.setText(msg)


    def StartManage(self):
        self.setmode()
        for mission in self.Managerment.JobQueue:
            if self.Managerment.AlgMode == "首次适应算法":
                if mission.Length >= 0:
                    self.Managerment.First_allocate(mission)
                else:
                    self.Managerment.First_deallocate(mission)
            elif self.Managerment.AlgMode == "最佳适应算法":
                if mission.Length >= 0:
                    self.Managerment.Best_allocate(mission)
                else:
                    self.Managerment.Best_deallocate(mission)
            self.DrawUI()
            self.repaint()
            time.sleep(1)

    def paintEvent(self,event):

        self.DrawUI()
        # 绘制区域的坐标
        origin_x =0
        origin_y = 90
        width = 1301
        height =161

        painter = QPainter(self)
        pen = QPen()  # 画笔
        pen.setColor(QColor(0, 0, 0))  # 黑色画笔画外框
        brush = QBrush(QColor(165, 165, 165, 255))  # 画刷
        painter.setPen(pen)  # 添加画笔
        painter.setBrush(brush)  # 添加画刷

        painter.drawRect(origin_x, origin_y, width, height)  # 绘制总体外框

        color_collection = [
            QColor("#FFB7DD"), QColor("#FF44AA"), QColor("#C10066"), QColor("#FFDDAA"),
            QColor("#FFAA33"), QColor("#EE7700"), QColor("#EEFFBB"), QColor("#CCFF33"),
            QColor("#99DD00"), QColor("#BBFFEE"), QColor("#33FFAA"), QColor("#00DD77"),
            QColor("#CCDDFF"), QColor("#5599FF"), QColor("#0044BB"), QColor("#9955FF")
        ]

        for i,(start, end, JobID) in enumerate(self.Managerment.memory):
            if JobID ==None:
                continue
            job_num = int(JobID.split('作业')[1])
            brush_temp = QBrush(color_collection[job_num % 15])
            painter.setBrush(brush_temp)  # 设置颜色


            # 位置设置
            block_x = int((width * (
                    int(start) + 1) / self.Managerment.total_size) + origin_x)
            block_y = int(origin_y)
            block_width = int(width * int(end - start) / self.Managerment.total_size)
            block_height = int(height)
            print(f"int start+1={int(start)+1},width={width},end-start={end-start},total_size={self.Managerment.total_size}")
            painter.drawRect(block_x, block_y, block_width, block_height)
            print(f"{block_x},{block_y},{block_width},{block_height}")
            painter.drawText(int(block_x + block_width / 2 - width * block_width / 10000), int(block_y + block_height / 2),
                             JobID)

            job_length = str(end - start) + "K"
            painter.drawText(int(block_x + block_width / 2 - width * block_width / 10000),
                             int(block_y + block_height / 2 + height / 9), job_length)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    manage = Managerment(640, "首次适应算法")
    mw = MainWindow(manage)
    mw.show()
    sys.exit(app.exec_())
