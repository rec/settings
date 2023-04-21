import dataclasses as dc
from settings import Settings
from typing import List

def field(factory):
    return dc.field(default_factory=factory)


@dc.dataclass
class Audio(Settings):
    levels: List[float] = field(list)


@dc.dataclass
class DMX(Settings):
    channel: int = 0


@dc.dataclass
class Midi(Settings):
    channel: int = 0
    name: str = ''


@dc.dataclass
class Everything(Settings):
    audio: Audio = field(Audio)
    dmx: DMX = field(DMX)
    midi: Midi = field(Midi)


def test_simple():
    e = Everything()
    assert e.modified() == {}

    e.dmx.channel = 3
    assert e.modified() == {'dmx': {'channel': 3}}


def test_lists():
    e = Everything()
    assert e.modified() == {}

    e.audio.levels[:] = [1.0, 2.0]
    assert e.modified() == {}
    # Can't detect this

    e.audio.levels = [1.0, 2.0]
    assert e.modified() == {'audio': {'levels': [1.0, 2.0]}}


def test_diff():
    e = Everything()
    e.audio.levels[:] = [1.0, 2.0]

    assert Everything().diff(e) == {'audio': {'levels': [1.0, 2.0]}}
    assert e.diff(Everything()) == {'audio': {'levels': []}}



if __name__ == '__main__':
    d = dc.asdict(Everything())
