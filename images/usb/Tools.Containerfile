ARG BASE
FROM ${BASE}
RUN pacman -Syu --disable-sandbox-filesystem --noconfirm --needed bc dtc openssl dosfstools mtools gptfdisk e2fsprogs qemu-system-aarch64 && pacman -Q > /usr/share/mainframeos-build/packages.txt
