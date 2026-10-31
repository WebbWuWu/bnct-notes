# ============================================================
#  rewrite_xs_lookup3.py —— 默写 xs_lookup 四个函数（第 3 次，10/27，从 10/28 拉来）
#  2026-10-27 Claude 开文件，只写了这段注释；下面全部由你写
#  放在 whiteboard\ 下：这个文件只用标准库 + numpy + h5py
# ============================================================
#  要写：
#    1. import + 两个常数：LIB（截面库目录）、BARN
#    2. load_nuclide(nuc, T)：读一个核素 → 返回 E, mts, XS, awr, Q（跳过 redundant 的道；按阈值下标补 0）
#    3. xs_at(E, s, e, lo)：一个道在 e 处线性插值
#    4. find_cell(E, e)：e 落在第几个格子（含 e == E[-1] 的特殊情况）
#    5. sigma_at(E, XS, e)：所有道在 e 处的截面列表 + 总截面
#  不写：assert、if __name__ == "__main__": 那一行和下面整块、print
#  不计分：NUC、T、E_TEST 这几个只给 __main__ 用的常数（写不写都行）
#  不看：xs_lookup.py、copy_xs_lookup.py、讲解_xs_lookup.md、lesson11_mt301.py、rewrite_xs_lookup2.py
#  写完：存盘，告诉 Claude，Claude 代对拍（假库查值逐位比；load_nuclide 没有 h5py，只做逐行读）
# ============================================================
