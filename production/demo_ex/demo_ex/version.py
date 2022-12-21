import pkg_resources as pkr

__pkg__ = 'demo_ex'

try:
    __distribution__= pkr.get_distribution(__pkg__)
    __version__ = 'v' + __distribution__.version
except pkr.DistributionNotFound:
   __distribution__ = pkr.Distribution()
   __version__  = 'v0.0.0'