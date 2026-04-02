import binascii
import configparser
import os

config = configparser.ConfigParser()
config.read("settings.ini")

debug = config["settings"]["debug"].lower() == "true"

# dirs
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
tmp_dir = os.path.join(base_dir, "tmp/")
script_dir = os.path.join(base_dir, "tmp/scripts")

# databases
database_uri = config["settings"]["database_uri"]
host_name = config["settings"]["host_name"]
# sentry
# sentry_dsn = config["settings"]["sentry_dsn"]

# yandex cloud logging
yandex_logger_config = config["yandex_logger"]
yandex_logger_token = yandex_logger_config["token"]
yandex_log_group_id = yandex_logger_config.get("log_group_id", None)
yandex_folder_id = yandex_logger_config.get("folder_id", None)
yandex_resource_type = yandex_logger_config.get("resource_type", None)
yandex_resource_id = yandex_logger_config.get("resource_id", None)
yandex_log_batch_size = int(yandex_logger_config.get("log_batch_size", "5"))
yandex_log_commit_period = int(yandex_logger_config.get("log_commit_period", "5"))

# admin
admin_password = config["settings"]["admin_password"]
auth_secret_key = config["settings"]["secret_key"]

# integrations
# smsaero
smsaero_base_url = config["smsaero"]["base_url"]
# smsru
smsru_base_url = config["smsru"]["base_url"]

# pushes
realms_map = {
}

google_fcm_base_url = "https://fcm.googleapis.com"

scopes = ["https://www.googleapis.com/auth/firebase.messaging"]

# npd
npd_url = config["settings"]["npd_url"]
npd_token = config["settings"]["npd_token"]

# kafka
max_concurrency = config["kafka"]["max_concurrency"]
kafka_uri = config["kafka"]["kafka_uri"]

# encryptor
nonce = b"\xdd\x05\xb3,/!\x85e\xd3G$\x97"
mac_len = 16
public_link_secret_key = binascii.unhexlify(
    config.get("settings", "PUBLIC_LINK_SECRET_KEY")
)

messagio_otp_url = "https://otp.messaggio.com/api/v1/code"
messagio_msg_url = "https://msg.messaggio.com/api/v1/send"
messagio_otp_check_status_url = "https://otp.messaggio.com/api/v1/code/dlrs"

telegram_gateway_url = "https://gatewayapi.telegram.org/"
telegram_gateway_token = ""
