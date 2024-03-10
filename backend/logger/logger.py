
import os
import time

from flask import Request


class Logger:
    logger_file = os.path.join(os.path.dirname(__file__), "server_error_logger.txt")

    @staticmethod
    def error(request: Request, exc: Exception):
        exc_str = f"time: {time.time()}\n" \
                  f"request: {request.method.upper()} {request.url}\n" \
                  f"exception: {exc}\n" \
                  f"exception_type: {type(exc)}\n" \
                  f"{'=' * 60}\n"

        # exception_data: str = json.dumps({
        #     "time": time.time(),
        #     "request": f"{request.method.upper()} {request.url}",
        #     "exception": str(exc),
        #     "exception_type": str(type(exc))
        # }) + "\n"
        # exception_data += "=" * 60

        with open(Logger.logger_file, 'a') as sel:
            sel.write(exc_str)

