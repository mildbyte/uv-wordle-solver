import toml

PREFIX = "wordle_"
BUILD_BACKEND = toml.loads("""
[build-system]
requires = ["uv_build>=0.7.19,<0.8.0"]
build-backend = "uv_build"
""")
