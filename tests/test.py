import os.path as osp
import sys
import time

from progressbar import ProgressBar

from avi_r import AVIReader

# Videos from the MEVA dataset (http://mevadata.org)
VIDEO_LIST = [
    '2018-03-11.16-30-08.16-35-08.hospital.G436.avi',  # no missing
    '2018-03-07.16-55-06.17-00-06.school.G336.avi',  # have missing
    '2018-03-11.11-25-01.11-30-01.school.G424.avi',
    '2018-03-11.16-25-00.16-30-00.school.G639.avi',  # bidirectional
    '2018-03-11.11-35-00.11-40-00.school.G299.avi',  # frame id misorder
    '2018-03-11.11-35-00.11-40-00.school.G330.avi',
    '2018-03-12.10-05-00.10-10-00.hospital.G436.avi'  # first frame fail
]


def integrity_test(video_dir, video_list=VIDEO_LIST,
                   random_access_point=(5790, 100)):
    print('Fix missing with random access')
    start_frame_id, length = random_access_point
    for video_name in video_list:
        print('\t', video_name, flush=True)
        bar = ProgressBar().start()
        v = AVIReader(video_name, video_dir)
        for i, f in bar(enumerate(v)):
            assert f.frame_id == i
        bar = ProgressBar().start()
        v = AVIReader(video_name, video_dir)
        v.seek(start_frame_id)
        for i, frame in bar(enumerate(v.get_iter(length))):
            assert frame.frame_id == start_frame_id + i
    print('No fix missing')
    for video_name in video_list:
        print('\t', video_name, flush=True)
        bar = ProgressBar().start()
        v = AVIReader(video_name, video_dir, fix_missing=False)
        for i, f in bar(enumerate(v)):
            pass


def speed_test_opencv(video_dir, video_list=VIDEO_LIST):
    import cv2
    for video_name in video_list:
        print('\t', video_name, flush=True)
        bar = ProgressBar().start()
        cap = cv2.VideoCapture(osp.join(video_dir, video_name))
        for _ in bar(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
            r, _ = cap.read()
            if not r:
                break


def speed_test_moviepy(video_dir, video_list=VIDEO_LIST):
    from moviepy.editor import VideoFileClip
    for video_name in video_list:
        print('\t', video_name, flush=True)
        bar = ProgressBar().start()
        clip = VideoFileClip(osp.join(video_dir, video_name))
        for i in bar(range(int(round(clip.duration * clip.fps)))):
            clip.get_frame(i / clip.fps)


def speed_test_avi_r(video_dir, video_list=VIDEO_LIST):
    for video_name in video_list:
        print('\t', video_name, flush=True)
        bar = ProgressBar().start()
        video = AVIReader(video_name, video_dir)
        for _ in bar(range(video.length)):
            video.read()


if __name__ == "__main__":
    video_dir = sys.argv[1]
    integrity_test(video_dir)
