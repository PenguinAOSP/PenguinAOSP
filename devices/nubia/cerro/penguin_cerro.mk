#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#
# PenguinAOSP — Nubia Z60 Ultra (cerro)
# Lunch: penguin_cerro-cp2a-userdebug
# Base: UwUAOSP 17 (vendor/uwu/config/common.mk), device layer from
# nubia-sm8650-devs lineage-23.2 + RisingOS cerro optimizations (see
# docs/features/dt01-cerro-device-layer.md).
#
# UWU_DEVICE_TYPE / UWU_SUPPORTS_TELEPHONY are declared in device.mk
# (must come before the vendor/uwu/config/common.mk inherit below).
#

# PenguinOS: UwU gates BoardConfigUwU.mk / sepolicy / product overrides on
# UWU_BUILD. Upstream only auto-derives it from uwu_* PRODUCT_NAME; our lunch
# target is penguin_cerro, so set it before any inherit (also patched into
# build/make/core/config.mk for penguin_* via PENGUIN_UWU_BUILD_PREFIX).
UWU_BUILD := cerro

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit from device.
$(call inherit-product, device/nubia/cerro/device.mk)

# PenguinOS: UwU common product layer (single entry point, see
# vendor/uwu/config/README.md).
$(call inherit-product, vendor/uwu/config/common.mk)

# Boot animation
TARGET_SCREEN_HEIGHT := 2480
TARGET_SCREEN_WIDTH := 1116

PRODUCT_BRAND := nubia
PRODUCT_DEVICE := cerro
PRODUCT_MANUFACTURER := nubia
PRODUCT_MODEL := NX721J
PRODUCT_NAME := penguin_cerro
PRODUCT_SYSTEM_DEVICE := PQ83A01
PRODUCT_SYSTEM_NAME := PQ83A01-UN

PRODUCT_GMS_CLIENTID_BASE := android-zte

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="PQ83A01-UN PQ83A01 15 AQ3A.240812.002 20250916.013811 release-keys" \
    BuildFingerprint=nubia/PQ83A01-UN/PQ83A01:15/AQ3A.240812.002/20250916.013811:user/release-keys \
    DeviceName=$(PRODUCT_SYSTEM_DEVICE) \
    DeviceProduct=$(PRODUCT_SYSTEM_NAME)
