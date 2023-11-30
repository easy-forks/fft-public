from enum import Enum
import maple.profession as Profession

profession = Profession.Profession

class Job(Enum):
    """
    직업 계열Job은 전사, 마법사, 궁수, 도적, 해적으로 구분됩니다
    모든 캐릭터는 위의 다섯 계열 중 하나에 속합니다
    """
    WARRIOR = ("warrior", "STR", "DEX")
    MAGE = ("mage", "INT", "LUK")
    ARCHER = ("archer", "DEX", "STR")
    THIEF = ("thief", "LUK", "DEX")
    PIRATE = ("pirate", "STR", "DEX")
    SHADOWER = (profession.SHADOWER, "LUK", ["DEX", "STR"])
    DUAL_BLADE = (profession.DUAL_BLADE, "LUK", ["DEX", "STR"])
    CADENA = (profession.CADENA, "LUK", ["DEX", "STR"])
    CAPTAIN = (profession.CAPTAIN, "DEX", "STR")
    ANGELIC_BUSTER = (profession.ANGELIC_BUSTER, "DEX", "STR")
    MECHANIC = (profession.MECHANIC, "DEX", "STR")
    XENON = (profession.XENON, ["LUK", "DEX", "STR"], "")
    DEMON_AVENGER = (profession.DEMON_AVENGER, "HP", "STR")

    def __init__(self, job_name, main_status, sub_status):
        self.job_name = job_name
        self.main_status = main_status
        self.sub_status = sub_status