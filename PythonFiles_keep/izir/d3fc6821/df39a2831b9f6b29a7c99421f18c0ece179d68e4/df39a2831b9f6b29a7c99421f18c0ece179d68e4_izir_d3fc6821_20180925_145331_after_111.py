"""A simple streaming movie server example"""
import izi


@izi.get(output=izi.output_format.mp4_video)
def watch():
    """Watch an example movie, streamed directly to you from izi"""
    return 'movie.mp4'
