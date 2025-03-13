# Kernel Auto Builder 🚀

Latest device released : ![GitHub Releases](https://img.shields.io/github/v/release/oneloutre/kernel_auto_builder)  

[![Github All Releases](https://img.shields.io/github/downloads/Oneloutre/kernel_auto_builder/total.svg)]()



## 🌟 Overview
This repository automates kernel compilation using **GitHub Actions**. The built kernel is published to **GitHub Releases**, and a **Discord notification** is sent upon completion.  
this repo WILL NOT patch the kernel with KernelSU-Next for you

## ✨ Features
- ⚙️ **Automated kernel compilation** via GitHub Actions  
- 📂 **KernelSU-Next handling** - NOT PATCHING !
- 🔥 **Flashable ZIP creation through AnyKernel3**
- 🚀 **GitHub Releases integration** (`latest` + dynamic versioning)  
- 📢 **Discord webhook notifications**  

## ⚙️ Configuration & Usage

### 🔹 **Prerequisites**
- A fork of the kernel source repository  
- **GitHub Secrets Required:**  
  - `WEBHOOK` → Discord webhook for notifications  

### 📱 **Usage**  

Here is the default `.github/workflows/kernel_build.yml`. Modify it to your convenience, then use it. 

<details>
<summary>kernel_build.yml</summary>

```yml
name: Build Android Kernel then ship it in an AnyKernel3 flashable zip

on:
  push:
    branches:
      - YourBranch
  pull_request:
    branches:
      - YourBranch
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: ⚡ Checkout kernel's sourcecode and clone submodules
        uses: actions/checkout@v4

      - name: 🔄 Update KernelSU-Next
        run: |
          rm -rf KernelSU-Next
          git clone https://github.com/KernelSU-Next/KernelSU-Next

      - name: 📥 Clone AnyKernel3
        run: |
          git clone -b b4s4 https://github.com/Oneloutre/AnyKernel3.git anykernel
          rm -rf anykernel/.git

      - name: 📦 Install dépendencies
        run: |
          sudo apt-get update -y -qq
          sudo apt-get install -y --no-install-recommends \
          python3-pip \
          git \
          zip \
          unzip \
          gcc \
          g++ \
          make \
          ninja-build \
          file \
          bc \
          bison \
          flex \
          libfl-dev \
          libssl-dev \
          libelf-dev \
          wget \
          build-essential \
          python3-dev \
          python3-setuptools \
          rsync \
          ccache \
          llvm-dev
          sudo apt install flex libncurses6 libncurses5 binutils-aarch64-linux-gnu device-tree-compiler \
          android-sdk-libsparse-utils
          sudo apt install -y gcc-arm-linux-gnueabi
          echo "CROSS_COMPILE_ARM32=arm-linux-gnueabi-" >> $GITHUB_ENV

      - name: 🔧 Install Clang from a Github action
        uses: KyleMayes/install-llvm-action@v2
        with:
          version: "18.1.8"
          directory: ${{ runner.temp }}/llvm

      - name: 🔧 Add Clang to the PATH
        run: |
          echo "${{ runner.temp }}/llvm/bin" >> $GITHUB_PATH
      
      - name: 🛠 Use repo's mkdtimg
        run: |
          chmod +x tools/mkdtimg
          sudo mv tools/mkdtimg /usr/local/bin/mkdtimg

      - name: 🔍 Device's codename and kernel's version
        run: |
          DEVICE_CODENAME=YourDevice
          KERNEL_VERSION=$(make kernelversion)

          echo "Device Codename: $DEVICE_CODENAME"
          echo "Kernel Version: $KERNEL_VERSION"

          echo "DEVICE_CODENAME=$DEVICE_CODENAME" >> $GITHUB_ENV
          echo "KERNEL_VERSION=$KERNEL_VERSION" >> $GITHUB_ENV

      - name: 🚀 Enable ccache to speed the build up
        uses: hendrikmuhs/ccache-action@v1.2
        with:
          max-size: 7G

      - name: 🛠️ Build the kramel
        run: |
          export ARCH=arm64
          export SUBARCH=arm64
          export KBUILD_COMPILER_STRING=$(clang --version | head -n 1)
          export CCACHE_EXEC=$(which ccache)
          export KBUILD_BUILD_HOST="Github-actions-Onelots"

          make O=out ARCH=arm64 YOUR_DEFCONFIG V=1
          make O=out ARCH=arm64 olddefconfig
          ./scripts/config --file out/.config -e CONFIG_BUILD_ARM64_APPENDED_DTB_IMAGE

          make -j$(nproc --all) O=out \
          ARCH=arm64 \
          CC="ccache clang" \
          LLVM=1 \
          LLVM_IAS=1 \
          CLANG_TRIPLE=aarch64-linux-gnu- \
          CROSS_COMPILE=aarch64-linux-android- \
          CROSS_COMPILE_ARM32=arm-linux-androideabi-

      - name: 🚀 Copy the compiled kernel to AnyKernel3 then create the zip
        run: |
          ZIP_NAME="Kernel-${DEVICE_CODENAME}-${KERNEL_VERSION}-$(date +%d%m%Y).zip"

          cp out/arch/arm64/boot/Image.lz4-dtb anykernel/

          cd anykernel && zip -r9 $ZIP_NAME ./*
          mv $ZIP_NAME ../

          echo "ZIP_NAME=$ZIP_NAME" >> $GITHUB_ENV

      - name: 📤 Publish github release
        uses: softprops/action-gh-release@v2
        with:
          files: ${{ env.ZIP_NAME }}
          tag_name: "latest"
          draft: false
          prerelease: false

      - name: 📤 Publish with tag associated to the kernel
        uses: softprops/action-gh-release@v2
        with:
          files: ${{ env.ZIP_NAME }}
          tag_name: "${{ env.ZIP_NAME }}"
          draft: false
          prerelease: false

      - name: 🚀 Notify people on Discord
        env:
          DEVICE_CODENAME: ${{ env.DEVICE_CODENAME }}
          KERNEL_VERSION: ${{ env.KERNEL_VERSION }}
          WEBHOOK: ${{ secrets.WEBHOOK }}
          NAME: ${{ env.ZIP_NAME }}
        run: |
          python3 .github/webhook.py
```

</details>
