import asyncio
import argparse
from pathlib import Path
import shutil
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log"),
        logging.StreamHandler()
    ]
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Sort files by extension asynchronously.")
    parser.add_argument("source", type=str, help="Path to the source folder.")
    parser.add_argument("destination", type=str, help="Path to the destination folder.")
    return parser.parse_args()


async def read_folder(source_path: Path, destination_path: Path):
    """Рекурсивно читає всі файли у вихідній папці та передає їх для копіювання."""
    tasks = []
    for item in source_path.rglob("*"):
        if item.is_file():
            tasks.append(copy_file(item, destination_path))

    if tasks:
        await asyncio.gather(*tasks)


async def copy_file(file_path: Path, destination_path: Path):
    """Копіює файл до відповідної папки на основі його розширення."""
    try:
        # Визначення розширення файлу
        extension = file_path.suffix.lstrip(".").lower() or "unknown"
        target_folder = destination_path / extension
        target_folder.mkdir(parents=True, exist_ok=True)

        # Копіювання файлу
        target_file = target_folder / file_path.name
        await asyncio.to_thread(shutil.copy2, file_path, target_file)

        logging.info(f"Copied: {file_path} -> {target_file}")
    except Exception as e:
        logging.error(f"Failed to copy {file_path}: {e}")


async def main():
    args = parse_arguments()
    source_path = Path(args.source)
    destination_path = Path(args.destination)

    if not source_path.exists() or not source_path.is_dir():
        logging.error("Source path does not exist or is not a directory.")
        return

    destination_path.mkdir(parents=True, exist_ok=True)
    await read_folder(source_path, destination_path)


if __name__ == "__main__":
    asyncio.run(main())
