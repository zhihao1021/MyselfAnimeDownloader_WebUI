from anime_module import VideoQueue, ImageCacheQueue
from utils import ConnectionManager

VIDEO_QUEUE = VideoQueue()
IMAGE_CACHE_QUEUE = ImageCacheQueue(5)
BROADCAST_WS = ConnectionManager()