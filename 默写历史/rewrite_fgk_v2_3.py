# ============================================================
#  rewrite_fgk_v2_3.py —— 默写 free_gas_kinematics 精简版（第 2 次，10/30）
#  2026-10-29 Claude 开文件，只写了这段注释和下面两行路径；下面全部由你写
#  第 1 次（10/25，rewrite_fgk_v2_2.py）对拍 8/8 过
# ============================================================
#  要写：
#    1. import（函数本身用得到的才写）
#    2. dot(a, b)、norm(a)
#    3. free_gas_kinematics(E, u, v, w, A, kT, x, mu_T, rng) → 返回 E', u', v', w'
#       步骤（只给步名，想不起来的空着写 # ?）：
#         0 中子方向 d、算 y   1 中子速度
#         2a 抽辅助方向、去掉沿中子方向的部分（最多 100 轮，够长就停）
#         2b 归一化成 e1   2c 靶核方向   2d 靶核速度   3 质心速度
#         4 CM 里的中子速度和速率   5+6 CM 里各向同性抽新方向，回 LAB → E' 和新方向
#  不写：assert、if __name__ == "__main__": 那一行和下面整块、print；2a 的 for…else 整块不写
#  不看：抄写历史\copy_fgk_v2.py、默写历史\rewrite_fgk_v2_1.py、rewrite_fgk_v2_2.py、rewrite_fgk1.py、
#        my_code\lesson07_freegas.py、项目文档\讲解_free_gas_kinematics.md
#  写完：存盘，告诉 Claude，Claude 代对拍（同输入同种子，四个返回值 + 发生器状态逐位比）
#  ⚠️ 10/30 你若先把 rng.py 换成乙，对拍用的发生器跟着变 —— 不影响「逐位比」，两边用同一个 rng
# ============================================================
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "my_code"))
# ============================ 你从这里往下写 ============================
from rng import isotropic_direction
import math

def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def norm(a):
    return math.sqrt(a[0]**2+a[1]**2+a[2]**2)

def free_gas_kinematics(E,u,v,w,A,kT,x,mu_T,rng):
    d=(u,v,w)
    y=math.sqrt(E*A/kT)
    vn=[d[i]*y for i in range(3)]
    for j in range(100):
        p=isotropic_direction(rng)
        r=[p[i]-dot(d,p)*d[i] for i in range(3)]
        if norm(r)>1e-6:
            break
    el=[r[i]/norm(r) for i in range(3)]
    st=math.sqrt(1-mu_T**2)
    rb=[mu_T*d[i]+st*el[i] for i in range(3)]
    vb=[rb[i]*x for i in range(3)]
    vcm=[(vn[i]+A*vb[i])/(1+A) for i in range(3)]
    vcn=[vn[i]-vcm[i] for i in range(3)]
    q=isotropic_direction(rng)
    vl=[vcm[i]+q[i]*norm(vcn)for i in range(3)]
    L=norm(vl)
    return kT/A*L**2,vl[0]/L,vl[1]/L,vl[2]/L
