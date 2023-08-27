import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from dataclasses import dataclass
import os

@dataclass
class graphProcess:
    data: dict
    images_dir: str = "images"

    def make_graph_images(self):
        ## Включаем не интерактивный режим
        matplotlib.use('Agg')
        timestamps = []
        cpu_values = []
        disk_writes = []
        disk_reads = []
        vnet_tx = []
        vnet_rx = []
        time_interval_seconds = 3600

        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        for entry in self.data:
            dt = datetime.strptime(entry["dt"], "%Y-%m-%d %H:%M:%S")
            timestamps.append(dt)
            cpu_values.append(entry["stat"]["cpu"])
            disk_writes.append(entry["stat"]["disk_writes"] / time_interval_seconds)
            disk_reads.append(entry["stat"]["disk_reads"] / time_interval_seconds)
            vnet_tx_kbps = (entry["stat"]["vnet_tx"] * 8) / 1024
            vnet_tx_kbps = vnet_tx_kbps / time_interval_seconds
            vnet_rx_kbps = (entry["stat"]["vnet_rx"] * 8) / 1024
            vnet_rx_kbps = vnet_rx_kbps / time_interval_seconds
            vnet_tx.append(vnet_tx_kbps)
            vnet_rx.append(vnet_rx_kbps)
        ## Создаем график для CPU
        fig1, ax1 = plt.subplots()
        ax1.plot(timestamps, cpu_values, color='tab:blue')
        ax1.set_xlabel('Timestamp')
        ax1.set_ylabel('CPU (%)')
        ax1.set_title('CPU Usage')
        ## Создаем график для IOPS
        fig2, ax2 = plt.subplots()
        ax2.plot(timestamps, disk_reads, color='tab:purple', label='Disk Reads')
        ax2.plot(timestamps, disk_writes, color='tab:green', label='Disk Writes')
        ax2.set_xlabel('Timestamp')
        ax2.set_ylabel('Disk Operations (IOPS)')
        ax2.set_title('Disk Operations')
        ax2.legend()
        ## Создаем график для VNET
        fig3, ax3 = plt.subplots()
        ax3.plot(timestamps, vnet_rx, color='tab:blue', label='VNET RX')
        ax3.plot(timestamps, vnet_tx, color='tab:orange', label='VNET TX')
        ax3.set_xlabel('Timestamp')
        ax3.set_ylabel('VNET Operations (Kbps)')
        ax3.set_title('VNET Operations')
        ax3.legend()
        ## Сохраняем график в изображение
        fig1.savefig(f"{self.images_dir}/cpu_usage.png")
        fig2.savefig(f"{self.images_dir}/disk.png")
        fig3.savefig(f"{self.images_dir}/vnet.png")
        ## Закрываем фигуры
        plt.close(fig1)
        plt.close(fig2)
        plt.close(fig3)
