import re

class CRC16:

    @staticmethod
    def calculate(payload: str) -> str:
        crc = 65535
        polynomial = 4129
        payload += '6304'
        for byte in payload.encode('utf-8'):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 32768:
                    crc = crc << 1 ^ polynomial
                else:
                    crc <<= 1
            crc &= 65535
        return f'{crc:04X}'

class PixPayload:

    def __init__(self, key: str, name: str, city: str, amount: str=None, txid: str='***'):
        self.key = key
        self.name = self._normalize_str(name, 25)
        self.city = self._normalize_str(city, 15)
        self.amount = amount
        self.txid = txid if txid else '***'

    def _normalize_str(self, text: str, max_len: int) -> str:
        return text[:max_len]

    def _format_field(self, field_id: str, value: str) -> str:
        if not value:
            return ''
        length = len(value)
        return f'{field_id}{length:02d}{value}'

    def generate(self) -> str:
        payload = [self._format_field('00', '01'), self._format_field('26', self._build_merchant_account_info()), self._format_field('52', '0000'), self._format_field('53', '986')]
        if self.amount:
            try:
                amt = f'{float(self.amount):.2f}'
                payload.append(self._format_field('54', amt))
            except ValueError:
                pass
        payload.extend([self._format_field('58', 'BR'), self._format_field('59', self.name), self._format_field('60', self.city), self._format_field('62', self._build_additional_data_field())])
        raw_payload = ''.join(payload)
        crc = CRC16.calculate(raw_payload)
        return f'{raw_payload}6304{crc}'

    def to_string(self) -> str:
        return self.generate()

    def _build_merchant_account_info(self) -> str:
        gui = self._format_field('00', 'br.gov.bcb.pix')
        key = self._format_field('01', self.key)
        return f'{gui}{key}'

    def _build_additional_data_field(self) -> str:
        return self._format_field('05', self.txid)

class WifiPayload:

    def __init__(self, ssid: str, password: str, encryption: str='WPA', hidden: bool=False):
        self.ssid = ssid
        self.password = password
        self.encryption = encryption
        self.hidden = hidden

    def generate(self) -> str:
        safe_ssid = self._escape(self.ssid)
        safe_pass = self._escape(self.password)
        payload = f'WIFI:T:{self.encryption};S:{safe_ssid};'
        if self.encryption != 'nopass':
            payload += f'P:{safe_pass};'
        if self.hidden:
            payload += 'H:true;'
        payload += ';'
        return payload

    def to_string(self) -> str:
        return self.generate()

    def _escape(self, text: str) -> str:
        return text.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace(':', '\\:')

class SocialPayload:

    @staticmethod
    def _clean_user(value):
        return value.strip().lstrip('@')

    @staticmethod
    def _clean_phone(value):
        return re.sub('\\D', '', value)

    @staticmethod
    def whatsapp(number):
        clean = SocialPayload._clean_phone(number)
        return f'https://wa.me/{clean}'

    @staticmethod
    def instagram(username):
        return f'https://instagram.com/{SocialPayload._clean_user(username)}'

    @staticmethod
    def twitter(username):
        return f'https://twitter.com/{SocialPayload._clean_user(username)}'

    @staticmethod
    def facebook(username):
        return f'https://facebook.com/{SocialPayload._clean_user(username)}'

    @staticmethod
    def linkedin(username):
        return f'https://linkedin.com/in/{SocialPayload._clean_user(username)}'

    @staticmethod
    def github(username):
        return f'https://github.com/{SocialPayload._clean_user(username)}'

    @staticmethod
    def youtube(channel):
        val = SocialPayload._clean_user(channel)
        return f'https://youtube.com/@{val}'

    @staticmethod
    def discord(invite_code):
        code = invite_code.replace('https://discord.gg/', '').strip()
        return f'https://discord.gg/{code}'

    @staticmethod
    def telegram(username):
        return f'https://t.me/{SocialPayload._clean_user(username)}'

    @staticmethod
    def email(address):
        clean = address.strip().replace('mailto:', '')
        return f'MATMSG:TO:{clean};;'

    @staticmethod
    def steam(id_or_url):
        val = SocialPayload._clean_user(id_or_url)
        return f'https://steamcommunity.com/id/{val}'

    @staticmethod
    def pinterest(username):
        return f'https://pinterest.com/{SocialPayload._clean_user(username)}'