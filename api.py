from dataclasses import dataclass
import requests
from logger import Logging
from graph import graphProcess
import os

@dataclass
class basicApiCall:
    hoster_token: str
    logger: Logging
    basic_url: str = "https://userapi.vdsina.ru"
    balance_ep: str = "v1/account.balance"
    account_ep: str = "v1/account"
    servers_ep: str = "v1/server"
    servers_mon_ep: str = "v1/server.stat"
    images_dir: str = "images"

    def send_api_requests(self, **kwargs):
        headers = {
            'Authorization': f'{self.hoster_token}',
            'Content-Type': 'application/json'
        }
        if kwargs.get("method") == "GET":
            try:
                response = requests.get(url=kwargs.get("url"), headers=headers)
                if response.status_code == 200:
                    return response.json()
            except requests.exceptions.RequestException as err:
                self.logger.warning("Ошибка при отправке запроса на %s. Код ответа %s", kwargs.get("url"), response.status_code)
        return None

    def get_servers_name(self):
        servers_list = []
        response = self.send_api_requests(method="GET", url=f"{self.basic_url}/{self.servers_ep}")
        try:
            for _, value in enumerate(response["data"]):
                servers_list.append(value["name"])
        except (KeyError, IndexError, TypeError) as err:
            self.logger.error("Методо get_server_name() вернул ошибку: %s", err)
            servers_list = None
        return servers_list

    def make_servers_mapping(self):
        servers_dict = {}
        response = self.send_api_requests(method="GET", url=f"{self.basic_url}/{self.servers_ep}")
        try:
            for _, value in enumerate(response["data"]):
                servers_dict[value["name"]] = value["id"]
        except (KeyError, IndexError, TypeError) as err:
            self.logger.error("Методо make_servers_mapping() вернул ошибку: %s", err)
            servers_dict = None
        return servers_dict
@dataclass
class servers(basicApiCall):

    def get_server_params(self, server_name):
        servers_mapping = self.make_servers_mapping()
        response = self.send_api_requests(method="GET", url=f"{self.basic_url}/{self.servers_ep}/{servers_mapping[server_name]}")
        try:
            server_status = response["status"]
            server_ip_addr = response["data"]["ip"][0]["ip"]
            cpu_count = response["data"]["data"]["cpu"]["value"]
            ram_count = response["data"]["server-plan"]["name"]
            disk_volume = response["data"]["data"]["disk"]["value"]
            disk_calculation = response["data"]["data"]["disk"]["for"]
            traff_volume = response["data"]["data"]["traff"]["value"]
            traff_calculation = response["data"]["data"]["traff"]["for"]
            os_release = response["data"]["template"]["name"]
            location = response["data"]["datacenter"]["name"]
            message = (
                f"Имя сервера: {server_name}\n"
                f"Статус: {server_status}\n"
                f"ОС: {os_release}\n"
                f"IP адрес: {server_ip_addr}\n"
                f"Кол-во ЦПУ: {cpu_count}\n"
                f"RAM: {ram_count}\n"
                f"Объем диска: {disk_volume}{disk_calculation}\n"
                f"Объем трафика: {traff_volume}{traff_calculation}\n"
                f"Датацентр: {location}"
            )
        except (KeyError, IndexError, TypeError) as err:
            self.logger.error("Метод get_server_params() вернул ошибку: %s", err)
            message = f"Ошибка при получении параметров сервера: {err}"
        return message

    def get_server_monitoring(self, server_name):
        servers_mapping = self.make_servers_mapping()
        response = self.send_api_requests(method="GET", url=f"{self.basic_url}/{self.servers_mon_ep}/{servers_mapping[server_name]}")
        try:
            response = response["data"][-3:]
            graphProcess(response).make_graph_images()
            image_files = os.listdir(self.images_dir)
            image_files = [filename for filename in image_files if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            image_files_with_path = [f"images/{filename}" for filename in image_files]
        except Exception as err:
            self.logger.error("Метод get_server_monitoring() вернул ошибку: %s", err)
            image_files_with_path = None
        return image_files_with_path

        
@dataclass
class account(basicApiCall):

    def get_balance(self):
        response = self.send_api_requests(method="GET", url=f"{self.basic_url}/{self.balance_ep}")
        try:
            status = response["status"]
            balance_real = response["data"]["real"]
            balance_bonus = response["data"]["bonus"]
            balance_partner = response["data"]["partner"]
            message = (
                f"Статус: {status}\n"
                f"Баланс: {balance_real} руб\n"
                f"Бонусы: {balance_bonus} руб\n"
                f"Партеры: {balance_partner} руб"
            )
        except (KeyError, IndexError, TypeError) as err:
            self.logger.error("Метод get_balance() вернул ошибку: %s", err)
            message = f"Ошибка при получении баланса: {err}"
        return message

    def get_forecast(self):
        response = self.send_api_requests(method="GET", url=f"{self.basic_url}/{self.account_ep}")
        try:
            forecast = response["data"]["forecast"]
            message = (
                "Формат даты: гг-мм-дд\n"
                f"Будет отключено: {forecast}"
            )
        except (KeyError, IndexError, TypeError) as err:
            self.logger.error("Метод get_forecast() вернул ошибку: %s", err)
            message = f"Ошибка при получении прогноза отключения: {err}"
        return message
