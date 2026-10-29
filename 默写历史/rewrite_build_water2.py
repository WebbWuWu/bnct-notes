# ============================================================
#  rewrite_build_water2.py —— 默写 build_water（第 2 次，10/29）
#  2026-10-28 Claude 开文件，只写了这段注释；下面全部由你写
#  🔴 第 1 次（10/28 看着写的）错 5 处：mts=[] 应为 mts1=[] · Q1.append[...] 方括号调用 · 字典里 mts / Q 应为 mts1 / Q1 · 少 "awr" 键 · sorted(len(...)) 漏 range
#     → 筛过的叫 mts1、XS1、Q1，往后所有地方都用带 1 的那个
#  放在 E:\BNCT_GPU\默写历史\ 下（10/28 起）：要 import my_code 里的模块，下面两行是 Claude 加的（不计分）
# ============================================================
#  要写：
#    1. import（只写 build_water 真用到的；默写仍写 import，9/28 规矩）
#    2. 三个常数：rho_w、share_B、nucs_w
#    3. build_water(E_keep)，四块：
#       ① 每个核素读截面（load_nuclide）+ MT=301（load_heating），装进 stodic[核素]
#       ② 质量份额：H、O 按水分子质量占比 × (1 − share_B)；B10 = share_B
#       ③ 每个核素：筛道 → 数密度 → 读 kT → 拼核素字典（9 个键）→ 在 0.0253 eV 处排 order
#       ④ return nuclides, order
#  不写：assert、if __name__ == "__main__": 那一行和下面整块、print
#  不计分：字典里的键名照抄也行（"Q_value"、"kT" 这些是名字）
#  不看：lesson11_water.py、抄写历史\copy_build_water.py、默写历史\rewrite_build_water1.py
#  写完：存盘，告诉 Claude，Claude 代对拍（没有 h5py，只做逐行读 + 份额 / 数密度用真数代算）
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
# ============================ 你从这里往下写 ============================
from xs_lookup import load_nuclide,find_cell
from lesson07_freegas import load_kT
from lesson11_mt301 import load_heating
import numpy as np
from lesson08_dose import T,M_N,N_A
import os

rho_w=0.998
share_B=15e-6
nucs_w=["H1","O16","B10"]

def build_water(E_keep):
    stodic={}
    for nuc in nucs_w:
        E,mts,XS,awr,Q=load_nuclide(nuc,T)
        _,heat=load_heating(nuc,T)
        stodic[nuc]={
            "E":E,
            "mts":mts,
            "XS":XS,
            "awr":awr,
            "Q":Q,
            "heat":heat
        }
    M_H=M_N*stodic["H1"]["awr"]
    M_O=M_N*stodic["O16"]["awr"]
    M_water=1*M_O+2*M_H
    frac={
        "H1":2*M_H/M_water*(1-share_B),
        "O16":M_O/M_water*(1-share_B),
        "B10":share_B
    }
    nuclides=[]
    order=[]
    for nuc in nucs_w:
        keys=["E","mts","XS","awr","Q","heat"]
        E1,mts1,XS1,awr1,Q1,heat1=[stodic[nuc][i] for i in keys]
        mts2=[]
        XS2=[]
        Q2=[]
        for i in range(len(XS1)):
            if np.any(XS1[i][E1<E_keep]>0):
                XS2.append(XS1[i])
                mts2.append(mts1[i])
                Q2.append(Q1[i])
        dens=frac[nuc]*rho_w*N_A/awr1/M_N
        kT=load_kT(nuc,T)
        dic={
            "E":E1,
            "mts":mts2,
            "XS":XS2,
            "awr":awr1,
            "Q":Q2,
            "heat":heat1,
            "name":nuc,
            "dens":dens,
            "kT":kT
        }
        loa_e=find_cell(E1,0.0253)
        nuclides.append(dic)
        order.append(sorted(range(len(mts2)),key=lambda t:XS2[t][loa_e],reverse=True))
    return nuclides,order
