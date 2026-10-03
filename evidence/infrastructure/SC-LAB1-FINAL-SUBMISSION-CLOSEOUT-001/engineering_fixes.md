# 本轮工程适配记录

1. 权威旧Process PDF为0444，直接copyfile报PermissionError。输入和旧件已在仓库外保护；使用同目录临时文件加os.replace原子替换，旧件保留history确切字节。没有修改成品源。

2. 独立检查发现teacher README把外部历史FULL证据误写成Notebook保存输出。两个Notebook实际12/8代码单元全部count=null，outputs=0；保护首个候选后仅改README说明并重建、重做实包检查，不修改Notebook。

3. 发布前不加范围的git diff --cached --check对新增镜像的原始数据、作者源和真实日志报告既有行尾空白。未格式化或改动这些受保护字节；对实际编写的代码/说明/元数据执行专项diff检查通过，全部staged内容另作秘密/字体/文件大小与ZIP检查。

4. 独立代码核验要求远程回读的“无本地对象借用”说明有实际约束。已在包外辅助脚本清除Git对象/工作目录继承变量，核验bare/origin，并在fetch前后检查alternates；三项错误origin/外部对象借用夹具均在网络fetch前拒绝。独立复核通过，实际远程回读另行登记。
