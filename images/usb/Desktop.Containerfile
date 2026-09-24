ARG BASE
FROM ${BASE}
RUN printf 'Server = https://fl.us.mirror.archlinuxarm.org/$arch/$repo\n' > /etc/pacman.d/mirrorlist && \
    pacman-key --init && pacman-key --populate archlinuxarm && \
    pacman -Syu --disable-sandbox-filesystem --noconfirm --needed plasma-desktop fastfetch m4 wireless-regdb rtkit sddm konsole dolphin kate firefox flatpak discover networkmanager plasma-nm plasma-pa kscreen bluedevil bluez bluez-utils pipewire pipewire-pulse pipewire-alsa wireplumber alsa-utils mesa vulkan-freedreno linux-firmware linux-firmware-qcom sudo grub dosfstools e2fsprogs parted rsync python && \
    usermod -l mainframe -d /home/mainframe -m alarm && passwd -l mainframe && passwd -l root && \
    usermod -aG wheel mainframe && \
    systemctl disable sshd systemd-networkd systemd-resolved && \
    systemctl enable NetworkManager bluetooth sddm && \
    mkdir -p /etc/sddm.conf.d /etc/sudoers.d /usr/share/mainframeos && \
    printf '[Autologin]\nUser=mainframe\nSession=plasma\n' > /etc/sddm.conf.d/live.conf && \
    printf 'mainframe ALL=(ALL:ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/mainframeos-live && chmod 0440 /etc/sudoers.d/mainframeos-live && \
    printf 'en_US.UTF-8 UTF-8\n' > /etc/locale.gen && locale-gen && \
    printf 'LANG=en_US.UTF-8\n' > /etc/locale.conf && \
    printf 'mainframeos-live\n' > /etc/hostname && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    rm -f /etc/resolv.conf && ln -s /run/NetworkManager/resolv.conf /etc/resolv.conf && \
    pacman -Q > /usr/share/mainframeos/packages.txt && \
    rm -f /var/cache/pacman/pkg/* && \
    truncate -s 0 /etc/machine-id && rm -f /var/lib/dbus/machine-id /etc/ssh/ssh_host_* && \
    rm -f /etc/systemd/system/multi-user.target.wants/sshd.service
