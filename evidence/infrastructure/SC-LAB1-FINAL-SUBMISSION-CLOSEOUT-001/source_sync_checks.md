# 本轮 Project Sources 交接

当前上传集合由sources.json计算为15项；仅两件Process改变，其余13件与基线同字节。正向同步、check、再同步和再次check均通过，重复执行没有修改bundle字节或mtime。

根目录/release中的新输入不证明ChatGPT UI已上传。本轮UI状态USER_CONFIRMATION_REQUIRED；此前USER_REPORTED_UPDATED仅绑定旧版本。用户若已上传当前hash的新两件，不需要再次上传。否则仅逐一替换Process PDF/ZIP。Project Settings保持，无需重贴。

详细hash和命令见[source_sync_receipt.json](source_sync_receipt.json)；release仅含批准15项，不含教师ZIP、检查器、回执或设置。
