import builtins

# 确保在未运行 gettext.install 时 _ 函数有安全的默认回退，避免单元测试 NameError
if '_' not in builtins.__dict__:
    builtins.__dict__['_'] = lambda s: s
