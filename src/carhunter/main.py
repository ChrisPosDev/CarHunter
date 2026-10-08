import asyncio
import logging
import signal
import sys
from pathlib import Path
from dotenv import load_dotenv

from .bootstrap import setup_application

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    load_dotenv()
    project_root = Path(__file__).parent.parent.parent

    monitor_service, http_client, repository = await setup_application(project_root)

    def handle_sigint(sig, frame):
        logger.info("Received SIGINT, shutting down...")
        monitor_service.stop()

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        await monitor_service.start()
    finally:
        logger.info("Cleaning up resources...")
        await http_client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

