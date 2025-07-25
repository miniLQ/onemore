from loguru import logger
from app.common.utils import generate_uuid
from plugins.TZ_LOG_PARSER.TzErrorCodeDecodeInterface import TzErrorCodeDecodeInterface as tz
from plugins.TZ_LOG_PARSER.TzErrorCodeDecodeInterface import TzErrorCodeDecodeCardsInfo

UNIQUE_NAME = "Test TZ log parser"


def get_route_key():
    """
    Generate a unique route key for the plugin.
    """
    return f"{UNIQUE_NAME} {generate_uuid()}"


def register(main_window):
    plugin_state = {}

    def on_open():

        routekey = get_route_key()
        interface = tz(mainWindow=main_window)
        interface.addTab(routeKey=routekey, text=routekey, icon='app/resource/images/Chicken.png')

        plugin_state["interface"] = interface
        plugin_state["routeKey"] = routekey

    def on_tab_changed(route_key: str):
        route_key_plugin = plugin_state.get("routeKey")
        interface = plugin_state.get("interface")

        if interface is not None and route_key_plugin in route_key:
            logger.info(f"Tab 切换到 {route_key_plugin}")
            widget = main_window.showInterface.findChild(TzErrorCodeDecodeCardsInfo, route_key_plugin)
            main_window.showInterface.setCurrentWidget(widget)
        else:
            logger.warning(f"无法处理 Tab 切换，未找到状态 route_key={route_key}")

    appcard = main_window.generalInterface.addCard(f"app/resource/images/Chicken.png", "Test TZ log parser", '@designed by iliuqi.', "Test TZ log parser")

    main_window.registerPluginOpener(UNIQUE_NAME, on_open)
    main_window.registerTabChangedHandler(UNIQUE_NAME, on_tab_changed)
