#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/penguin_cerro.mk \
    $(LOCAL_DIR)/lineage_cerro.mk

# PenguinOS: primary lunch target is penguin_cerro-*; lineage_cerro kept as
# reference/debug target.
COMMON_LUNCH_CHOICES += \
    penguin_cerro-cp2a-userdebug \
    penguin_cerro-cp2a-user \
    penguin_cerro-cp2a-eng \
    lineage_cerro-cp2a-userdebug \
    lineage_cerro-cp2a-user \
    lineage_cerro-cp2a-eng
