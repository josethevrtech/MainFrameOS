ARG BASE
FROM ${BASE}
COPY kernel/ /opt/mainframeos-kernel/
COPY firmware/ /usr/lib/firmware/qcom/x1p42100/hp/omnibook-5/
COPY overlay/ /
COPY mkinitcpio.conf /etc/mkinitcpio-mainframeos.conf
COPY support.pkg.tar.xz /tmp/support.pkg.tar.xz
RUN printf 'mainframe:mainframe\n' | chpasswd && \
    pacman -U --noconfirm /tmp/support.pkg.tar.xz && rm /tmp/support.pkg.tar.xz && \
    pacman -R --noconfirm linux-aarch64 && \
    cp -a /opt/mainframeos-kernel/lib/modules/* /usr/lib/modules/ && \
    cp /opt/mainframeos-kernel/Image /boot/Image-mainframeos && \
    cp /opt/mainframeos-kernel/device.dtb /boot/mainframeos.dtb && \
    cp /opt/mainframeos-kernel/kernel.config /boot/config-mainframeos && \
    depmod "$(cat /opt/mainframeos-kernel/kernelrelease)" && \
    mkinitcpio -k "$(cat /opt/mainframeos-kernel/kernelrelease)" -c /etc/mkinitcpio-mainframeos.conf -g /boot/initramfs-mainframeos.img && \
    systemctl enable mainframeos-smoke.service && \
    systemctl set-default graphical.target && \
    pacman -Q > /usr/share/mainframeos/packages.txt && \
    rm -rf /opt/mainframeos-kernel
