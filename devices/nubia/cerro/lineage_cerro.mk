#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#
# RisingOS 9 (seventeen) — Nubia Z60 Ultra (cerro)
# Lunch: lineage_cerro-cp2a-userdebug / riseup cerro userdebug
# First bringup: VANILLA UNOFFICIAL (WITH_GMS := false)
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit from device.
$(call inherit-product, device/nubia/cerro/device.mk)

# Inherit some common Lineage stuff (RisingOS injects from here).
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# RisingOS 9 — VANILLA UNOFFICIAL (About phone #非官方)
WITH_GMS := false
RISING_MAINTAINER := Artist Rong

# Boot animation
TARGET_SCREEN_HEIGHT := 2480
TARGET_SCREEN_WIDTH := 1116

PRODUCT_BRAND := nubia
PRODUCT_DEVICE := cerro
PRODUCT_MANUFACTURER := nubia
PRODUCT_MODEL := NX721J
PRODUCT_NAME := lineage_cerro
PRODUCT_SYSTEM_DEVICE := PQ83A01
PRODUCT_SYSTEM_NAME := PQ83A01-UN

PRODUCT_GMS_CLIENTID_BASE := android-zte

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="PQ83A01-UN PQ83A01 15 AQ3A.240812.002 20250916.013811 release-keys" \
    BuildFingerprint=nubia/PQ83A01-UN/PQ83A01:15/AQ3A.240812.002/20250916.013811:user/release-keys \
    DeviceName=$(PRODUCT_SYSTEM_DEVICE) \
    DeviceProduct=$(PRODUCT_SYSTEM_NAME)
