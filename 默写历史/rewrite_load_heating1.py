# ============================================================
#  rewrite_load_heating1.py —— 默写 load_heating（第 1 次，10/28）
#  2026-10-27 Claude 开文件，只写了这段注释；下面全部由你写
#  放在 E:\BNCT_GPU\默写历史\ 下（10/28 起）：要 import my_code 里的模块，下面两行是 Claude 加的（不计分）
# ============================================================
#  要写：
#    1. import（函数真用到的）
#    2. load_heating(nuc, T)：读一个核素的 MT=301 加热数
#       打开 HDF5 → 能量网格 E → reaction_301 的 xs 和 threshold_idx → 前面补 0 拼成和 E 一样长 → return E, heat
#  不写：assert、if __name__ == "__main__": 那一行和下面整块、print；show_mt301 不写
#  不看：lesson11_mt301.py、xs_lookup.py
#  写完：存盘，告诉 Claude，Claude 代对拍（没有 h5py，只做逐行读）
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
# ============================ 你从这里往下写 ============================
from xs_lookup import LIB
import h5py
import numpy as np
def load_heating(nuc,T):
    path=os.path.join(LIB,nuc+".h5")
    with h5py.File(path,"r")as f:
        root=f[nuc]
        E=root["energy"][T][:]
        xs301=root["reactions"]["reaction_301"][T]["xs"][:]
        thi_301=int(root["reactions"]["reaction_301"][T]["xs"].attrs["threshold_idx"])
        heat=np.zeros(len(E))
        heat[thi_301:]=xs301
    return E,heat
