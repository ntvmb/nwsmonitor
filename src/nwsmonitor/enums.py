from enum import Enum


class WFO(Enum):
    AAQ = "NWS National Tsunami Warning Center"
    AFG = "NWS Fairbanks AK"
    AFC = "NWS Anchorage AK"
    AJK = "NWS Juneau AK"
    GUM = "NWS Tiyan GU"
    HFO = "NWS Honolulu HI"
    SJU = "NWS San Juan PR"
    SEW = "NWS Seattle WA"
    OTX = "NWS Spokane WA"
    MSO = "NWS Missoula MT"
    TFX = "NWS Great Falls MT"
    GGW = "NWS Glasgow MT"
    BIS = "NWS Bismarck ND"
    FGF = "NWS Grand Forks ND"
    DLH = "NWS Duluth MN"
    MQT = "NWS Marquette MI"
    APX = "NWS Gaylord MI"
    BUF = "NWS Buffalo NY"
    BTV = "NWS Burlington VT"
    GYX = "NWS Gray ME"
    CAR = "NWS Caribou ME"
    PQR = "NWS Portland OR"
    PDT = "NWS Pendleton OR"
    BYZ = "NWS Billings MT"
    UNR = "NWS Rapid City SD"
    ABR = "NWS Aberdeen SD"
    MPX = "NWS Twin Cities/Chanhassen MN"
    ARX = "NWS La Crosse WI"
    GRB = "NWS Green Bay WI"
    BGM = "NWS Binghamton NY"
    ALY = "NWS Albany NY"
    BOX = "NWS Boston/Norton MA"
    MFR = "NWS Medford OR"
    BOI = "NWS Boise ID"
    PIH = "NWS Pocatello ID"
    RIW = "NWS Riverton WY"
    FSD = "NWS Sioux Falls SD"
    MKX = "NWS Milwaukee/Sullivan WI"
    GRR = "NWS Grand Rapids MI"
    DTX = "NWS Detroit/Pontiac MI"
    OKX = "NWS Upton NY"
    CYS = "NWS Cheyenne WY"
    LBF = "NWS North Platte NE"
    OAX = "NWS Omaha/Valley NE"
    DMX = "NWS Des Moines IA"
    DVN = "NWS Quad Cities IA IL"
    LOT = "NWS Chicago IL"
    IWX = "NWS Northern Indiana"
    CLE = "NWS Cleveland OH"
    CTP = "NWS State College PA"
    PHI = "NWS Mount Holly NJ"
    EKA = "NWS Eureka CA"
    STO = "NWS Sacramento CA"
    REV = "NWS Reno NV"
    LKN = "NWS Elko NV"
    SLC = "NWS Salt Lake City UT"
    GJT = "NWS Grand Junction CO"
    BOU = "NWS Denver CO"
    GLD = "NWS Goodland KS"
    GID = "NWS Hastings NE"
    TOP = "NWS Topeka KS"
    EAX = "NWS Kansas City/Pleasant Hill MO"
    LSX = "NWS St Louis MO"
    ILX = "NWS Lincoln IL"
    IND = "NWS Indianapolis IN"
    ILN = "NWS Wilmington OH"
    PBZ = "NWS Pittsburgh PA"
    RLX = "NWS Charleston WV"
    LWX = "NWS Baltimore MD/Washington DC"
    PUB = "NWS Pueblo CO"
    DDC = "NWS Dodge City KS"
    ICT = "NWS Wichita KS"
    SGF = "NWS Springfield MO"
    PAH = "NWS Paducah KY"
    LMK = "NWS Louisville KY"
    JKL = "NWS Jackson KY"
    RNK = "NWS Blacksburg VA"
    AKQ = "NWS Wakefield VA"
    MTR = "NWS San Francisco CA"
    HNX = "NWS Hanford CA"
    VEF = "NWS Las Vegas NV"
    FGZ = "NWS Flagstaff AZ"
    ABQ = "NWS Albuquerque NM"
    AMA = "NWS Amarillo TX"
    LUB = "NWS Lubbock TX"
    OUN = "NWS Norman OK"
    TSA = "NWS Tulsa OK"
    LZK = "NWS Little Rock AR"
    MEG = "NWS Memphis TN"
    HUN = "NWS Huntsville AL"
    OHX = "NWS Nashville TN"
    MRX = "NWS Morristown TN"
    GSP = "NWS Greenville-Spartanburg SC"
    RAH = "NWS Raleigh NC"
    MHX = "NWS Newport/Morehead City NC"
    LOX = "NWS Los Angeles/Oxnard CA"
    SGX = "NWS San Diego CA"
    PSR = "NWS Phoenix AZ"
    TWC = "NWS Tucson AZ"
    EPZ = "NWS El Paso Tx/Santa Teresa NM"
    MAF = "NWS Midland/Odessa TX"
    SJT = "NWS San Angelo TX"
    FWD = "NWS Fort Worth TX"
    SHV = "NWS Shreveport LA"
    JAN = "NWS Jackson MS"
    BMX = "NWS Birmingham AL"
    FFC = "NWS Peachtree City GA"
    CAE = "NWS Columbia SC"
    CHS = "NWS Charleston SC"
    ILM = "NWS Wilmington NC"
    EWX = "NWS Austin/San Antonio TX"
    HGX = "NWS Houston/Galveston TX"
    LCH = "NWS Lake Charles LA"
    LIX = "NWS New Orleans LA"
    MOB = "NWS Mobile AL"
    TAE = "NWS Tallahassee FL"
    JAX = "NWS Jacksonville FL"
    CRP = "NWS Corpus Christi TX"
    TBW = "NWS Tampa Bay Ruskin FL"
    MLB = "NWS Melbourne FL"
    BRO = "NWS Brownsville TX"
    MFL = "NWS Miami FL"
    KEY = "NWS Key West FL"


class AlertType(Enum):
    # NOT ALL EVENT CODES LISTED ARE OFFICIAL
    TOE = "911 Telephone Outage"
    ADR = "Administrative Message"
    AQA = "Air Quality Alert"
    ASA = "Air Stagnation Advisory"
    FLY_ARROYO = "Arroyo And Small Stream Flood Advisory"
    ASH_ADV = "Ashfall Advisory"
    ASH_WARN = "Ashfall Warning"
    AVY = "Avalanche Advisory"
    AVW = "Avalanche Warning"
    AVA = "Avalanche Watch"
    BHS = "Beach Hazards Statement"
    BLU = "Blue Alert"
    BZW = "Blizzard Warning"
    BZA = "Blizzard Watch"
    BDY = "Blowing Dust Advisory"
    BDW = "Blowing Dust Warning"
    BWY = "Brisk Wind Advisory"
    CAE = "Child Abduction Emergency"
    CDW = "Civil Danger Warning"
    CEM = "Civil Emergency Message"
    CFY = "Coastal Flood Advisory"
    CFS = "Coastal Flood Statement"
    CFW = "Coastal Flood Warning"
    CFA = "Coastal Flood Watch"
    CWY = "Cold Weather Advisory"
    FOG = "Dense Fog Advisory"
    SMOKE = "Dense Smoke Advisory"
    DUST = "Dust Advisory"
    DSW = "Dust Storm Warning"
    EQW = "Earthquake Warning"
    EVI = "Evacuation Immediate"
    EHW = "Excessive Heat Warning"
    EHA = "Excessive Heat Watch"
    ECW = "Extreme Cold Warning"
    ECA = "Extreme Cold Watch"
    EFD = "Extreme Fire Danger"
    EWW = "Extreme Wind Warning"
    FRW = "Fire Warning"
    FWA = "Fire Weather Watch"
    FFS = "Flash Flood Statement"
    FFW = "Flash Flood Warning"
    FFA = "Flash Flood Watch"
    FLY = "Flood Advisory"
    FLS = "Flood Statement"
    FLW = "Flood Warning"
    FLA = "Flood Watch"
    FZW = "Freeze Warning"
    FZA = "Freeze Watch"
    FREEZING_FOG = "Freezing Fog Advisory"
    FREEZING_RAIN = "Freezing Rain Advisory"
    F_SPRAY_Y = "Freezing Spray Advisory"
    FZY = "Frost Advisory"
    GALE_WARN = "Gale Warning"
    GALE_WATCH = "Gale Watch"
    HARD_FREEZE_WARN = "Hard Freeze Warning"
    HARD_FREEZE_WATCH = "Hard Freeze Watch"
    HMW = "Hazardous Materials Warning"
    HAZARDOUS_SEAS_WARN = "Hazardous Seas Warning"
    HAZARDOUS_SEAS_WATCH = "Hazardous Seas Watch"
    HWO = "Hazardous Weather Outlook"
    HTY = "Heat Advisory"
    F_SPRAY_W = "Heavy Freezing Spray Warning"
    F_SPRAY_A = "Heavy Freezing Spray Watch"
    H_SURF_Y = "High Surf Advisory"
    H_SURF_W = "High Surf Warning"
    HWW = "High Wind Warning"
    HWA = "High Wind Watch"
    FORCE_12_W = "Hurricane Force Wind Warning"
    FORCE_12_A = "Hurricane Force Wind Watch"
    HLS = "Tropical Cyclone Statement"
    HUW = "Hurricane Warning"
    HUA = "Hurricane Watch"
    HYDRO_ADV = "Hydrologic Advisory"
    ESF = "Hydrologic Outlook"
    ICE = "Ice Storm Warning"
    LE_SNOW_Y = "Lake Effect Snow Advisory"
    LE_SNOW_W = "Lake Effect Snow Warning"
    LE_SNOW_A = "Lake Effect Snow Watch"
    LAKE_WIND = "Lake Wind Advisory"
    LFY = "Lakeshore Flood Advisory"
    LFS = "Lakeshore Flood Statement"
    LFW = "Lakeshore Flood Warning"
    LFA = "Lakeshore Flood Watch"
    LEW = "Law Enforcement Warning"
    LAE = "Local Area Emergency"
    LOW_WATER = "Low Water Advisory"
    MWS = "Marine Weather Statement"
    NUW = "Nuclear Power Plant Warning"
    RHW = "Radiological Hazard Warning"
    RFW = "Red Flag Warning"
    RIP_CURRENT = "Rip Current Statement"
    SVR = "Severe Thunderstorm Warning"
    SVA = "Severe Thunderstorm Watch"
    SVS = "Severe Weather Statement"
    SPW = "Shelter In Place Warning"
    NOW = "Short Term Forecast"
    SCY = "Small Craft Advisory"
    SCY_SEAS = "Small Craft Advisory For Hazardous Seas"
    SCY_BAR = "Small Craft Advisory For Rough Bar"
    SCY_WIND = "Small Craft Advisory For Winds"
    FLY_SMALL_STREAM = "Small Stream Flood Advisory"
    SQW = "Snow Squall Warning"
    SMW = "Special Marine Warning"
    SPS = "Special Weather Statement"
    SSW = "Storm Surge Warning"
    SSA = "Storm Surge Watch"
    STORM_W = "Storm Warning"
    STORM_A = "Storm Watch"
    TEST = "Test Message"
    TOR = "Tornado Warning"
    TOA = "Tornado Watch"
    TRW = "Tropical Storm Warning"
    TRA = "Tropical Storm Watch"
    TSY = "Tsunami Advisory"
    TSW = "Tsunami Warning"
    TSA = "Tsunami Watch"
    TYLS = "Typhoon Local Statement"
    TYW = "Typhoon Warning"
    TYA = "Typhoon Watch"
    FLY_URBAN = "Urban And Small Stream Flood Advisory"
    VOW = "Volcano Warning"
    WIND = "Wind Advisory"
    WCY = "Wind Chill Advisory"
    WCW = "Wind Chill Warning"
    WCA = "Wind Chill Watch"
    WSW = "Winter Storm Warning"
    WSA = "Winter Storm Watch"
    WSY = "Winter Weather Advisory"


class SpecialAlert(Enum):
    """Specialized alert types which are sub-types of other alerts.
    These are often used to indicate a particularly dangerous situation.
    """

    PDS_SVR = "**Severe Thunderstorm Warning (PDS)**"
    PDS_TOR = "**Tornado Warning (PDS)**"
    TOR_E = "**TORNADO EMERGENCY**"
    FFW_E = "**FLASH FLOOD EMERGENCY**"


class ValidTimeEventCodeVerb(Enum):
    """Verbs that correspond to alert statuses given a Valid Time Event
    Code (VTEC).
    """

    NEW = "issues"
    UPG = "upgrades"
    CON = "continues"
    CAN = "cancels"
    EXA = "expands area of"
    EXB = "extends time and expands area of"
    EXT = "extends time of"
    EXP = "expires"
    COR = "corrects"
    default = "updates"

    @classmethod
    def _missing_(cls, value):
        return cls.default


MARINE_ALERTS = {
    AlertType.BWY,
    AlertType.F_SPRAY_Y,
    AlertType.GALE_WARN,
    AlertType.GALE_WATCH,
    AlertType.HAZARDOUS_SEAS_WARN,
    AlertType.HAZARDOUS_SEAS_WATCH,
    AlertType.F_SPRAY_A,
    AlertType.F_SPRAY_W,
    AlertType.FORCE_12_A,
    AlertType.FORCE_12_W,
    AlertType.MWS,
    AlertType.SCY,
    AlertType.SCY_BAR,
    AlertType.SCY_SEAS,
    AlertType.SCY_WIND,
    AlertType.SMW,
}
REQUIRED_ALERTS = {
    AlertType.TOR,
    AlertType.SVR,
    AlertType.FFW,
    AlertType.CDW,
    AlertType.CEM,
    AlertType.WSW,
    AlertType.ICE,
    AlertType.BZW,
    AlertType.LEW,
    AlertType.LAE,
    AlertType.EWW,
}
ALERTS_WITH_NO_END_TIME = {
    AlertType.TRA,
    AlertType.TRW,
    AlertType.SSA,
    AlertType.SSW,
    AlertType.HUA,
    AlertType.HUW,
    AlertType.HLS,
    AlertType.HWO,
    AlertType.ESF,
    AlertType.CEM,
    AlertType.CAE,
    AlertType.CDW,
    AlertType.LEW,
    AlertType.LAE,
    AlertType.EVI,
    AlertType.HMW,
    AlertType.NUW,
    AlertType.RHW,
    AlertType.SPW,
    AlertType.FRW,
    AlertType.TOE,
    AlertType.NOW,
}
STR_ALERTS_WITH_NO_END_TIME = {a.value for a in ALERTS_WITH_NO_END_TIME}
DEFAULT_EMOJI = {
    AlertType.ADR.value: ":newspaper:",
    AlertType.AVY.value: ":mountain_snow:",
    AlertType.AVA.value: ":mountain_snow:",
    AlertType.AVW.value: ":mountain_snow:",
    AlertType.BHS.value: ":beach:",
    AlertType.BLU.value: ":blue_square",
    AlertType.BZW.value: ":bangbang: :cloud_snow:",
    AlertType.BZA.value: ":exclamation: :cloud_snow:",
    AlertType.CAE.value: ":orange_square:",
    AlertType.FOG.value: ":fog:",
    AlertType.SMOKE.value: ":fog:",
    AlertType.EHW.value: ":hot_face:",
    AlertType.EHA.value: ":sunny:",
    AlertType.EWW.value: ":bangbang: :wind_face:",
    AlertType.FRW.value: ":fire:",
    AlertType.FWA.value: ":triangular_flag_on_post:",
    AlertType.FFW.value: ":cloud_rain:",
    SpecialAlert.FFW_E.value: ":bangbang: :cloud_rain:",
    AlertType.HTY.value: ":sunny:",
    AlertType.HWW.value: ":exclamation: :wind_face:",
    AlertType.HWA.value: ":wind_face:",
    AlertType.HLS.value: ":cyclone:",
    AlertType.HUW.value: ":cyclone:",
    AlertType.HUA.value: ":cyclone:",
    AlertType.ESF.value: ":bar_chart:",
    AlertType.ICE.value: ":exclamation: :ice_cube:",
    AlertType.LAKE_WIND.value: ":wind_face:",
    AlertType.LEW.value: ":rotating_light:",
    AlertType.RHW.value: ":biohazard:",
    AlertType.RFW.value: ":triangular_flag_on_post:",
    AlertType.SVR.value: ":cloud_lightning:",
    SpecialAlert.PDS_SVR.value: ":exclamation: :cloud_lightning:",
    AlertType.SVA.value: ":cloud:",
    AlertType.NOW.value: ":bar_chart:",
    AlertType.SQW.value: ":wind_face: :cloud_snow:",
    AlertType.TOR.value: ":cloud_tornado:",
    SpecialAlert.PDS_TOR.value: ":exclamation: :cloud_tornado:",
    SpecialAlert.TOR_E.value: ":bangbang: :cloud_tornado:",
    AlertType.TRW.value: ":cyclone:",
    AlertType.TRA.value: ":cyclone:",
    AlertType.TSY.value: ":exclamation: :ocean:",
    AlertType.TSA.value: ":ocean:",
    AlertType.TSW.value: ":bangbang: :ocean:",
    AlertType.TYLS.value: ":cyclone:",
    AlertType.TYW.value: ":cyclone:",
    AlertType.TYA.value: ":cyclone:",
    AlertType.VOW.value: ":volcano:",
    AlertType.WIND.value: ":wind_face:",
    AlertType.WCY.value: ":cold_face:",
    AlertType.WCA.value: ":exclamation: :cold_face:",
    AlertType.WCW.value: ":bangbang: :cold_face:",
    AlertType.CWY.value: ":cold_face:",
    AlertType.ECA.value: ":exclamation: :cold_face:",
    AlertType.ECW.value: ":bangbang: :cold_face:",
    AlertType.WSW.value: ":cloud_snow:",
    AlertType.WSA.value: ":exclamation: :snowflake:",
    AlertType.WSY.value: ":snowflake:",
    AlertType.H_SURF_Y.value: ":surfer:",
    AlertType.H_SURF_W.value: ":exclamation: :surfer:",
}
