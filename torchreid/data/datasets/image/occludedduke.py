from __future__ import division, print_function, absolute_import
import re
import glob
import os.path as osp

from ..dataset import ImageDataset


class OccludedDuke(ImageDataset):
    """OccludedDuke.

    Reference:
        - Miao, Jiaxu, et al. Pose-guided feature alignment for occluded person re-identification. CVPR 2019.
        

    URL: `<https://github.com/layumi/DukeMTMC-reID_evaluation>` - Subset of DukeMTMC-reID dataset
    Splits: `<https://github.com/lightas/ICCV19_Pose_Guided_Occluded_Person_ReID/tree/master/dataset>`
    
    Dataset statistics:
        - identities: 1404 (train + query).
        - images:15618 (train) + 2210 (query) + 17661 (gallery).
        - cameras: 8.
    """
    dataset_dir = 'occluded_duke'
    dataset_url = None

    def __init__(self, root='', **kwargs):
        self.root = osp.abspath(osp.expanduser(root))
        self.dataset_dir = osp.join(self.root, self.dataset_dir)
        self.download_dataset(self.dataset_dir, self.dataset_url)
        self.train_dir = osp.join(
            self.dataset_dir, 'bounding_box_train'
        )
        self.query_dir = osp.join(self.dataset_dir, 'query')
        self.gallery_dir = osp.join(
            self.dataset_dir, 'bounding_box_test'
        )

        required_files = [
            self.dataset_dir, self.train_dir, self.query_dir, self.gallery_dir
        ]
        self.check_before_run(required_files)

        train = self.process_dir(self.train_dir, relabel=True)
        query = self.process_dir(self.query_dir, relabel=False)
        gallery = self.process_dir(self.gallery_dir, relabel=False)

        super(OccludedDuke, self).__init__(train, query, gallery, **kwargs)

    def process_dir(self, dir_path, relabel=False):
        img_paths = glob.glob(osp.join(dir_path, '*.jpg'))
        pattern = re.compile(r'([-\d]+)_c(\d)')

        pid_container = set()
        for img_path in img_paths:
            pid, _ = map(int, pattern.search(img_path).groups())
            pid_container.add(pid)
        pid2label = {pid: label for label, pid in enumerate(pid_container)}

        data = []
        for img_path in img_paths:
            pid, camid = map(int, pattern.search(img_path).groups())
            assert 1 <= camid <= 8
            camid -= 1 # index starts from 0
            if relabel:
                pid = pid2label[pid]
            data.append((img_path, pid, camid))

        return data
