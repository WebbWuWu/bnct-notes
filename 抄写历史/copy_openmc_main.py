# -*- coding: utf-8 -*-
# ============================================================
#  copy_openmc_main.py  --  OpenMC 主流程抄写稿（11/1 抄；默写（1）11/2）
#  Claude 2026-11-01 开好文件头；从「你从这里往下写」那一行下面开始，照原文手敲
# ============================================================
#
#  照着抄的原文：my_code\lesson09_openmc.py
#    · 第 18 行          openmc.config[...] = 截面库路径
#    · 第 22–73 行       mater / geom / kur / mesh
#    · 第 96–134 行      run / tallies
#  约 90 行。lesson11_openmc.py 的水模体跑法就是 import 这几个函数（第 2 行），所以这就是「那一套」主流程。
#
#  要写：上面三段，顺序照原文
#  不写：import（10/27 定）· 第 8–16 行 KUR_TALLIES 清单 · 第 19–20 行 path1 · 第 75–94 行 tally / tru_tally
#        （和 lesson11 的 water_tally 同一个结构，看一眼就行）· if __name__ 整块 · assert · print
#  不用跑：Windows 的 openmc 环境里没有 OpenMC，跑了在第一行 import 就报错。抄完告诉我，我在我这边逐行和原文对。
#
#  ─────────────────────────────────────────────────────────────
#  用到的写法逐个回顾（10/27 定：用过的也讲一遍；例子和项目无关）
#  ─────────────────────────────────────────────────────────────
#  【截面库】
#    · openmc.config['cross_sections'] = 路径：告诉 OpenMC 去哪找 cross_sections.xml（库的目录表）。
#        这里是 Linux 路径 /mnt/e/...，因为 OpenMC 只在 WSL 里跑。
#  【mater：材料】
#    · openmc.Material(name='...')：建一个材料，name 是自己起的标签，OpenMC 不认它的意思
#    · 材料.add_nuclide(核素名, 份额, 'wo')：'wo' = 质量份额，'ao' = 原子份额
#        例：碳钢 st.add_nuclide('Fe56', 0.98, 'wo'); st.add_nuclide('C12', 0.02, 'wo')
#    · 材料.set_density('g/cm3', 数)：密度；单位字符串必须是 OpenMC 认的那几个
#    · 材料.temperature = 294：温度，K（截面按这个温度取；和你程序的 "294K" 对上）
#    · 字典.keys()：取全部键。for nuc in MASS_FRAC.keys() 就是挨个拿核素名
#  【geom：几何】
#    · openmc.XPlane(x0=7.3, boundary_type='reflective')：平面 x = 7.3。YPlane / ZPlane 同理（参数 y0 / z0）
#        boundary_type：'reflective' 反射（碰到就镜面弹回）· 'vacuum' 真空（出去就丢掉）
#    · -面 = 这个面的负侧（x < x0）；+面 = 正侧（x > x0）；& = 两个区域取交集
#        例：-openmc.XPlane(x0=3.5) & +openmc.XPlane(x0=-3.5) 就是 −3.5 < x < 3.5 这一片
#    · openmc.Cell(fill=材料, region=区域)：一个「区域里装着这种材料」的单元
#    · openmc.Geometry([单元列表])：整个几何；列表，哪怕只有一个单元也要方括号
#  【kur：源能谱】
#    · kur_table()：lesson08_dose 里你写的，返回 (edges, shares)：11 个箱边界、10 个份额
#    · 每个箱再切 M = 50 份，按「等比」切：r = (上界/下界)^(1/M)，第 m 个边界 = 下界 × r^(m − i·M)
#        例：从 1 切到 16、切 4 份，r = 16^(1/4) = 2 → 1, 2, 4, 8, 16
#        你犯过：下标只在第一个箱对（m − i vs m − i·M，i = 0 是特殊值，10/13）
#    · [0.0] * n：长 n、全是 0.0 的列表（先占好位置，后面按下标填）
#    · int(j / M)：第 j 个小箱属于第几个大箱。例：M = 50，j = 137 → 2
#    · 列表.append(0.0)：在末尾放一个元素
#    · openmc.stats.Tabular(x, p, interpolation="histogram")：分段常数的分布；x 是边界，p 是每段的概率密度
#        histogram 时 p 要和 x 一样长，最后一个 p 用不到 —— 所以 dens 末尾补一个 0
#  【mesh：分层计数】
#    · openmc.RegularMesh()：规则网格；.dimension = [nx, ny, nz] 每个方向几格
#        .lower_left / .upper_right = 网格的两个对角点
#        例：一个 2 × 2 × 10 的网格，从 (0,0,0) 到 (4,4,20)，每格 2 × 2 × 2 cm
#    · openmc.MeshFilter(网格)：把计数按网格的每一格分开记
#  【run：写输入、跑】
#    · os.makedirs(目录, exist_ok=True)：建目录；已经有了也不报错
#    · openmc.Materials([材料])：材料集合（注意复数，和单个 Material 不是一个东西）
#    · openmc.stats.Point((x, y, z))：点源位置；openmc.stats.Monodirectional((u, v, w))：单一方向
#    · openmc.IndependentSource(space=位置, angle=方向, energy=能量分布)：把三样拼成一个源
#    · openmc.Settings()：运行设置；.run_mode = 'fixed source'（固定源，不是临界计算）
#        .particles = 每一批多少个粒子 · .batches = 批数 · .seed = 种子 · .source = 源
#    · 对象.export_to_xml(路径)：写成 OpenMC 读的 xml 输入文件
#    · os.path.join(目录, 文件名)：拼路径。你犯过：字符串直接相加，少斜杠（10/14 两次）
#    · openmc.run(cwd=目录)：在这个目录里启动 OpenMC
#    · 'statepoint.' + str(batch) + '.h5'：OpenMC 跑完写的结果文件名，数字 = 批数
#        str(数)：数字变字符串，才能和字符串相加。例：'第' + str(3) + '章' → '第3章'
#  【tallies：读结果】
#    · with openmc.StatePoint(路径) as sp：打开结果文件，缩进块结束自动关
#    · sp.get_tally(name='...')：按 tally 的 name（你自己起的标签）取。你混过：name vs scores（10/14）
#    · tally.mean / tally.std_dev：均值、标准误，多维 numpy 数组。你写错过：std.dev（10/14）
#    · 数组.flatten()：拍平成一维。例：[[1, 2], [3, 4]] → [1, 2, 3, 4]
#    · 数组.tolist()：numpy 数组 → Python 列表（json 存不了 numpy 数组）。你写错过：少括号 .tolist（10/14）
#    · return m2, s2：返回两个东西，调用方用 m, s = tallies(...) 接
#
#  抄的时候想清楚四件事（今晚老师问答会问其中一两件）：
#    1. geom 里 x、y 四个面用反射、z 两个面用真空。这块几何在模拟什么？横向为什么不用真空？（提示：你的程序是几维的）
#    2. mater 里密度写的是 RHO × MASS_sum，不是 RHO。MASS_FRAC 五个份额加起来是多少？为什么要乘它？
#    3. kur 里每个箱按「等比」切 50 份、每份分到同样的份额。这等于假设箱里的能谱是什么形状？（近似 #19）改成等差切又是什么假设？
#    4. run 里源放在 z = 1e-6，不放在 0。放在 0 正好在真空面上，可能出什么事？
#
#  下面四行是 Claude 加的（不用抄）：路径 + 函数要用的 import（抄写不抄 import）
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
from lesson08_dose import MASS_FRAC, RHO, D, kur_table, NL
import openmc
# ============================ 你从这里往下写 ============================
openmc.config['cross_sections']="/mnt/e/BNCT_GPU/lib80x_hdf5/cross_section.xml"

def mater():
    soft=openmc.Material(name='soft tissue')
    MASS_sum=0.0
    for nuc in MASS_FRAC.keys():
        soft.add_nuclide(nuc,MASS_FRAC[nuc],'wo')
        MASS_sum+=MASS_FRAC[nuc]
    soft.set_density('g/cm3',RHO*MASS_sum)
    soft.temperature=294
    return soft

def geom(mat):
    xp1=openmc.XPlane(x0=7.3,boundary_type='reflective')
    xp2=openmc.XPlane(x0=-7.3,boundary_type='reflective')
    yp1=openmc.YPlane(y0=7.3,boundary_type='reflective')
    yp2=openmc.YPlane(y0=-7.3,boundary_type='reflective')
    zp1=openmc.ZPlane(z0=D,boundary_type='vacuum')
    zp2=openmc.ZPlane(z0=0,boundary_type='vacuum')
    bou=-xp1&+xp2&-yp1&+yp2&-zp1&+zp2
    c=openmc.Cell(fill=mat,region=bou)
    geo=openmc.Geometry([c])
    return geo

def kur():
    edges,shares=kur_table()
    M=50
    edges1=[0.0]*((len(edges)-1)*M+1)
    shares1=[0.0]*(len(shares)*M)
    dens=[0.0]*(len(shares)*M)
    edges1[0]=edges[0]
    for i in range(len(edges)-1):
        r=(edges[i+1]/edges[i])**(1/M)
        for m in range(i*M+1,(i+1)*M+1):
            edges1[m]=edges[i]*r**(m-i*M)
    for j in range(len(shares1)):
        shares1[j]=shares[int(j/M)]/M
        dens[j]=shares1[j]/(edges1[j+1]-edges1[j])
    dens.append(0.0)
    dsp=openmc.stats.Tabular(edges1,dens,interpolation="histogram")
    return dsp

def mesh():
    grid=openmc.RegularMesh()
    grid.dimension=[1,1,NL]
    grid.lower_left=[-7.3,-7.3,0]
    grid.upper_right=[7.3,7.3,D]
    filt=openmc.MeshFilter(grid)
    return filt

def run(E_dis,tal,inp,batch,n_bat,mat,seed=1):
    os.makedirs(inp,exist_ok=True)
    material=openmc.Materials([mat])
    geo=geom(mat)
    pos=openmc.stats.Point((0,0,1e-6))
    dirn=openmc.stats.Monodirectional((0,0,1))
    S=openmc.IndependentSource(space=pos,angle=dirn,energy=E_dis)
    st=openmc.Settings()
    st.run_mode='fixed source'
    st.particles=n_bat
    st.batched=batch
    st.seed=seed
    st.source=S
    path2=os.path.join(inp,'materials.xml')
    path3=os.path.join(inp,'geometry.xml')
    path4=os.path.join(inp,'settings.xml')
    path5=os.path.join(inp,'tallies.xml')
    material.export_to_xml(path2)
    geo.export_to_xml(path3)
    st.export_to_xml(path4)
    tal.export_to_xml(path5)
    openmc.run(cwd=inp)
    path6=os.path.join(inp,'statepoint.'+str(batch)+'.h5')
    return path6

def tallies(path,name1):
    with openmc.StatePoint(path)as sp:
        t2=sp.get_tally(name=name1)
        m=t2.mean
        s=t2.std_dev
        m1=m.flatten()
        m2=m1.tolist()
        s1=s.flatten()
        s2=s1.tolist()
    return m2,s2
