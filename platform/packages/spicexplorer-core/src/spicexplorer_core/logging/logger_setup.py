import logging
import os
import sys
from datetime import datetime
from pathlib import Path


def setup_loggers(
    out_logname: str = "SpiceXplorer",
    parent_folder: Path = Path("."),
    console_level: int = logging.INFO,
) -> logging.Logger:
    """Configure the ``spicexplorer`` logger hierarchy.

    Args:
        out_logname:    Base name for the timestamped log file.
        parent_folder:  Directory that will contain the ``logs/`` sub-folder.
        console_level:  Minimum level printed to the console
                        (``logging.DEBUG``, ``logging.INFO``, ``logging.WARNING``,
                        ``logging.ERROR``, or ``logging.CRITICAL``).
                        The log *file* always captures everything at DEBUG level.
    """
    # --- Create timestamped log filename ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = Path(f"{parent_folder}/logs/{out_logname}_{timestamp}.log")
    os.makedirs(log_path.parent, exist_ok=True)

    # --- The wrapper logger ---
    logger = logging.getLogger("spicexplorer")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s: [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # Always clear old handlers to avoid duplicates on re-init
    logger.handlers.clear()

    # --- Console Handler (user-configurable level) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- File Handler (always DEBUG so nothing is lost) ---
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("🚀 Logger initialized and ready!")
    logger.info(f"📄 Log file: {os.path.abspath(log_path)}")
    logger.info(f"🖥️  Console level: {logging.getLevelName(console_level)}")

    # --- Configure logging for spicelib (file only, suppress console noise) ---
    spicelib_logger = logging.getLogger("spicelib")
    spicelib_logger.setLevel(logging.CRITICAL)
    logger.info(f"🔧 spicelib logger set to {spicelib_logger.getEffectiveLevel()}")

    return logger

def setup_spicelib_logging(file_handler: logging.FileHandler) -> logging.Logger:
    # Get the top-level spicelib logger
    logger = logging.getLogger("spicelib")
    logger.setLevel(logging.INFO)  # Master level must be low enough to let handlers filter

    # --- Console handler (only CRITICAL)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.CRITICAL)
    console_formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    # Clear old handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Attach handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Ensure all children inherit this setup
    for name, temp_logger in logging.Logger.manager.loggerDict.items():
        if name.startswith("spicelib"):
            logging.getLogger(name).setLevel(logging.INFO)
            if isinstance(temp_logger, logging.Logger):
                temp_logger.addHandler(console_handler)
                temp_logger.addHandler(file_handler)

    return logger


class JupyterLogFilter:
    """
    Wraps Jupyter's stdout to filter noise.
    - Suppresses noise keywords.
    - INTELLIGENTLY suppresses the trailing newline from print() calls associated with noise.
    """
    def __init__(self, original_stream, file_logger):
        self._original_stream = original_stream
        self._file_logger = file_logger
        self._suppress_next_newline = False # State flag

    def __getattr__(self, name):
        return getattr(self._original_stream, name)

    def write(self, buf):
        # 1. Check for specific noise keywords
        is_noise = any(keyword in buf for keyword in [
            "RunTask",
            "Simulation Successful",
            "Simulation Callback",
            "spicexplorer.optimization",
            "Sun Feb", "Mon Feb", "Tue Feb" # Date headers
        ])

        # 2. Log EVERYTHING to the file (strip cleanly)
        if buf.strip():
            self._file_logger.info(buf.rstrip())

        # --- 3. The "Empty Line" Fix ---
        if is_noise:
            # If this chunk is noise, suppress it AND mark to suppress the next \n
            self._suppress_next_newline = True
            return

        # If it's just a newline and we are in 'suppress' mode, kill it
        if buf == '\n' and self._suppress_next_newline:
            self._suppress_next_newline = False # Reset flag
            return

        # If we got here, it's valid content (or a newline for valid content)
        self._suppress_next_newline = False # Reset flag just in case
        self._original_stream.write(buf)

    def flush(self):
        self._original_stream.flush()

# --- 2. Setup Function ---
def setup_loggers_with_spicelib_suppression(out_logname="SpiceXplorer", parent_folder:Path=Path(".")) -> logging.Logger:

    # Reset logging if we are re-running the cell to avoid nesting wrappers
    if hasattr(sys.stdout, '_original_stream'):
        sys.stdout = sys.stdout._original_stream

    original_stdout = sys.stdout

    # --- File Setup ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = Path(f"{parent_folder}/logs/{out_logname}_{timestamp}.log")
    os.makedirs(log_path.parent, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(name)s: [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    # --- Handlers ---
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Use original_stdout for console logging to avoid recursive loops
    console_handler = logging.StreamHandler(stream=original_stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # --- Loggers ---

    # 1. Main Logger (Visible everywhere)
    logger = logging.getLogger("spicexplorer")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 2. Redirect Logger (Hidden container for the proxy)
    redirect_logger = logging.getLogger("std_redirect")
    redirect_logger.setLevel(logging.INFO)
    redirect_logger.propagate = False
    redirect_logger.handlers.clear()
    redirect_logger.addHandler(file_handler)

    # 3. Spicelib Logger (File only)
    spicelib_logger = logging.getLogger("spicelib")
    spicelib_logger.setLevel(logging.INFO)
    spicelib_logger.propagate = False
    spicelib_logger.handlers.clear()
    spicelib_logger.addHandler(file_handler)

    # --- Apply Proxy ---
    # Wrap stdout in our class that mimics Jupyter's stream
    sys.stdout = JupyterLogFilter(original_stdout, redirect_logger)

    # Log initial status
    logger.info("🚀 Logger initialized!")
    logger.info(f"📄 Log file: {os.path.abspath(log_path)}")
    logger.info("👀 TQDM and Errors will still show in console (stderr).")
    logger.info("🔇 Standard outputs and SPICE logs are redirected to file (stdout).")

    return logger
