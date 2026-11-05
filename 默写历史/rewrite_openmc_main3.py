# -*- coding: utf-8 -*-
# ============================================================
#  rewrite_openmc_main3.py  --  OpenMC 主流程默写（3）：run + tallies · 2026-11-05
#  Claude 开好文件头；你从「你从这里往下写」那一行下面开始写
# ============================================================
#
#  主流程分三次默（11/2 你定）：
#    （1）11/2 ✅：import + 截面库路径那一行 + mater + geom
#    （2）11/3 ✅：kur + mesh
#    （3）今天：run + tallies                                   约 38 行
#
#  今天要写（顺序照原文）：
#    · import（只写 run、tallies 两个函数用到的：你自己想是哪几个）
#    · run(E_dis, tal, inp, batch, n_bat, mat, seed=1)：搭源 → Settings → 四个 xml 导出 → openmc.run → 返回 statepoint 路径
#    · tallies(path, name1)：打开 statepoint → 按名字取 tally → 均值、标准差摊平成列表 → 返回
#  run 里要用 geom(mat)（第 1 次默过）：这里直接写这个名字，不用再把 geom 写一遍
#  不写：assert · print · if __name__ 整块 · openmc.config 那一行 · mater / geom / kur / mesh / tally / tru_tally
#
#  🔴 不看：my_code\lesson09_openmc.py、抄写历史\copy_openmc_main.py
#  不用跑（Windows 环境里没有 OpenMC）。写完告诉我，我逐行对拍。
#
#  这两个函数以前出过的错（盯住，答案不在这里）：
#    · 函数第一行把参数覆盖掉（10/14 两次：mat=mater()、inp=…）
#    · 路径用字符串直接拼（少斜杠）—— 一律 os.path.join（10/14 两次）
#    · 给 OpenMC 对象设属性：名字拼错不报错、悄悄新建（11/2 soft.set_temperature、11/1 st.batched）
#    · 类名大写；方法名、属性名照 OpenMC 的拼法（std_dev 不是 std.dev；.tolist 后面要括号）
#    · statepoint 文件名里的批数从哪来（又一次「算好的变量没用上」）
#    · 打开文件用 with，取东西要在 with 里面
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
# ============================ 你从这里往下写 ============================
