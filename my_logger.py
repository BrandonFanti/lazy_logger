import logging
import sys
import pprint
from os import makedirs, getcwd
from os.path import isdir, sep

from bcolors import bcolors

class Logger_Base: #No inheritance - functions oft inject unique behavior (maybe better write better wrapper class?)
    default_log_format = "%(asctime)s - %(name)s - %(levelname)s {}- %(message)s"

    def __init__(self, name=None, file_path=None, log_level=None, stderr=False, strictly_console=False):
        self.logger = logging.getLogger(name)

        self.log_level = logging.INFO

        if log_level: self.log_level = log_level
        self.set_level(self.log_level)
        self.logger.addHandler(Logger_Base.get_log_stream())
        if strictly_console: return

        self.logger.info(f"logs:{file_path}")
        sub_structs=[]
        if file_path:
            sub_structs = file_path.split(sep)
        if len(sub_structs)>1:
            logs_path = sep.join(sub_structs[0:-1])
        else:
            logs_path = getcwd()

        if stderr: self.logger.addHandler(Logger_Base.get_log_stream(stream=sys.stderr))
        if not isdir(logs_path): makedirs(logs_path)
        if file_path:
            self.logger.addHandler(Logger_Base.get_file_handler(file_path))
        self.logger.addHandler(Logger_Base.get_file_handler("latest.log"))

    def enable_debug(self):
        self.logger.setLevel(logging.DEBUG)

    def set_level(self, level):
        self.logger.setLevel(level)
    def error(self, *k, **kw):
        self.logger.info(f"{bcolors.FAIL}ERROR: {k[0]} {bcolors.ENDC}", *k[1:-1], **kw)
    def info(self, *k, **kw):
        self.logger.info(f"{bcolors.OKBLUE}{k[0]}{bcolors.ENDC}", *k[1:-1], **kw)
    def warn(self, *k, **kw):
        self.logger.warn(f"{bcolors.WARNING}{k[0]}{bcolors.ENDC}", *k[1:-1], **kw)
    def debug(self, *k, **kw):
        self.logger.debug(f"{bcolors.OKGREEN}{k[0]}{bcolors.ENDC}", *k[1:-1], **kw)
    def exception(self, *k, stack_info=True, exc_info=True, **kw):
        self.logger.exception(f"{bcolors.FAIL}ERROR: {k[0]}", *k[1:-1],
            **kw
        )
        print(bcolors.ENDC, end="")

    def pprint(self, obj, log_func=None):
        if not log_func: log_func = self.logger.debug
        log_func(pprint.pformat(obj))

    @staticmethod
    def get_file_handler(file_path, format_str=None) -> logging.FileHandler:
        if format_str: log_format=format_str.format("")
        else: log_format = __class__.default_log_format.format("")

        h = logging.FileHandler(filename=file_path)
        fmt = logging.Formatter(log_format)
        h.setFormatter(fmt)
        return h

    @staticmethod
    def get_log_stream(stream=sys.stdout, format_str=None) -> logging.StreamHandler:
        if format_str: log_format=format_str.format("")
        else: log_format = __class__.default_log_format.format("")

        if stream == sys.stdout: log_format = log_format.format("")
        if stream == sys.stderr: log_format = log_format.format("STDERR")

        handler = logging.StreamHandler(stream)

        if not format_str:
            formatter   = logging.Formatter(log_format)
        else:
            formatter   = logging.Formatter(log_format)
        
        handler.setFormatter(formatter)

        return handler

    def add_stream_handler(self, handler):
        self.logger.addHandler(handler)

    @staticmethod
    def timedelta_fmt(t):
        fields_o=['days', 'hours','minutes','seconds','microseconds']
        field_higher_order = [7,24,60,60,1000]
        fields = zip(fields_o,field_higher_order)
        s=""
        for index,field in enumerate(fields):
            field, order = field
            if field == 'microseconds':continue
            if field == 'seconds' and hasattr(t, 'seconds') and hasattr(t, 'microseconds'):
                secs = getattr(t, field)
                s+= f"{secs}.{t.microseconds % field_higher_order[index+1]} seconds"
                continue
            fv=0
            if hasattr(t, field): 
                fv = getattr(t, field)
            if hasattr(t, fields_o[index-1]): fv = fv % field_higher_order[index-1]
            if fv == 0: continue
            s+=f"{fv} {field}"
            if field != fields[-1]: s+= ", "
        return s

    def time_to_process(self, td, ts1=None, ts2=None, task_name="Unnamed_Task"):
        if ts1 and ts2:
            tdstr = self.__class__.timedelta_fmt(ts1-ts2)
        if td: tdstr = self.__class__.timedelta_fmt(td)
        if tdstr:
            self.logger.debug(f"{task_name}: {tdstr}")