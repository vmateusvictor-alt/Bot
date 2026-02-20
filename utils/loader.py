from sources.toonbr import ToonBrSource


def get_all_sources():
    return {
        "ToonBr": ToonBrSource(),
    }
