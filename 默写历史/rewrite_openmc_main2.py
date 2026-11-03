# -*- coding: utf-8 -*-
# ============================================================
#  rewrite_openmc_main2.py  --  OpenMC 主流程默写（2）：kur + mesh · 2026-11-03
#  Claude 开好文件头；你从「你从这里往下写」那一行下面开始写
# ============================================================
#
#  主流程分三次默（11/2 你定）：
#    （1）11/2 ✅：import + 截面库路径那一行 + mater + geom
#    （2）今天：kur + mesh                                      约 27 行
#    （3）11/4：run + tallies                                   约 38 行
#
#  今天要写（顺序照原文）：
#    · import openmc、from lesson08_dose import ……（只写 kur、mesh 两个函数用到的名字，你自己想是哪几个）
#    · kur、mesh 两个函数
#  不写：assert · print · if __name__ 整块 · openmc.config 那一行（第 1 次默过，这两个函数用不到）
#        · mater / geom（第 1 次）· tally / tru_tally · run / tallies（11/4）
#
#  🔴 不看：my_code\lesson09_openmc.py、抄写历史\copy_openmc_main.py
#  不用跑（Windows 环境里没有 OpenMC）。写完告诉我，我逐行对拍。
#
#  这两个函数以前出过的错（盯住，答案不在这里）：
#    · 细分以后的列表和原来的列表名字只差一个后缀 —— 用的时候是哪个，每一处都要想（10/13 两次，又一次 x vs x1）
#    · 细分箱的下标：每个粗箱的起点不一样，只在第一个粗箱对的写法是错的（10/13，i = 0 是特殊值）
#    · 取下标用方括号，不是圆括号（10/13 四处）
#    · 给 OpenMC 对象设属性：名字拼错不报错、悄悄新建（11/2 soft.set_temperature、11/1 st.batched）
#    · 类名大写（11/2 openmc.material / openmc.geometry）
#
#  下面两行是 Claude 加的（不用写）：让这个文件能找到 my_code 里的 lesson08_dose
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
# ============================ 你从这里往下写 ============================
