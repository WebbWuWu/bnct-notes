# -*- coding: utf-8 -*-
# ============================================================
#  rewrite_openmc_main1.py  --  OpenMC 主流程默写（1）：mater + geom · 2026-11-02
#  Claude 开好文件头；你从「你从这里往下写」那一行下面开始写
# ============================================================
#
#  主流程分三次默（11/2 你定：一次写不了这么多）：
#    （1）今天：import + 截面库路径那一行 + mater + geom        约 25 行
#    （2）下周：kur + mesh                                      约 27 行
#    （3）下周：run + tallies                                   约 38 行
#
#  今天要写（顺序照原文）：
#    · import openmc、from lesson08_dose import ……（今天两个函数用到哪几个名字，你自己想）
#    · openmc.config 那一行（截面库路径）
#    · mater、geom 两个函数
#  不写：assert · print · if __name__ 整块 · KUR_TALLIES 清单 · path1 · tally / tru_tally · kur / mesh / run / tallies（下周）
#  照抄、不计分：name='soft tissue' 这类标签字符串、路径字符串里的文件夹名
#
#  🔴 不看：my_code\lesson09_openmc.py、抄写历史\copy_openmc_main.py
#  不用跑（Windows 环境里没有 OpenMC）。写完告诉我，我逐行对拍。
#
#  抄写对拍（11/1 那份，11/2 Claude 对）：79 行里 2 处不同 —— 默写时盯住这两处
#    · 截面库文件名：cross_section.xml 少了一个 s → OpenMC 开跑才报「找不到文件」，离出错的那行很远
#    · st.batched = batch（应为 batches）→ 给不存在的属性赋值不报错、悄悄新建（又一次 self.satet），
#      真正的批数没设上
#
#  下面两行是 Claude 加的（不用写）：让这个文件能找到 my_code 里的 lesson08_dose
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
# ============================ 你从这里往下写 ============================
import openmc
from lesson08_dose import MASS_FRAC, RHO,D

openmc.config['cross_sections']='/mnt/e/BNCT_GPU/lib80x_hdf5/cross_sections.xml'
def mater():
    soft=openmc.Material(name='soft tissue')
    Mass_sum=0.0
    for nuc in MASS_FRAC.keys():
        soft.add_nuclide(nuc,MASS_FRAC[nuc],'wo')
        Mass_sum+=MASS_FRAC[nuc]
    soft.set_density('g/cm3',RHO*Mass_sum)
    soft.temperature=294
    return soft

def geom(mat):
    x1=openmc.XPlane(x0=7.3,boundary_type='reflective')
    x2=openmc.XPlane(x0=-7.3,boundary_type='reflective')
    y1=openmc.YPlane(y0=7.3,boundary_type='reflective')
    y2=openmc.YPlane(y0=-7.3,boundary_type='reflective')
    z1=openmc.ZPlane(z0=D,boundary_type='vacuum')
    z2=openmc.ZPlane(z0=0,boundary_type='vacuum')
    bou=-x1&+x2&-y1&+y2&-z1&+z2
    c=openmc.Cell(fill=mat,region=bou)
    geo=openmc.Geometry([c])
    return geo
    
