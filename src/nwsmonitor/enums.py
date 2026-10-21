from enum import Enum


class WFO(Enum):
    AAQ = "NWS National Tsunami Warning Center"
    HEB = "NWS Pacific Tsunami Warning Center"
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
    ASY = "Air Stagnation Advisory"
    AFW = "Ashfall Warning"
    AFY = "Ashfall Advisory"
    SAB = "Avalanche Advisory"
    AVW = "Avalanche Warning"
    AVA = "Avalanche Watch"
    BHS = "Beach Hazards Statement"
    BLU = "Blue Alert"
    BZW = "Blizzard Warning"
    BWY = "Brisk Wind Advisory"
    CAE = "Child Abduction Emergency"
    CDW = "Civil Danger Warning"
    CEM = "Civil Emergency Message"
    CFY = "Coastal Flood Advisory"
    CFS = "Coastal Flood Statement"
    CFW = "Coastal Flood Warning"
    CFA = "Coastal Flood Watch"
    CWY = "Cold Weather Advisory"
    FGY = "Dense Fog Advisory"
    SMY = "Dense Smoke Advisory"
    DSY = "Dust Advisory"
    DSW = "Dust Storm Warning"
    EQW = "Earthquake Warning"
    EVI = "Evacuation Immediate"
    EHW = "Extreme Heat Warning"
    EHA = "Extreme Heat Watch"
    ECW = "Extreme Cold Warning"
    ECA = "Extreme Cold Watch"
    RFD = "Extreme Fire Danger"
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
    ZYY = "Freezing Spray Advisory"
    ZFY = "Freezing Fog Advisory"
    FRY = "Frost Advisory"
    GLW = "Gale Warning"
    GLA = "Gale Watch"
    HZA = "Hard Freeze Watch"
    HZW = "Hard Freeze Warning"
    HMW = "Hazardous Materials Warning"
    SEW = "Hazardous Seas Warning"
    SEA = "Hazardous Seas Watch"
    HTY = "Heat Advisory"
    UPW = "Heavy Freezing Spray Warning"
    UPA = "Heavy Freezing Spray Watch"
    UPY = "Heavy Freezing Spray Advisory"
    SUY = "High Surf Advisory"
    SUW = "High Surf Warning"
    HWW = "High Wind Warning"
    HWA = "High Wind Watch"
    HFW = "Hurricane Force Wind Warning"
    HFA = "Hurricane Force Wind Watch"
    HLS = "Tropical Cyclone Statement"
    HUW = "Hurricane Warning"
    HUA = "Hurricane Watch"
    ESF = "Hydrologic Outlook"
    ISW = "Ice Storm Warning"
    WSW_LEW = "Lake Effect Snow Warning"
    LWY = "Lake Wind Advisory"
    LSY = "Lakeshore Flood Advisory"
    LSS = "Lakeshore Flood Statement"
    LSW = "Lakeshore Flood Warning"
    LSA = "Lakeshore Flood Watch"
    LEW = "Law Enforcement Warning"
    LAE = "Local Area Emergency"
    LOY = "Low Water Advisory"
    MWS = "Marine Weather Statement"
    NUW = "Nuclear Power Plant Warning"
    RHW = "Radiological Hazard Warning"
    RFW = "Red Flag Warning"
    RPS = "Rip Current Statement"
    SVR = "Severe Thunderstorm Warning"
    SVA = "Severe Thunderstorm Watch"
    SVS = "Severe Weather Statement"
    SPW = "Shelter In Place Warning"
    SCY = "Small Craft Advisory"
    SWY = "Small Craft Advisory For Hazardous Seas"
    RBY = "Small Craft Advisory For Rough Bar"
    SIY = "Small Craft Advisory For Winds"
    SQW = "Snow Squall Warning"
    SMW = "Special Marine Warning"
    SPS = "Special Weather Statement"
    SSW = "Storm Surge Warning"
    SSA = "Storm Surge Watch"
    SRW = "Storm Warning"
    SRA = "Storm Watch"
    TST = "Test Message"
    TOR = "Tornado Warning"
    TOA = "Tornado Watch"
    TRW = "Tropical Storm Warning"
    TRA = "Tropical Storm Watch"
    TSY = "Tsunami Advisory"
    TSU = "Tsunami Warning"
    TSA = "Tsunami Watch"
    TYS = "Typhoon Local Statement"
    TYW = "Typhoon Warning"
    TYA = "Typhoon Watch"
    VOW = "Volcano Warning"
    WIY = "Wind Advisory"
    WCY = "Wind Chill Advisory"
    WCW = "Wind Chill Warning"
    WCA = "Wind Chill Watch"
    WSW = "Winter Storm Warning"
    WSA = "Winter Storm Watch"
    WWY = "Winter Weather Advisory"


class SpecialAlert(Enum):
    """Specialized alert types which are sub-types of other alerts.
    These are often used to indicate a particularly dangerous situation.
    """

    PDS_SVR = "**Severe Thunderstorm Warning (Extremely Dangerous Situation)**"
    PDS_TOR = "**Tornado Warning (PDS)**"
    PDS_BZW = "**Blizzard Warning (PDS)**"
    PDS_ISW = "**Ice Storm Warning (PDS)**"
    PDS_RFW = "**Red Flag Warning (PDS)**"
    PDS_TOA = "**Tornado Watch (PDS)**"
    PDS_SVA = "**Severe Thunderstorm Watch (PDS)**"
    TOR_E = "**TORNADO EMERGENCY**"
    FFW_E = "**FLASH FLOOD EMERGENCY**"
    SVR_DESTRUCTIVE = "**Severe Thunderstorm Warning (Destructive)**"


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


class AutoplotSector(Enum):
    AK = "Alaska"
    AL = "Alabama"
    AS = "American Samoa"
    AR = "Arkansas"
    AZ = "Arizona"
    CA = "California"
    CO = "Colorado"
    CT = "Connecticut"
    DC = "District of Columbia"
    DE = "Deleware"
    FL = "Florida"
    GA = "Georgia"
    HI = "Hawaii"
    IA = "Iowa"
    ID = "Idaho"
    IL = "Illinois"
    IN = "Indiana"
    KS = "Kansas"
    KY = "Kentucky"
    LA = "Louisiana"
    MA = "Massachusetts"
    MD = "Maryland"
    ME = "Maine"
    MI = "Michigan"
    MN = "Minnesota"
    MO = "Missouri"
    MS = "Mississippi"
    MT = "Montana"
    NC = "North Carolina"
    ND = "North Dakota"
    NE = "Nebraska"
    NH = "New Hampshire"
    NJ = "New Jersey"
    NM = "New Mexico"
    NV = "Nevada"
    NY = "New York"
    OH = "Ohio"
    OK = "Oklahoma"
    OR = "Oregon"
    PA = "Pennsylvania"
    PR = "Puerto Rico"
    RI = "Rhode Island"
    SC = "South Carolina"
    SD = "South Dakota"
    TN = "Tennessee"
    TX = "Texas"
    UT = "Utah"
    VA = "Virginia"
    VI = "Virgin Islands"
    VT = "Vermont"
    WA = "Washington"
    WI = "Wisconsin"
    WV = "West Virginia"
    WY = "Wyoming"
    conus = "Contiguous US"
    cornbelt = "Corn Belt US"
    highplains = "High Plains"
    iailin = "IA + IL + IN"
    iailmo = "IA + IL + MO"
    midwest = "Midwestern US"
    northeast = "Northeastern US"
    sengland = "Southern New England"
    northwest = "Northwestern US"
    southeast = "Southeastern US"
    southernplains = "Southern Plains US"
    southwest = "Southwestern US"


STR_ALERTS = {a.value for a in AlertType}
MARINE_ALERTS = {
    AlertType.BWY,
    AlertType.UPY,
    AlertType.GLW,
    AlertType.GLA,
    AlertType.SEW,
    AlertType.SEA,
    AlertType.UPA,
    AlertType.UPW,
    AlertType.SRA,
    AlertType.SRW,
    AlertType.HFA,
    AlertType.HFW,
    AlertType.MWS,
    AlertType.SCY,
    AlertType.RBY,
    AlertType.SWY,
    AlertType.SIY,
    AlertType.SMW,
    AlertType.LOY,
    AlertType.ZYY,
}
REQUIRED_ALERTS = {
    AlertType.TOR,
    AlertType.SVR,
    AlertType.FFW,
    AlertType.CDW,
    AlertType.CEM,
    AlertType.WSW,
    AlertType.ISW,
    AlertType.BZW,
    AlertType.LEW,
    AlertType.LAE,
    AlertType.EWW,
    AlertType.TSU,
    AlertType.EQW,
    AlertType.EVI,
    AlertType.BLU,
    AlertType.HMW,
    AlertType.NUW,
    AlertType.RHW,
    AlertType.SPW,
    AlertType.SQW,
}
SVR_ALERTS = REQUIRED_ALERTS.union(
    {
        AlertType.TOA,
        AlertType.SVA,
        AlertType.SMW,
        AlertType.TOE,
        AlertType.SVS,
        AlertType.DSW,
        AlertType.TRA,
        AlertType.TRW,
        AlertType.HUA,
        AlertType.HUW,
        AlertType.TSA,
    }
)
STR_SVR_ALERTS = {a.value for a in SVR_ALERTS}
ALERTS_WITH_NO_END_TIME = {
    AlertType.TRA,
    AlertType.TRW,
    AlertType.SSA,
    AlertType.SSW,
    AlertType.HUA,
    AlertType.HUW,
    AlertType.HLS,
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
    AlertType.TSU,
    AlertType.TSA,
    AlertType.TSY,
    AlertType.AVA,
    AlertType.AVW,
    AlertType.SAB,
    AlertType.BLU,
}
STR_ALERTS_WITH_NO_END_TIME = {a.value for a in ALERTS_WITH_NO_END_TIME}
DEFAULT_EMOJI = {
    AlertType.ADR.value: ":newspaper:",
    AlertType.AVA.value: ":mountain_snow:",
    AlertType.AVW.value: ":mountain_snow:",
    AlertType.BHS.value: ":beach:",
    AlertType.BLU.value: ":blue_square",
    AlertType.BZW.value: ":exclamation: :cloud_snow:",
    SpecialAlert.PDS_BZW.value: ":bangbang: :cloud_snow:",
    AlertType.CAE.value: ":orange_square:",
    AlertType.FGY.value: ":fog:",
    AlertType.SMY.value: ":fog:",
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
    AlertType.ISW.value: ":exclamation: :ice_cube:",
    SpecialAlert.PDS_ISW.value: ":bangbang: :ice_cube:",
    AlertType.LWY.value: ":wind_face:",
    AlertType.LEW.value: ":rotating_light:",
    AlertType.RHW.value: ":biohazard:",
    AlertType.RFW.value: ":triangular_flag_on_post:",
    SpecialAlert.PDS_RFW.value: ":exclamation: :triangular_flag_on_post:",
    AlertType.SVR.value: ":cloud_lightning:",
    SpecialAlert.PDS_SVR.value: ":bangbang: :cloud_lightning:",
    SpecialAlert.SVR_DESTRUCTIVE.value: ":exclamation: :cloud_lightning:",
    AlertType.SVA.value: ":cloud:",
    SpecialAlert.PDS_SVA.value: ":exclamation: :cloud:",
    AlertType.SQW.value: ":wind_face: :cloud_snow:",
    AlertType.TOA.value: ":cloud:",
    SpecialAlert.PDS_TOA.value: ":bangbang: :cloud:",
    AlertType.TOR.value: ":cloud_tornado:",
    SpecialAlert.PDS_TOR.value: ":exclamation: :cloud_tornado:",
    SpecialAlert.TOR_E.value: ":bangbang: :cloud_tornado:",
    AlertType.TRW.value: ":cyclone:",
    AlertType.TRA.value: ":cyclone:",
    AlertType.TSY.value: ":exclamation: :ocean:",
    AlertType.TSA.value: ":ocean:",
    AlertType.TSU.value: ":bangbang: :ocean:",
    AlertType.TYS.value: ":cyclone:",
    AlertType.TYW.value: ":cyclone:",
    AlertType.TYA.value: ":cyclone:",
    AlertType.VOW.value: ":volcano:",
    AlertType.WIY.value: ":wind_face:",
    AlertType.WCY.value: ":cold_face:",
    AlertType.WCA.value: ":exclamation: :cold_face:",
    AlertType.WCW.value: ":bangbang: :cold_face:",
    AlertType.CWY.value: ":cold_face:",
    AlertType.ECA.value: ":exclamation: :cold_face:",
    AlertType.ECW.value: ":bangbang: :cold_face:",
    AlertType.WSW.value: ":cloud_snow:",
    AlertType.WSA.value: ":exclamation: :snowflake:",
    AlertType.WWY.value: ":snowflake:",
    AlertType.SUY.value: ":surfer:",
    AlertType.SUW.value: ":exclamation: :surfer:",
}
