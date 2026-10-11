#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from nubia sm8650-common
$(call inherit-product, device/nubia/sm8650-common/common.mk)

DEVICE_PATH := device/nubia/cerro

# PenguinOS: uwuAOSP bringup flags (docs/bringup-17)
UWU_DEVICE_TYPE := phone
UWU_SUPPORTS_TELEPHONY := true
UWU_MAINTAINER := ycrrongos

# PenguinOS: PenguinLaboratory (penguinOS feature hub, see docs/penguinos-feature-inventory.md)
PRODUCT_PACKAGES += \
    PenguinLaboratory

# Audio
PRODUCT_COPY_FILES += \
    $(DEVICE_PATH)/audio/mixer_paths_pineapple_mtp.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio/sku_pineapple/mixer_paths_pineapple_mtp.xml

# Soong
PRODUCT_SOONG_NAMESPACES += \
    $(DEVICE_PATH)

# Overlays
# PenguinOS: SystemUIResCerro (UDC software protection RRO) intentionally dropped
PRODUCT_PACKAGES += \
    SettingsProviderResCerro \
    LineageSdkResCerro

# Nubia sliding switch (packages-overlay/NubiaParts)
$(call inherit-product, packages/apps/NubiaParts/config.mk)
PRODUCT_PACKAGES += \
    NubiaGameSwitch

# Inherit from proprietary targets
$(call inherit-product, vendor/nubia/cerro/cerro-vendor.mk)

# Camera vendor data bootstrap (watermarks + dualcam cali)
PRODUCT_COPY_FILES += \
    $(DEVICE_PATH)/rootdir/bin/init.cerro.camera.sh:$(TARGET_COPY_OUT_VENDOR)/bin/init.cerro.camera.sh \
    $(DEVICE_PATH)/rootdir/etc/init.cerro.camera.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/init.cerro.camera.rc
