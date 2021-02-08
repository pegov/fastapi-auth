class SocialErrorMessages:
    def __init__(self, language: str, base_url: str):
        if language == "RU":
            self._full_messages = {
                "email facebook error": f"""<p>Приложение не отдаёт ваш email. Удостоверьтесь, что <a href=\"https://facebook.com/settings\">в настройках facebook</a>, в контактной информации у вас указан email адрес.</p>
                <p><a href=\"{base_url}/login\">Обратно</p>
                """,
                "email vk error": f"""<p>Приложение не отдаёт ваш email. Удостоверьтесь, что <a href=\"https://vk.com/settings\">в настройках vk</a>, у вас указан email.</p>
                <p><a href=\"{base_url}\"/login">Обратно</p>
                """,
                "email exists": f"""<p>Такой email уже зарегистрирован через другую соц. сеть или напрямую через сайт.</p>
                <p><a href=\"{base_url}/login\">Обратно</p>
                """,
                "ban": f"""<p>Учетная запись деактивирована за нарушение правил сайта.</p>
                <p><a href=\"{base_url}/login\">Обратно</p>""",
            }
            self._server_error = "Неизвестная ошибка"
        else:
            self._full_messages = {
                "email facebook error": f"""<p>We can't get your email. Please, check <a href=\"https://facebook.com/settings\">your facebook settings</a>. Make sure you have email there.</p>
                <p><a href=\"{base_url}/login\">Back</p>
                """,
                "email exists": f"""<p>Email already exists.</p>
                <p><a href=\"{base_url}/login\">Back</p>
                """,
                "ban": f"""<p>User has been banned.</p>
                <p><a href=\"{base_url}/login\">Back</p>""",
            }
            self._server_error = "Unknown error"

    def get_error_message(self, msg: str) -> str:
        full_message = self._full_messages.get(msg) or self._server_error
        return full_message


def get_error_message(msg: str, language: str, base_url: str) -> str:
    error_messages = SocialErrorMessages(language, base_url)
    return error_messages.get_error_message(msg)
