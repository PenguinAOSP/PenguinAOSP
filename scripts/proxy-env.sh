#!/usr/bin/env bash
# PenguinAOSP: 代理环境（下载类脚本统一 source 本文件）
# 用法: source scripts/proxy-env.sh && <下载命令>
# 默认走本机 flclash 混合端口；设置 PENGUIN_NO_PROXY=1 可跳过。

if [ "${PENGUIN_NO_PROXY:-0}" != "1" ]; then
    export http_proxy="${http_proxy:-http://127.0.0.1:7890}"
    export https_proxy="${https_proxy:-http://127.0.0.1:7890}"
    export all_proxy="${all_proxy:-socks5://127.0.0.1:7890}"
fi
