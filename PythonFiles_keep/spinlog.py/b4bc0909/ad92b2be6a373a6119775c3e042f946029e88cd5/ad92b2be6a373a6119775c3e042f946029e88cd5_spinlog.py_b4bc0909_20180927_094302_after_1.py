from spinlog import Spinner
from time import sleep

with Spinner.get("yolololo") as s:
    sleep(2)
    s.warn("ah bon?")
    sleep(2)
    s.error("BIM\nBIM")
    sleep(2)
    s.info("HAHA\nHAHA")
    s.log("HAHA")
    s.log("HAHA", symbol="😆".encode("utf-8"))
    sleep(2)
    s.debug("HAHA oui c'est drole")
    sleep(2)

