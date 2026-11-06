# -*- coding: utf-8 -*-
# ============================================================
#  rewrite_load_thermal1.py  --  load_thermal 默写（第 1 次）· 2026-11-06
#  Claude 11/5 收工时开好文件头；你从「你从这里往下写」那一行下面开始写
# ============================================================
#
#  11/5 抄过一遍（抄写历史\copy_load_thermal.py）；今天第一次默写，约 30 行。
#
#  要写：import（默写一律写）· N_MU 那一行常数 · 整个 load_thermal(sab_path, T_tag)，顺序照原文
#  不写：assert · print · if __name__ 整块
#
#  🔴 不看：my_code\thermal.py、抄写历史\copy_load_thermal.py、项目文档\函数解读_10-31至11-01.md 第 4 节
#  不用跑。写完告诉我，我逐行对拍。
#
#  这个函数以前出过的错（盯住，答案不在这里）：
#    · Python 自带的 open 和 h5py 的文件对象混用（10/31、11/1 两次）
#    · 属性用 .attrs[...] 取，而且要在 [:] 之前取（10/31、11/1 两次）
#    · 组上的属性当子组取（11/1）
#    · 取二维数组的一整行：逗号写不写，结果差很多（11/5 抄写时 xs[1:]）
#    · 装 118 张表的列表、装一张表 μ 的列表：各放在哪一层循环外面（纪律第 6 条）
#    · 切片终点是不是又 +1 了（11/1）
#    · 表号当行号（10/31 eout[j0, …]）
# ============================================================
# ============================ 你从这里往下写 ============================
import h5py,numpy as np
N_MU=30
def load_thermal(sab_path,T_tag):
    thermal={}
    with h5py.File(sab_path,"r")as f:
        root=f["c_H_in_H2O"]
        thermal["E_max"]=float(root.attrs["energy_max"])
        xs=root[T_tag]["xs"][:]
        thermal["xs_E"]=xs[0,:]
        thermal["xs_sig"]=xs[1,:]
        dist=root[T_tag]["inelastic/distribution"]
        thermal["E_in"]=dist["energy"][:]
        eout=dist["energy_out"][:]
        offs=dist["energy_out"].attrs["offsets"]
        mu_all=dist["mu"][:]
        n_out=np.diff(np.append(offs,eout.shape[1]))
        thermal["tables"]=[]
        for l in range(len(offs)):
            beg=offs[l]
            end=beg+n_out[l]
            E_out,pdf,cdf=eout[0:3,beg:end]
            mu_beg=eout[4,beg:end].type(int)
            mu_rows=[]
            for k in range(len(mu_beg)):
                mu_rows.append(mu_all[0,mu_beg[k]:mu_beg[k]+N_MU])
            mu_tab=np.array(mu_rows)
            dic={
                "E_out":eout,
                "pdf":pdf,
                "cdf":cdf,
                "mu":mu_tab
            }
            thermal["tables"].append(dic)
    return thermal
