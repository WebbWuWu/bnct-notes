# ============================================================
#  rewrite_tally4.py —— 抄写现在的 run_slab（第 7 课 + 第 8 课，全函数）
#  2026-10-11 Claude 开文件；20:14 用户改「默写」为「抄写」（第 7 课版本没学过，
#  先抄后默），这段注释 22:40 由 Claude 按此改写。下面的代码由你抄。
# ============================================================
#  照 lesson07_freegas.py 抄：
#    1. 第 197–203 行：import + 模块级常数（Max、wt_lo、wt_hi、Q_val）
#       （以及 run_slab 用到、在它上面定义的东西 —— 抄的时候看到一个就 import 一个）
#    2. 第 205–530 行：整个 run_slab，assert 也抄（学的阶段认真看每条抓什么）
#  抄的时候盯住「每个变量在哪一层」：函数开头 / 历史开头 / 步循环 / 拆层循环 / 历史结束
#  10/11 抄到 ind_102=[] 为止；10/12 上课先看、晚上接着抄完
#  ⚠️ 已抄部分 Claude 看到两处和原文不同，抄完时自己对一遍：
#     签名第一个参数（大小写）；函数开头那几条 assert 没抄
#  抄完：存盘，告诉 Claude，同种子 + 假截面库逐位对拍
#  默写：抄完至少隔一天，分段默（日期 10/12 收工排）
# ============================================================
def run_slab(N,seed,d,nuclides,E_src,order,z_src=None,t_cut=None,implicit=False,NL=20,src=None):
    if z_src is None:
        z_src=d/2
    E_cut=[]
    len_nuc=len(nuclides)
    ind_B=None
    ind_N=None
    ind_102=[]
    for j in range(len_nuc):
        if nuclides[j]["name"]=="B10":
            ind_B=j
            loca_800=nuclides[j]["mts"].index(800)
            loca_801=nuclides[j]["mts"].index(801)
            Q_800=nuclides[j]["Q_value"][loca_800]
            Q_801=nuclides[j]["Q_value"][loca_801]
        if nuclides[j]["name"]=="N14":
            ind_N=j
            loca_600=nuclides[j]["mts"].index(600)
            Q_600=nuclides[j]["Q_value"][loca_600]
        loca_102=nuclides[j]["mts"].index(102)
        ind_102.append(loca_102)
    rng=lcg(seed)
    if src!=None:
        edges,shares=src
        cdf=make_cdf(shares)
    n_T=0
    n_ki=0
    n_R=0
    n_A=0
    nt_w=0
    nr_w=0
    n_stuck=0
    n_i=0
    nt_cut=0
    n_sd=0
    dz=d/NL
    track_sum=[0.0]*NL
    track_sq=[0.0]*NL
    Br_sum=[0.0]*NL
    Br_sq=[0.0]*NL
    Bc_sum=[0.0]*NL
    Bc_sq=[0.0]*NL
    Nc_sum=[0.0]*NL
    Nc_sq=[0.0]*NL
    ag_sum=[0.0]*NL
    ag_sq=[0.0]*NL
    DH_sum=[0.0]*NL
    DH_sq=[0.0]*NL
    v_sum=v_sq=0.0
    tol_sigt_all=0.0
