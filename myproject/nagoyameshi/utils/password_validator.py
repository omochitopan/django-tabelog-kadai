import re
from django.core.exceptions import ValidationError

class PasswordValidator:
    msg = '英小文字/大文字、数字、または特殊文字が含まれていません'
    
    def validate(self, password, user=None):
        REX = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[~!@#$%^&*_\-+=`|(){}\[\]:;\"\'<>,.?/]).{8,64}"
        result = re.fullmatch(REX, password)
        if not result:
            raise ValidationError(self.msg)
    
    def get_help_text(self):
        return self.msg
