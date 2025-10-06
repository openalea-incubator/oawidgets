from openalea.mtg import MTG
from openalea.oawidgets.mtg import plot
import pathlib

data = pathlib.Path(__file__).parent.resolve() / "data"


def test_mtg():
    g = MTG(data / "boutdenoylum2.mtg")
    plot(g)
