ERR_MSG = "DT: {datetime} | FUNC: {func} | ERROR: {error}"


class MessageOperators:
    SMSAERO = "smsaero"
    SMSRU = "smsru"
    MESSAGIO = "messagio"
    TELEGRAM = "telegram"

    ALL = [SMSAERO, MESSAGIO, SMSRU, TELEGRAM]


class MessageDeliveryStatus:
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"


class MessageChannels:
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SMS = "sms"

    ALL = [WHATSAPP, TELEGRAM, SMS]


class CallOperators:
    MESSAGIO = "messagio"
