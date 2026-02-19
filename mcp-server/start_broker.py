import logging
from broker import run_broker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        run_broker()
    except Exception as e:
        logger.error(f"Failed to start broker: {e}")
