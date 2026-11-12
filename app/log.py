import logging

LOGGER = logging.getLogger("devops")
LOGGER.setLevel(logging.INFO)

handler = logging.StreamHandler()
file_handler = logging.FileHandler("app.log", encoding="utf-8")

formatter = logging.Formatter("%(name)s - %(asctime)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

LOGGER.addHandler(handler)
LOGGER.addHandler(file_handler)

LOGGER.info("Logging is set up.")
LOGGER.debug("This is a debug message.")
LOGGER.warning("This is a warning message.")