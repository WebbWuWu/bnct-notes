# ============================================================
#  rewrite_interp3.py —— 默写 interp 三个（第 3 次，10/25）：find · interp_loglog · number_density
#  2026-10-18 Claude 开文件（10/18 晚改名为第 3 次用），只写了这段注释；下面全部由你写
# ============================================================
#  要写：
#    1. import（要哪些自己想；函数本身用不到的就不写）
#    2. 三个常数 NA、M_N、RHO（名字和数值）
#    3. find（在能量表里找 e 落在哪一格，返回左端下标；两头越界怎么办）
#    4. interp_loglog（log-log 插值）
#    5. number_density（质量份额 + awr → 数密度）
#  不写：assert、if __name__ == "__main__": 那一行和下面整块、print
#  不看：copy_interp3.py、rewrite_interp1.py、lesson05_tissue_scaffold.py、whiteboard_05_rewrite.py、
#        whiteboard\whiteboard_05_scaffold.py、讲解_interp三个.md
#  写完：存盘，把文件名发给 Claude 对拍（同一组输入跑原函数和你的函数，逐位比）
# ============================================================
