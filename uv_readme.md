# 常见命令
```sh
uv venv

# 安装开发依赖
uv pip install -r requirements.txt

# 导出当前环境
uv pip freeze > requirements.txt

# 锁依赖
uv pip compile pyproject.toml

# 同步依赖
uv pip sync requirements.txt

# 卸载
uv pip uninstall requirements.txt

# 启动项目
uv run main.py
```