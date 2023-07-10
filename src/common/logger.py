import logging


def log_message(log_fn, msg="", newline_prefix: bool = False, newline_suffix: bool = False) -> None:
    prefix = "\n" if newline_prefix else ""
    suffix = "\n" if newline_suffix else ""
    formatted_msg = f"{prefix}{msg}{suffix}"
    log_fn(formatted_msg)


class Logger:
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    @staticmethod
    def info(msg="", newline_prefix: bool = False, newline_suffix: bool = False):
        log_message(logging.info, msg, newline_prefix, newline_suffix)

    @staticmethod
    def error(msg="", newline_prefix: bool = False, newline_suffix: bool = False):
        log_message(logging.error, msg, newline_prefix, newline_suffix)
