import os
import re
import datetime as dt

load_date = lambda date: dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

clean_text = lambda text: re.sub(
    '\n+|\\s+|\\t+|\\r+|\\r\\n+|\\r\\n',
    ' ',
    ''.join(text)
).strip()

format_date = lambda date, formate: dt.datetime.strptime(
    date,
    formate,
).strftime("%Y-%m-%d %H:%M:%S")


def path(file_path: str, secondary_path: str = None) -> str:
    """ converts a relative path to an absolute path """
    seperator = '\\' if 'nt' in os.name.lower() else '/'
    file = os.path.join(
        seperator.join(
            os.path.realpath(
                os.path.join(
                    os.getcwd(),
                    os.path.dirname(__file__)
                )
            ).split(seperator)[:-1]),  # remove the current folder from path
        file_path
    )
    return file if secondary_path is None else os.path.join(file, secondary_path)
