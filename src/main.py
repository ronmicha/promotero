import traceback

from common.logger import Logger
from handlers.args_handler import get_args
from promotero import Promotero

if __name__ == "__main__":
    try:
        input_args = get_args()

        promotero = Promotero(input_args)
        promotero.run()

        Logger.info("*" * 10 + " DONE! " + "*" * 10, True)
    except Exception:
        Logger.error("ERROR!", True)
        Logger.error(traceback.format_exc())
