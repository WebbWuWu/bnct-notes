# -*- coding: utf-8 -*-
# ============================================================
#  copy_load_thermal.py  --  load_thermal 抄写稿（11/5 抄；默写放 11/6）
#  Claude 2026-11-05 开好文件头；从「你从这里往下写」那一行下面开始，照原文手敲
# ============================================================
#
#  照着抄的原文：my_code\thermal.py 第 23–54 行（def load_thermal 到 return thermal）
#  约 30 行。
#
#  要写：整个函数，顺序照原文
#  不写：import（10/27 定）· assert · print · if __name__ 整块
#  抄的时候边抄边想（不用写下来）：
#    · 哪几行在读「截面」（给 lookup_xs 用），哪几行在读「出射分布」（给 sample_thermal 用）
#    · offsets 在哪个数据集的属性上；第几行是 μ 表起点
#    · 为什么 μ 那一层要再套一个循环（每个出射点 20 个 μ）
# ============================================================
import h5py,numpy as np
N_MU=20
# ===== 你从这里往下写 =====
def load_thermal(sab_path,T_tag):
    thermal={}
    with h5py.File(sab_path,"r")as f:
        root=f["c_H_in_H2O"]
        thermal["E_max"]=float(root.attrs["energy_max"])
        xs=root[T_tag]["inelastic/xs"][:]
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
            mu_beg=eout[4,beg:end].astype(int)
            mu_rows=[]
            for k in range(len(mu_beg)):
                mu_rows.append(mu_all[0,mu_beg[k]:mu_beg[k]+N_MU])
            mu_tab=np.array(mu_rows)
            dic={
                "E_out":E_out,
                "pdf":pdf,
                "cdf":cdf,
                "mu":mu_tab
            }
            thermal["tables"].append(dic)
    return thermal
