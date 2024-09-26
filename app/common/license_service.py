# coding: utf-8


class LicenseService:
    """ License service """

    def validate(self, license: str, email: str):
        """ Verify if the activation code is legal """
        # TODO: ADD YOUR VALIDATE LOGIC HERE

        if license == "123456" and email == "test@longcheer.com":
            return True
        else:
            return False

