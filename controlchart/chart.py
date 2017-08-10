import numpy as np

from .parameter import Parameter

from plotting import LeveyJenningsChart
from util import cacheroot


class ControlChart(object):

    def __init__(self, param, points=None):
        self.pointsdata = None if points is None else np.array(points)
        self.points = np.array([]) if points is None else self.pointsdata[:, 2].astype(float)
        self.param = param

    @classmethod
    def from_database(cls, dbifc, ccID):
        param = Parameter.from_database(ccID, dbifc)
        points = dbifc.get_measurements(ccID)
        return cls(param, points)

    @staticmethod
    def load(path=None):
        import pickle
        import gzip
        if path is None:
            path = cacheroot + "cchart.pkl.gz"
        with gzip.open(path, "rb") as handle:
            cc = pickle.load(handle)
        return cc

    def plot(self, show=False):
        if not self.plottable:
            raise RuntimeError("Not plottable!")
        plotter = LeveyJenningsChart(self.param, self.points)
        dumppath = cacheroot + "cc_pic.png"
        plotter.plot(show=show, dumppath=dumppath)
        return dumppath

    def backup(self, path=None):
        import pickle
        import gzip
        if self.param["ccID"] is None:
            print("Not backing up new ControlChart!")
            return
        flnm = f"KD-{self.param['ccID']}.pkl.gz"
        if path is None:
            path = cacheroot
        with gzip.open(path + flnm, "wb") as handle:
            pickle.dump(self, handle)
        return path

    @property
    def plottable(self):
        return len(self.points) > 5
