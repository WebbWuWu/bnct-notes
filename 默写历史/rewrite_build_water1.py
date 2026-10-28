# ============================================================
#  rewrite_build_water1.py —— 默写 build_water（第 1 次，10/28）
#  2026-10-27 Claude 开文件，只写了这段注释；下面全部由你写
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
#  不看：lesson11_water.py、whiteboard\copy_build_water.py
#  写完：存盘，告诉 Claude，Claude 代对拍（没有 h5py，只做逐行读 + 份额 / 数密度用真数代算）
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
# ============================ 你从这里往下写 ============================
from xs_lookup import load_nuclide,find_cell
from lesson07_freegas import load_kT,run_slab
from lesson11_mt301 import load_heating
import numpy as np
from lesson08_dose import T,M_N,N_A,kur_table,KEEP_FACTOR
import os,time
from lesson08_dose import save_result,load_result,D,NL,N,SEED,OUT_DIR

rho_w=0.998
share_B=15e-6
nucs_w=["H1","O16","B10"]

def build_water(E_keep):
    stodic={}
    for nuc in nucs_w:
        E1,mts1,XS1,awr1,Q1=load_nuclide(nuc,T)
        E2,heat2=load_heating(nuc,T)
        stodic[nuc]={
            "E":E1,
            "mts":mts1,
            "XS":XS1,
            "awr":awr1,
            "Q":Q1,
            "heat":heat2
        }
    M_H=M_N*stodic["H1"]["awr"]
    M_O=M_N*stodic["O16"]["awr"]
    M_water=2*M_H+M_O
    share_H=M_H*2/M_water*(1-share_B)
    share_O=M_O/M_water*(1-share_B)
    frac={
        "H1":share_H,
        "O16":share_O,
        "B10":share_B
    }
    nuclides=[]
    order=[]
    for nuc in nucs_w:
        keys=["E","mts","XS","awr","Q","heat"]
        E,mts,XS,awr,Q,heat=[stodic[nuc][k] for k in keys]
        mts1=[]
        XS1=[]
        Q1=[]
        for i in range(len(XS)):
            if np.any(XS[i][E<E_keep]>0):
                mts1.append(mts[i])
                XS1.append(XS[i])
                Q1.append(Q[i])
        dens=frac[nuc]*rho_w*N_A/awr/M_N
        kT=load_kT(nuc,T)
        dirc={
            "E":E,
            "mts":mts1,
            "XS":XS1,
            "awr":awr,
            "Q_value":Q1,
            "name":nuc,
            "dens":dens,
            "kT":kT,
            "heat":heat
        }
        loa_e=find_cell(E,0.0253)
        order.append(sorted(range(len(mts1)),key=lambda t:XS1[t][loa_e],reverse=True))
        nuclides.append(dirc)
    return nuclides,order
