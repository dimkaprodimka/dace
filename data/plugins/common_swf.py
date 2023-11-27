#-plugin-sig:Tv8p0HW4QHJnO0fgK6+A2wVP2pTrz2XfihcUXCJatwsEKuGzlziVXdc6ghXsGNImRYh/7oIMbHQfnodx0RJbXrP7OxfDfp5XsdSAM/lVi5jp+kJWNdZdCyzZ4v2++Z2SOK5749N4x2Vc9/EmoYka3l5Bp0vxfi6bl6VVwXDcLV6R/BXhqIAw7Fo4REAyQaNXOfrEQkTe0n9HYQiYkU6N4NGKRyWGZf7yg7LU3xT6jG03VPw1gVRTpATBkQx00LWfpEbGLnQAa/1f4xvsOED2XHrjNyF6LdOr3c2h+mjq50S+qLajYTs6/Nm8SUI8A/fj1a623Jew1oGYljjf1O77eA==
from collections import namedtuple
from io import BytesIO

from ACEStream.PluginsContainer.streamlink.utils import swfdecompress
from ACEStream.PluginsContainer.streamlink.packages.flashmedia.types import U16LE, U32LE

__all__ = ["parse_swf"]

Rect = namedtuple("Rect", "data")
Tag = namedtuple("Tag", "type data")
SWF = namedtuple("SWF", "frame_size frame_rate frame_count tags")


def read_rect(fd):
    header = ord(fd.read(1))
    nbits = header >> 3
    nbytes = int(((5 + 4 * nbits) + 7) / 8)
    data = fd.read(nbytes - 1)

    return Rect(data)


def read_tag(fd):
    header = U16LE.read(fd)
    tag_type = header >> 6
    tag_length = header & 0x3f
    if tag_length == 0x3f:
        tag_length = U32LE.read(fd)

    tag_data = fd.read(tag_length)

    return Tag(tag_type, tag_data)


def read_tags(fd):
    while True:
        try:
            yield read_tag(fd)
        except IOError:
            break


def parse_swf(data):
    data = swfdecompress(data)
    fd = BytesIO(data[8:])
    frame_size = read_rect(fd)
    frame_rate = U16LE.read(fd)
    frame_count = U16LE.read(fd)
    tags = list(read_tags(fd))

    return SWF(frame_size, frame_rate, frame_count, tags)
