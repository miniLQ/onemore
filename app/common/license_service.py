# coding: utf-8
import bcrypt


class LicenseService:
    """ License service """
    def __init__(self):
        self.hashed_license = b'$2b$12$oJ/u1geyl3ldSlI6IputYei9Jy8ZP9WivEusdqX3UhxRtOcPW92wG'
        self.hashed_email = b'$2b$12$8LGdhY3LQFCUaT3krQo.2O3JE83YnqnxkxvBuxqsAJt/TZLYam7eO'

    def validate(self, license: str, email: str):
        """ Verify if the activation code is legal """
        # TODO: ADD YOUR VALIDATE LOGIC HERE

        return bcrypt.checkpw(email.encode(), self.hashed_email) and bcrypt.checkpw(license.encode(), self.hashed_license)

