from mitmproxy import ctx
from mitmproxy import io
from mitmproxy import exceptions
import sys


class ReadStdin:
    """
        An addon that reads from stdin if we're not attached to (someting like)
        a tty.
    """
    def __init__(self):
        self.keepserving = False

    def configure(self, options, updated):
        if "keepserving" in updated:
            self.keepserving = options.keepserving

    def running(self, stdin = sys.stdin):
        if not stdin.isatty():
            ctx.log.info("Reading from stdin")
            try:
                stdin.buffer.read(0)
            except Exception as e:
                ctx.log.warn("Cannot read from stdin: {}".format(e))
                return
            freader = io.FlowReader(stdin.buffer)
            try:
                for i in freader.stream():
                    ctx.master.load_flow(i)
            except exceptions.FlowReadException as e:
                ctx.log.error("Error reading from stdin: %s" % e)
            if not self.keepserving:
                ctx.master.shutdown()
