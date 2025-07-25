from loguru import logger
from app.common.utils import generate_uuid
from plugins.TZ_LOG_PARSER.TzErrorCodeDecodeInterface import TzErrorCodeDecodeInterface as tz

UNIQUE_NAME = "Test TZ log parser"

def register(main_window):
    def on_open():
        logger.info("test TZ log parser plugin on_open")
        ramdomNum = generate_uuid()
        routekey = "{} {}".format(UNIQUE_NAME, ramdomNum)

        TzErrorCodeDecodeInterface = tz(mainWindow=main_window)
        TzErrorCodeDecodeInterface.addTab(routeKey=routekey, text=routekey,
                                               icon='app/resource/images/Chicken.png')


    appcard = main_window.generalInterface.addCard(f"app/resource/images/Chicken.png", "Test TZ log parser", '@designed by iliuqi.', "Test TZ log parser")

    main_window.registerPluginOpener(UNIQUE_NAME, on_open)

