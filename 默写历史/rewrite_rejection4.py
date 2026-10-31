# ============================================================
#  rewrite_rejection4.py —— 默写 sample_rejection（第 4 次，10/30）
#  2026-10-29 Claude 开文件，只写了这段注释；下面全部由你写
# ============================================================
#  要写：
#    1. import + 最多轮数那个常数
#    2. sample_rejection(f, g, g_sample, M, rng)：舍选法抽一个样本 → 返回 (x, 第几轮接受)；撞满返回 None
#       （9/27 你定的 5 个设计决定照旧：g 和 g_sample 分开传、rng 由调用方传、接受条件严格 <、返回 k+1、撞满 None）
#  不写：assert、if __name__ == "__main__": 那一行和下面整块、print
#  不看：my_code\whiteboard_08_rejection.py、默写历史\rewrite_rejection1.py、rewrite_rejection2.py、rewrite_rejection3.py
#  写完：存盘，告诉 Claude，Claude 代对拍（两组 f × 2 万次 + 撞满那一种，逐位比 + 发生器状态）
# ============================================================
Max=1000
def sample_rejection(f,g,g_sample,m,rng):
    for k in range(Max):
        x=g_sample(rng)
        if f(x)>g(x)*m*rng.random():
            return x,k+1
    else:
        return None
