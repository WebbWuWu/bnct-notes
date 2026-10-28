# -*- coding: utf-8 -*-
# ============================================================
#  copy_load_heating.py  --  load_heating 抄写稿（10/28 抄；默写（1）另排）
#  Claude 2026-10-28 开好文件头；从「你从这里往下写」那一行下面开始，照原文手敲
# ============================================================
#
#  照着抄的原文：my_code\lesson11_mt301.py 第 25–38 行 def load_heating(nuc, T)
#
#  要写：函数体，四步
#    ① 拼出这个核素的 .h5 文件路径（库目录 LIB + 核素名 + ".h5"）
#    ② 打开文件，进到这个核素的组，读这个温度的能量网格 E
#    ③ 读 reaction_301 这个温度下的 xs（加热数），以及 xs 这个数据集上挂的 threshold_idx（从第几个格点开始有值）
#    ④ 建一个和 E 一样长、全是 0 的数组 heat，从 threshold_idx 开始放进 xs → return E, heat
#
#  不写：import（10/27 定，抄写不抄 import）· assert 和它上面那行 [Claude assert] 注释 · print · if __name__ 整块 · show_mt301
#
#  用到的写法逐个回顾（10/27 定：用过的也讲一遍；例子和项目无关）
#    · os.path.join(目录, 文件名)：拼路径，自动加斜杠。os.path.join("D:\\photos", "cat.jpg") → "D:\\photos\\cat.jpg"
#        你犯过：字符串直接相加 OUT_DIR + "x.json"，少了斜杠（10/14 两次）
#    · with h5py.File(路径, "r") as f：只读打开 HDF5，缩进块结束自动关文件。"r" 是读；写 "w" 会把文件清空
#    · f["组名"]["子组名"]：一层一层往里走，和字典一样用方括号。例：书架["三楼"]["小说区"]
#        你犯过：HDF5 名字拼错 reaction_301 → reactions_301（10/22）
#    · 数据集[:]：把数据集整段读成 numpy 数组。只有「数据集」能这样读，「组」不行（10/22 你把组当数据集用过）
#    · 数据集.attrs["名字"]：读挂在数据集上的属性（一个小标签，不是数据本身）。只在 h5py 对象上有，Python 字典没有 .attrs
#        例：一瓶药（数据集）上贴的标签「保质期」就是 attrs
#    · int(x)：把 numpy 的整数转成普通 Python 整数，后面拿去当下标
#    · np.zeros(n)：长 n、全是 0.0 的数组。np.zeros(4) → [0. 0. 0. 0.]
#    · 数组[k:] = 另一个数组：从第 k 个位置一直到末尾，整段替换；两边长度必须一样
#        例：a = np.zeros(5); a[2:] = [7, 8, 9] → [0. 0. 7. 8. 9.]
#
#  抄的时候想清楚两件事（老师问答会问）：
#    1. 为什么要「前面补 0」？threshold_idx 以下的能量，这个核素的 MT=301 是不存在、还是等于 0？
#    2. 为什么最后要和 E 一样长？（提示：build_water 里 sigma_at_ext 拿 heat 和截面用同一张能量网格查）
#
#  下面五行是 Claude 加的（不用抄）：路径 + 函数要用的 import（抄写不抄 import）
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
from xs_lookup import LIB
import h5py
import numpy as np
# ============================ 你从这里往下写 ============================
def load_heating(nuc,T):
    path=os.path.join(LIB,nuc+".h5")
    with h5py.File(path,"r")as f:
        root=f[nuc]
        E=root["energy"][T][:]
        xs_301=root["reactions"]["reaction_301"][T]["xs"][:]
        thi_301=int(root["reactions"]["reaction_301"][T]["xs"].attrs["threshold_idx"])
        heat=np.zeros(len(E))
        heat[thi_301:]=xs_301
    return E,heat
