#!/usr/bin/env bash
# 编译前解除 shell 侧资源上限（source 本脚本，不要直接 bash 执行期望留下函数）
set +e
ulimit -v unlimited
ulimit -m unlimited
ulimit -s unlimited
ulimit -c unlimited
ulimit -n 1048576
ulimit -l unlimited 2>/dev/null || ulimit -l 16777216 2>/dev/null || true
set -e

# Soong bootstrap 勿传 -j（会写进 SOONG_UI_NINJA_ARGS 导致 soong_build 异常退出）
unset SOONG_UI_NINJA_ARGS
unset NINJA_ARGS

penguin_build() {
  if command -v prlimit >/dev/null 2>&1; then
    prlimit --as=unlimited --rss=unlimited --stack=unlimited -- "$@" \
      || prlimit --as=unlimited --rss=unlimited -- "$@" \
      || "$@"
  else
    "$@"
  fi
}
