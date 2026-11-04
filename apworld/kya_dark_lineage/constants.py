"""Kya Archipelago 0.6.3 rewards test data, PAL SLES_514.73."""
GAME_NAME = "Kya: Dark Lineage"
PROTOTYPE_VERSION = "0.6.3-test"
ITEM_ID_BASE = 51473000
LOCATION_ID_BASE = 51474000

ITEM_BASIC_BOOMY = "Basic Boomy"
ITEM_PROGRESSIVE_LIFE_GAUGE = "Progressive Life Gauge"
ITEM_MAGIC_REGENERATION = "Magic Regeneration"
ITEM_HP_RESTORE = "HP Restore +50"
ITEM_MAGIC_RESTORE = "Magic Restore +50"
ITEM_ATTACK_BONUS = "+5% Attack"
ITEM_PROTECTION_BONUS = "+5% Protection"
ITEM_REWARD_COUNTS = {
    ITEM_PROGRESSIVE_LIFE_GAUGE: 4,
    ITEM_MAGIC_REGENERATION: 1,
    ITEM_HP_RESTORE: 40,
    ITEM_MAGIC_RESTORE: 40,
    ITEM_ATTACK_BONUS: 5,
    ITEM_PROTECTION_BONUS: 5,
}
ITEM_USEFUL = frozenset((
    ITEM_PROGRESSIVE_LIFE_GAUGE,
    ITEM_MAGIC_REGENERATION,
    ITEM_ATTACK_BONUS,
    ITEM_PROTECTION_BONUS,
))
ITEM_CONSUMABLE_FILLER = frozenset((ITEM_HP_RESTORE, ITEM_MAGIC_RESTORE))
ITEM_PROGRESSIVE_RUNE_PREFIX = "Progressive Rune: "
ITEM_NOOTIES = ("Nooties +50", "Nooties +100", "Nooties +200", "Nooties +500")
ITEM_RUNES = (
    "Progressive Rune: Root's Rune",
    "Progressive Rune: Hunter's Domain Rune",
    "Progressive Rune: Quarry's Rune",
    "Progressive Rune: Air Post Rune",
    "Progressive Rune: Forgotten Island Rune",
    "Progressive Rune: Flying Forest Rune",
)
ITEM_KEY_ITEMS = ("Blue Egg", "Receptacle")
ITEM_NAME_TO_ID = {
    'Basic Boomy': ITEM_ID_BASE + 1,
    'Nooties +50': ITEM_ID_BASE + 3,
    'Nooties +100': ITEM_ID_BASE + 12,
    'Nooties +200': ITEM_ID_BASE + 13,
    'Nooties +500': ITEM_ID_BASE + 14,
    "Progressive Rune: Root's Rune": ITEM_ID_BASE + 4,
    "Progressive Rune: Hunter's Domain Rune": ITEM_ID_BASE + 5,
    "Progressive Rune: Quarry's Rune": ITEM_ID_BASE + 6,
    'Progressive Rune: Air Post Rune': ITEM_ID_BASE + 7,
    'Progressive Rune: Forgotten Island Rune': ITEM_ID_BASE + 8,
    'Progressive Rune: Flying Forest Rune': ITEM_ID_BASE + 9,
    'Blue Egg': ITEM_ID_BASE + 10,
    'Receptacle': ITEM_ID_BASE + 11,
    ITEM_PROGRESSIVE_LIFE_GAUGE: ITEM_ID_BASE + 15,
    ITEM_MAGIC_REGENERATION: ITEM_ID_BASE + 16,
    ITEM_HP_RESTORE: ITEM_ID_BASE + 17,
    ITEM_MAGIC_RESTORE: ITEM_ID_BASE + 18,
    ITEM_ATTACK_BONUS: ITEM_ID_BASE + 19,
    ITEM_PROTECTION_BONUS: ITEM_ID_BASE + 20,
}

ITEM_RUNE_SCENARIO_VARS = {
    "Progressive Rune: Root's Rune": 0x004254B4,
    "Progressive Rune: Hunter's Domain Rune": 0x0042551C,
    "Progressive Rune: Quarry's Rune": 0x0042554C,
    'Progressive Rune: Air Post Rune': 0x00425574,
    'Progressive Rune: Forgotten Island Rune': 0x00425594,
    'Progressive Rune: Flying Forest Rune': 0x004254E4,
}

ITEM_SCENARIO_FLAGS = {
    'Blue Egg': 0x004253EC,
    'Receptacle': 0x0042544C,
    ITEM_MAGIC_REGENERATION: 0x00425434,
}

WOLFEN_KEY_TO_LOCATION = {
    0x0138: 'Hunters Domain - Wolfen 55',
    0x014A: 'Hunters Domain - Wolfen 56',
    0x014B: 'Hunters Domain - Wolfen 54',
    0x0150: 'Hunters Domain - Wolfen 53',
    0x01A2: 'Hunters Domain - Wolfen 79',
    0x01A4: 'Hunters Domain - Wolfen 80',
    0x01AE: 'Hunters Domain - Wolfen 81',
    0x01EE: 'Wolfen City - Wolfen 06',
    0x0286: 'Hunters Domain - Wolfen 95',
    0x02F0: 'Wolfen City - Wolfen 10',
    0x0302: 'Wolfen City - Wolfen 40',
    0x0303: 'Wolfen City - Wolfen 41',
    0x030A: 'Wolfen City - Wolfen 12',
    0x0327: 'Wolfen City - Wolfen 17',
    0x0337: 'The Quarry - Wolfen 15',
    0x037F: 'The Fortress - Wolfen 14',
    0x0395: 'Hunters Domain - Wolfen 64',
    0x03D8: 'Nativs City - Wolfen 01',
    0x03F2: 'Hunters Domain - Wolfen 66',
    0x040A: 'Hunters Domain - Wolfen 65',
    0x0461: 'The Fortress - Wolfen 10',
    0x0462: 'The Fortress - Wolfen 09',
    0x0464: 'The Fortress - Wolfen 13',
    0x0465: 'The Fortress - Wolfen 07',
    0x0466: 'The Fortress - Wolfen 02',
    0x0468: 'The Fortress - Wolfen 05',
    0x0469: 'The Fortress - Wolfen 11',
    0x046A: 'The Quarry - Wolfen 02',
    0x046B: 'The Fortress - Wolfen 12',
    0x046C: 'The Fortress - Wolfen 08',
    0x046D: 'The Fortress - Wolfen 01',
    0x046E: 'The Fortress - Wolfen 03',
    0x0476: 'The Quarry - Wolfen 09',
    0x0477: 'The Quarry - Wolfen 10',
    0x047B: 'The Fortress - Wolfen 06',
    0x048A: 'The Quarry - Wolfen 08',
    0x04F3: 'Wolfen City - Wolfen 37',
    0x04F4: 'Wolfen City - Wolfen 36',
    0x04F5: 'Wolfen City - Wolfen 39',
    0x04F6: 'Wolfen City - Wolfen 38',
    0x052F: 'The Air Post - Wolfen 49',
    0x054D: 'Hunters Domain - Wolfen 59',
    0x055E: 'Wolfen City - Wolfen 11',
    0x058E: 'Wolfen City - Wolfen 05',
    0x0595: 'The Quarry - Wolfen 14',
    0x059A: 'Wolfen City - Wolfen 03',
    0x059D: 'The Quarry - Wolfen 18',
    0x05A3: 'Wolfen City - Wolfen 04',
    0x05A9: 'The Air Post - Wolfen 53',
    0x05EE: 'Hunters Domain - Wolfen 74',
    0x0669: 'Wolfen City - Wolfen 15',
    0x0674: 'Wolfen City - Wolfen 16',
    0x0690: 'Wolfen City - Wolfen 19',
    0x06CE: 'Hunters Domain - Wolfen 46',
    0x06D0: 'Hunters Domain - Wolfen 45',
    0x06D6: 'Wolfen City - Wolfen 09',
    0x06FB: 'Wolfen City - Wolfen 22',
    0x071E: 'Wolfen City - Wolfen 20',
    0x0732: 'Wolfen City - Wolfen 31',
    0x075D: 'Hunters Domain - Wolfen 48',
    0x0778: 'The Air Post - Wolfen 45',
    0x07C5: 'Wolfen City - Wolfen 35',
    0x07CE: 'Wolfen City - Wolfen 33',
    0x07CF: 'Wolfen City - Wolfen 34',
    0x07D4: 'Wolfen City - Wolfen 32',
    0x07F5: 'Hunters Domain - Wolfen 49',
    0x0806: 'Forgotten Island - Wolfen 01',
    0x0824: 'Forgotten Island - Wolfen 02',
    0x0836: 'Forgotten Island - Wolfen 03',
    0x08D4: 'Flying Forest - Wolfen 09',
    0x08F9: 'Flying Forest - Wolfen 10',
    0x091D: 'Wolfen City - Wolfen 26',
    0x091F: 'Wolfen City - Wolfen 30',
    0x0921: 'Wolfen City - Wolfen 28',
    0x0923: 'Wolfen City - Wolfen 29',
    0x0925: 'Wolfen City - Wolfen 27',
    0x0926: 'Flying Forest - Wolfen 03',
    0x092F: 'Flying Forest - Wolfen 12',
    0x0932: 'Flying Forest - Wolfen 17',
    0x095E: 'Flying Forest - Wolfen 14',
    0x0993: 'Flying Forest - Wolfen 24',
    0x0995: 'Flying Forest - Wolfen 23',
    0x099E: 'Flying Forest - Wolfen 20',
    0x09FC: 'The Quarry - Wolfen 24',
    0x0A36: 'Flying Forest - Wolfen 30',
    0x0A37: 'Flying Forest - Wolfen 37',
    0x0A38: 'Flying Forest - Wolfen 31',
    0x0A39: 'Flying Forest - Wolfen 36',
    0x0A3A: 'Flying Forest - Wolfen 33',
    0x0A3B: 'Flying Forest - Wolfen 34',
    0x0A3C: 'Flying Forest - Wolfen 32',
    0x0A3D: 'Flying Forest - Wolfen 29',
    0x0A3E: 'Flying Forest - Wolfen 35',
    0x0A60: 'Flying Forest - Wolfen 19',
    0x0A80: 'Wolfen City - Wolfen 02',
    0x0A81: 'Flying Forest - Wolfen 25',
    0x0AA6: 'Flying Forest - Wolfen 27',
    0x0AA7: 'Flying Forest - Wolfen 26',
    0x0B0C: 'Flying Forest - Wolfen 28',
    0x0C28: 'Flying Forest - Wolfen 22',
    0x0C8A: 'Flying Forest - Wolfen 18',
    0x0CA3: 'Flying Forest - Wolfen 11',
    0x0CA5: 'Flying Forest - Wolfen 13',
    0x0CC3: 'The Quarry - Wolfen 23',
    0x0CC6: 'Flying Forest - Wolfen 16',
    0x0D89: 'Hunters Domain - Wolfen 39',
    0x0D8A: 'Hunters Domain - Wolfen 37',
    0x0D8B: 'Hunters Domain - Wolfen 38',
    0x0D8D: 'Hunters Domain - Wolfen 36',
    0x0D9E: 'Hunters Domain - Wolfen 50',
    0x0E5D: 'Wolfen City - Wolfen 08',
    0x0E5E: 'Wolfen City - Wolfen 07',
    0x0E67: 'Wolfen City - Wolfen 13',
    0x0E73: 'Wolfen City - Wolfen 21',
    0x0E93: 'Hunters Domain - Wolfen 52',
    0x0E94: 'Hunters Domain - Wolfen 51',
    0x0E95: 'Wolfen City - Wolfen 14',
    0x0E96: 'Wolfen City - Wolfen 18',
    0x0EB1: 'Wolfen City - Wolfen 25',
    0x0EB2: 'Wolfen City - Wolfen 23',
    0x0ECF: 'Wolfen City - Wolfen 24',
    0x0F1C: 'The Quarry - Wolfen 22',
    0x1088: 'The Quarry - Wolfen 16',
    0x1150: 'Hunters Domain - Wolfen 60',
    0x1151: 'Hunters Domain - Wolfen 61',
    0x120D: 'Hunters Domain - Wolfen 72',
    0x120E: 'Hunters Domain - Wolfen 70',
    0x1210: 'Hunters Domain - Wolfen 73',
    0x1213: 'Hunters Domain - Wolfen 71',
    0x1240: 'Flying Forest - Wolfen 15',
    0x1292: 'Hunters Domain - Wolfen 94',
    0x1293: 'Hunters Domain - Wolfen 91',
    0x1294: 'Hunters Domain - Wolfen 89',
    0x1295: 'Hunters Domain - Wolfen 90',
    0x1296: 'Hunters Domain - Wolfen 92',
    0x1297: 'Hunters Domain - Wolfen 93',
    0x1350: 'Forgotten Island - Wolfen 07',
    0x13C3: 'Forgotten Island - Wolfen 04',
    0x13C4: 'Forgotten Island - Wolfen 05',
    0x1498: 'Flying Forest - Wolfen 05',
    0x154E: 'Flying Forest - Wolfen 07',
    0x154F: 'Flying Forest - Wolfen 08',
    0x1550: 'Flying Forest - Wolfen 06',
    0x176F: 'The Quarry - Wolfen 03',
    0x177A: 'The Quarry - Wolfen 04',
    0x1781: 'The Quarry - Wolfen 19',
    0x17BE: 'The Quarry - Wolfen 28',
    0x17BF: 'The Quarry - Wolfen 30',
    0x17CD: 'The Quarry - Wolfen 31',
    0x17D0: 'The Quarry - Wolfen 29',
    0x17F6: 'Flying Forest - Wolfen 04',
    0x1847: 'Forgotten Island - Wolfen 06',
    0x18B0: 'Hunters Domain - Wolfen 40',
    0x197E: 'The Quarry - Wolfen 26',
    0x197F: 'The Quarry - Wolfen 27',
    0x1A9B: 'Forgotten Island - Wolfen 08',
    0x1BA5: 'Flying Forest - Wolfen 21',
    0x1C75: 'The Air Post - Wolfen 47',
    0x1D15: 'Hunters Domain - Wolfen 76',
    0x1D91: 'The Quarry - Wolfen 38',
    0x1DB2: 'Hunters Domain - Wolfen 96',
    0x1E6E: 'Hunters Domain - Wolfen 87',
    0x1E6F: 'Hunters Domain - Wolfen 85',
    0x1E70: 'Hunters Domain - Wolfen 84',
    0x1E71: 'Hunters Domain - Wolfen 86',
    0x1E72: 'Hunters Domain - Wolfen 88',
    0x1E73: 'Hunters Domain - Wolfen 83',
    0x208A: 'Hunters Domain - Wolfen 47',
    0x20E5: 'The Air Post - Wolfen 46',
    0x2227: 'Hunters Domain - Wolfen 42',
    0x2236: 'The Air Post - Wolfen 50',
    0x23AD: 'Hunters Domain - Wolfen 43',
    0x23F3: 'The Air Post - Wolfen 58',
    0x23F4: 'The Air Post - Wolfen 59',
    0x247B: 'The Quarry - Wolfen 25',
    0x24B0: 'The Quarry - Wolfen 20',
    0x24B2: 'The Quarry - Wolfen 21',
    0x24B6: 'Hunters Domain - Wolfen 82',
    0x24DC: 'The Quarry - Wolfen 07',
    0x24DD: 'The Quarry - Wolfen 06',
    0x24FA: 'The Quarry - Wolfen 05',
    0x2527: 'The Quarry - Wolfen 39',
    0x2529: 'The Quarry - Wolfen 42',
    0x252B: 'The Quarry - Wolfen 40',
    0x252C: 'The Quarry - Wolfen 43',
    0x252E: 'The Quarry - Wolfen 41',
    0x2538: 'The Quarry - Wolfen 44',
    0x2542: 'The Quarry - Wolfen 45',
    0x257B: 'The Air Post - Wolfen 61',
    0x257D: 'The Air Post - Wolfen 43',
    0x257E: 'The Air Post - Wolfen 41',
    0x2580: 'The Air Post - Wolfen 42',
    0x25AC: 'The Quarry - Wolfen 11',
    0x25AD: 'The Quarry - Wolfen 13',
    0x25AE: 'The Quarry - Wolfen 12',
    0x25F9: 'The Quarry - Wolfen 17',
    0x2649: 'Hunters Domain - Wolfen 78',
    0x2659: 'Hunters Domain - Wolfen 77',
    0x2671: 'The Quarry - Wolfen 37',
    0x2672: 'The Quarry - Wolfen 34',
    0x2673: 'The Quarry - Wolfen 33',
    0x2675: 'The Quarry - Wolfen 32',
    0x2680: 'Hunters Domain - Wolfen 75',
    0x26D4: 'Hunters Domain - Wolfen 57',
    0x26D7: 'Hunters Domain - Wolfen 58',
    0x26D8: 'The Air Post - Wolfen 48',
    0x26DA: 'The Air Post - Wolfen 55',
    0x26DD: 'The Air Post - Wolfen 56',
    0x26DE: 'The Air Post - Wolfen 57',
    0x2704: 'The Quarry - Wolfen 35',
    0x2705: 'The Quarry - Wolfen 36',
    0x2753: 'The Air Post - Wolfen 54',
    0x275E: 'The Air Post - Wolfen 52',
    0x275F: 'The Air Post - Wolfen 51',
    0x2848: 'Hunters Domain - Wolfen 26',
    0x2849: 'Hunters Domain - Wolfen 27',
    0x286D: 'Hunters Domain - Wolfen 32',
    0x288C: 'The Air Post - Wolfen 60',
    0x28A3: 'Hunters Domain - Wolfen 62',
    0x28F5: 'Hunters Domain - Wolfen 33',
    0x296A: 'The Quarry - Wolfen 01',
    0x2972: 'Hunters Domain - Wolfen 44',
    0x2975: 'The Air Post - Wolfen 44',
    0x2A2D: 'Hunters Domain - Wolfen 29',
    0x2A34: 'Hunters Domain - Wolfen 28',
    0x2AE2: 'Hunters Domain - Wolfen 41',
    0x2C7D: 'Hunters Domain - Wolfen 67',
    0x2C7F: 'Hunters Domain - Wolfen 63',
    0x2C81: 'Hunters Domain - Wolfen 69',
    0x2CA0: 'Hunters Domain - Wolfen 35',
    0x2CB3: 'Hunters Domain - Wolfen 31',
    0x2CB4: 'Hunters Domain - Wolfen 30',
    0x2CD2: 'Hunters Domain - Wolfen 34',
    0x2DE7: 'Hunters Domain - Wolfen 68',
}

WOLFEN_LOCATIONS_BY_ZONE = {
    'Flying Forest': ('Flying Forest - Wolfen 03', 'Flying Forest - Wolfen 04', 'Flying Forest - Wolfen 05', 'Flying Forest - Wolfen 06', 'Flying Forest - Wolfen 07', 'Flying Forest - Wolfen 08', 'Flying Forest - Wolfen 09', 'Flying Forest - Wolfen 10', 'Flying Forest - Wolfen 11', 'Flying Forest - Wolfen 12', 'Flying Forest - Wolfen 13', 'Flying Forest - Wolfen 14', 'Flying Forest - Wolfen 15', 'Flying Forest - Wolfen 16', 'Flying Forest - Wolfen 17', 'Flying Forest - Wolfen 18', 'Flying Forest - Wolfen 19', 'Flying Forest - Wolfen 20', 'Flying Forest - Wolfen 21', 'Flying Forest - Wolfen 22', 'Flying Forest - Wolfen 23', 'Flying Forest - Wolfen 24', 'Flying Forest - Wolfen 25', 'Flying Forest - Wolfen 26', 'Flying Forest - Wolfen 27', 'Flying Forest - Wolfen 28', 'Flying Forest - Wolfen 29', 'Flying Forest - Wolfen 30', 'Flying Forest - Wolfen 31', 'Flying Forest - Wolfen 32', 'Flying Forest - Wolfen 33', 'Flying Forest - Wolfen 34', 'Flying Forest - Wolfen 35', 'Flying Forest - Wolfen 36', 'Flying Forest - Wolfen 37'),
    'Forgotten Island': ('Forgotten Island - Wolfen 01', 'Forgotten Island - Wolfen 02', 'Forgotten Island - Wolfen 03', 'Forgotten Island - Wolfen 04', 'Forgotten Island - Wolfen 05', 'Forgotten Island - Wolfen 06', 'Forgotten Island - Wolfen 07', 'Forgotten Island - Wolfen 08'),
    'Hunters Domain': ('Hunters Domain - Wolfen 26', 'Hunters Domain - Wolfen 27', 'Hunters Domain - Wolfen 28', 'Hunters Domain - Wolfen 29', 'Hunters Domain - Wolfen 30', 'Hunters Domain - Wolfen 31', 'Hunters Domain - Wolfen 32', 'Hunters Domain - Wolfen 33', 'Hunters Domain - Wolfen 34', 'Hunters Domain - Wolfen 35', 'Hunters Domain - Wolfen 36', 'Hunters Domain - Wolfen 37', 'Hunters Domain - Wolfen 38', 'Hunters Domain - Wolfen 39', 'Hunters Domain - Wolfen 40', 'Hunters Domain - Wolfen 41', 'Hunters Domain - Wolfen 42', 'Hunters Domain - Wolfen 43', 'Hunters Domain - Wolfen 44', 'Hunters Domain - Wolfen 45', 'Hunters Domain - Wolfen 46', 'Hunters Domain - Wolfen 47', 'Hunters Domain - Wolfen 48', 'Hunters Domain - Wolfen 49', 'Hunters Domain - Wolfen 50', 'Hunters Domain - Wolfen 51', 'Hunters Domain - Wolfen 52', 'Hunters Domain - Wolfen 53', 'Hunters Domain - Wolfen 54', 'Hunters Domain - Wolfen 55', 'Hunters Domain - Wolfen 56', 'Hunters Domain - Wolfen 57', 'Hunters Domain - Wolfen 58', 'Hunters Domain - Wolfen 59', 'Hunters Domain - Wolfen 60', 'Hunters Domain - Wolfen 61', 'Hunters Domain - Wolfen 62', 'Hunters Domain - Wolfen 63', 'Hunters Domain - Wolfen 64', 'Hunters Domain - Wolfen 65', 'Hunters Domain - Wolfen 66', 'Hunters Domain - Wolfen 67', 'Hunters Domain - Wolfen 68', 'Hunters Domain - Wolfen 69', 'Hunters Domain - Wolfen 70', 'Hunters Domain - Wolfen 71', 'Hunters Domain - Wolfen 72', 'Hunters Domain - Wolfen 73', 'Hunters Domain - Wolfen 74', 'Hunters Domain - Wolfen 75', 'Hunters Domain - Wolfen 76', 'Hunters Domain - Wolfen 77', 'Hunters Domain - Wolfen 78', 'Hunters Domain - Wolfen 79', 'Hunters Domain - Wolfen 80', 'Hunters Domain - Wolfen 81', 'Hunters Domain - Wolfen 82', 'Hunters Domain - Wolfen 83', 'Hunters Domain - Wolfen 84', 'Hunters Domain - Wolfen 85', 'Hunters Domain - Wolfen 86', 'Hunters Domain - Wolfen 87', 'Hunters Domain - Wolfen 88', 'Hunters Domain - Wolfen 89', 'Hunters Domain - Wolfen 90', 'Hunters Domain - Wolfen 91', 'Hunters Domain - Wolfen 92', 'Hunters Domain - Wolfen 93', 'Hunters Domain - Wolfen 94', 'Hunters Domain - Wolfen 95', 'Hunters Domain - Wolfen 96'),
    'Nativs City': ('Nativs City - Wolfen 01',),
    'The Air Post': ('The Air Post - Wolfen 41', 'The Air Post - Wolfen 42', 'The Air Post - Wolfen 43', 'The Air Post - Wolfen 44', 'The Air Post - Wolfen 45', 'The Air Post - Wolfen 46', 'The Air Post - Wolfen 47', 'The Air Post - Wolfen 48', 'The Air Post - Wolfen 49', 'The Air Post - Wolfen 50', 'The Air Post - Wolfen 51', 'The Air Post - Wolfen 52', 'The Air Post - Wolfen 53', 'The Air Post - Wolfen 54', 'The Air Post - Wolfen 55', 'The Air Post - Wolfen 56', 'The Air Post - Wolfen 57', 'The Air Post - Wolfen 58', 'The Air Post - Wolfen 59', 'The Air Post - Wolfen 60', 'The Air Post - Wolfen 61'),
    'The Fortress': ('The Fortress - Wolfen 01', 'The Fortress - Wolfen 02', 'The Fortress - Wolfen 03', 'The Fortress - Wolfen 05', 'The Fortress - Wolfen 06', 'The Fortress - Wolfen 07', 'The Fortress - Wolfen 08', 'The Fortress - Wolfen 09', 'The Fortress - Wolfen 10', 'The Fortress - Wolfen 11', 'The Fortress - Wolfen 12', 'The Fortress - Wolfen 13', 'The Fortress - Wolfen 14'),
    'The Quarry': ('The Quarry - Wolfen 01', 'The Quarry - Wolfen 02', 'The Quarry - Wolfen 03', 'The Quarry - Wolfen 04', 'The Quarry - Wolfen 05', 'The Quarry - Wolfen 06', 'The Quarry - Wolfen 07', 'The Quarry - Wolfen 08', 'The Quarry - Wolfen 09', 'The Quarry - Wolfen 10', 'The Quarry - Wolfen 11', 'The Quarry - Wolfen 12', 'The Quarry - Wolfen 13', 'The Quarry - Wolfen 14', 'The Quarry - Wolfen 15', 'The Quarry - Wolfen 16', 'The Quarry - Wolfen 17', 'The Quarry - Wolfen 18', 'The Quarry - Wolfen 19', 'The Quarry - Wolfen 20', 'The Quarry - Wolfen 21', 'The Quarry - Wolfen 22', 'The Quarry - Wolfen 23', 'The Quarry - Wolfen 24', 'The Quarry - Wolfen 25', 'The Quarry - Wolfen 26', 'The Quarry - Wolfen 27', 'The Quarry - Wolfen 28', 'The Quarry - Wolfen 29', 'The Quarry - Wolfen 30', 'The Quarry - Wolfen 31', 'The Quarry - Wolfen 32', 'The Quarry - Wolfen 33', 'The Quarry - Wolfen 34', 'The Quarry - Wolfen 35', 'The Quarry - Wolfen 36', 'The Quarry - Wolfen 37', 'The Quarry - Wolfen 38', 'The Quarry - Wolfen 39', 'The Quarry - Wolfen 40', 'The Quarry - Wolfen 41', 'The Quarry - Wolfen 42', 'The Quarry - Wolfen 43', 'The Quarry - Wolfen 44', 'The Quarry - Wolfen 45'),
    'Wolfen City': ('Wolfen City - Wolfen 02', 'Wolfen City - Wolfen 03', 'Wolfen City - Wolfen 04', 'Wolfen City - Wolfen 05', 'Wolfen City - Wolfen 06', 'Wolfen City - Wolfen 07', 'Wolfen City - Wolfen 08', 'Wolfen City - Wolfen 09', 'Wolfen City - Wolfen 10', 'Wolfen City - Wolfen 11', 'Wolfen City - Wolfen 12', 'Wolfen City - Wolfen 13', 'Wolfen City - Wolfen 14', 'Wolfen City - Wolfen 15', 'Wolfen City - Wolfen 16', 'Wolfen City - Wolfen 17', 'Wolfen City - Wolfen 18', 'Wolfen City - Wolfen 19', 'Wolfen City - Wolfen 20', 'Wolfen City - Wolfen 21', 'Wolfen City - Wolfen 22', 'Wolfen City - Wolfen 23', 'Wolfen City - Wolfen 24', 'Wolfen City - Wolfen 25', 'Wolfen City - Wolfen 26', 'Wolfen City - Wolfen 27', 'Wolfen City - Wolfen 28', 'Wolfen City - Wolfen 29', 'Wolfen City - Wolfen 30', 'Wolfen City - Wolfen 31', 'Wolfen City - Wolfen 32', 'Wolfen City - Wolfen 33', 'Wolfen City - Wolfen 34', 'Wolfen City - Wolfen 35', 'Wolfen City - Wolfen 36', 'Wolfen City - Wolfen 37', 'Wolfen City - Wolfen 38', 'Wolfen City - Wolfen 39', 'Wolfen City - Wolfen 40', 'Wolfen City - Wolfen 41'),
}

# Confirmed/retained causal checks: value becomes the expected value on acquisition.
SPECIAL_LOCATION_CONDITIONS = {
    'Flying Forest - Map Discovery': ((4346892, 2),),
    "The Root - Root's Rune": ((4347060, 2),),
    "Hunters Domain - Hunter's Domain's Rune": ((4347164, 2),),
    "The Quarry - Quarry's Rune": ((4347212, 2),),
    "The Air Post - Air Post's Rune": ((4347252, 2),),
    "Forgotten Island - Forgotten Island's Rune": ((4347284, 2),),
    "Flying Forest - Flying Forest's Rune": ((4347108, 2),),
    'Blue Egg - Obtained': ((4346860, 1),),
    'Receptacle - Obtained': ((4346956, 1),),
}

LOCATION_NAME_TO_ID = {
    'Hunters Domain - Wolfen 55': 51474312,
    'Hunters Domain - Wolfen 56': 51474330,
    'Hunters Domain - Wolfen 54': 51474331,
    'Hunters Domain - Wolfen 53': 51474336,
    'Hunters Domain - Wolfen 79': 51474418,
    'Hunters Domain - Wolfen 80': 51474420,
    'Hunters Domain - Wolfen 81': 51474430,
    'Wolfen City - Wolfen 06': 51474494,
    'Hunters Domain - Wolfen 95': 51474646,
    'Wolfen City - Wolfen 10': 51474752,
    'Wolfen City - Wolfen 40': 51474770,
    'Wolfen City - Wolfen 41': 51474771,
    'Wolfen City - Wolfen 12': 51474778,
    'Wolfen City - Wolfen 17': 51474807,
    'The Quarry - Wolfen 15': 51474823,
    'The Fortress - Wolfen 14': 51474895,
    'Hunters Domain - Wolfen 64': 51474917,
    'Nativs City - Wolfen 01': 51474984,
    'Hunters Domain - Wolfen 66': 51475010,
    'Hunters Domain - Wolfen 65': 51475034,
    'The Fortress - Wolfen 10': 51475121,
    'The Fortress - Wolfen 09': 51475122,
    'The Fortress - Wolfen 13': 51475124,
    'The Fortress - Wolfen 07': 51475125,
    'The Fortress - Wolfen 02': 51475126,
    'The Fortress - Wolfen 05': 51475128,
    'The Fortress - Wolfen 11': 51475129,
    'The Quarry - Wolfen 02': 51475130,
    'The Fortress - Wolfen 12': 51475131,
    'The Fortress - Wolfen 08': 51475132,
    'The Fortress - Wolfen 01': 51475133,
    'The Fortress - Wolfen 03': 51475134,
    'The Quarry - Wolfen 09': 51475142,
    'The Quarry - Wolfen 10': 51475143,
    'The Fortress - Wolfen 06': 51475147,
    'The Quarry - Wolfen 08': 51475162,
    'Wolfen City - Wolfen 37': 51475267,
    'Wolfen City - Wolfen 36': 51475268,
    'Wolfen City - Wolfen 39': 51475269,
    'Wolfen City - Wolfen 38': 51475270,
    'The Air Post - Wolfen 49': 51475327,
    'Hunters Domain - Wolfen 59': 51475357,
    'Wolfen City - Wolfen 11': 51475374,
    'Wolfen City - Wolfen 05': 51475422,
    'The Quarry - Wolfen 14': 51475429,
    'Wolfen City - Wolfen 03': 51475434,
    'The Quarry - Wolfen 18': 51475437,
    'Wolfen City - Wolfen 04': 51475443,
    'The Air Post - Wolfen 53': 51475449,
    'Hunters Domain - Wolfen 74': 51475518,
    'Wolfen City - Wolfen 15': 51475641,
    'Wolfen City - Wolfen 16': 51475652,
    'Wolfen City - Wolfen 19': 51475680,
    'Hunters Domain - Wolfen 46': 51475742,
    'Hunters Domain - Wolfen 45': 51475744,
    'Wolfen City - Wolfen 09': 51475750,
    'Wolfen City - Wolfen 22': 51475787,
    'Wolfen City - Wolfen 20': 51475822,
    'Wolfen City - Wolfen 31': 51475842,
    'Hunters Domain - Wolfen 48': 51475885,
    'The Air Post - Wolfen 45': 51475912,
    'Wolfen City - Wolfen 35': 51475989,
    'Wolfen City - Wolfen 33': 51475998,
    'Wolfen City - Wolfen 34': 51475999,
    'Wolfen City - Wolfen 32': 51476004,
    'Hunters Domain - Wolfen 49': 51476037,
    'Forgotten Island - Wolfen 01': 51476054,
    'Forgotten Island - Wolfen 02': 51476084,
    'Forgotten Island - Wolfen 03': 51476102,
    'Flying Forest - Wolfen 09': 51476260,
    'Flying Forest - Wolfen 10': 51476297,
    'Wolfen City - Wolfen 26': 51476333,
    'Wolfen City - Wolfen 30': 51476335,
    'Wolfen City - Wolfen 28': 51476337,
    'Wolfen City - Wolfen 29': 51476339,
    'Wolfen City - Wolfen 27': 51476341,
    'Flying Forest - Wolfen 03': 51476342,
    'Flying Forest - Wolfen 12': 51476351,
    'Flying Forest - Wolfen 17': 51476354,
    'Flying Forest - Wolfen 14': 51476398,
    'Flying Forest - Wolfen 24': 51476451,
    'Flying Forest - Wolfen 23': 51476453,
    'Flying Forest - Wolfen 20': 51476462,
    'The Quarry - Wolfen 24': 51476556,
    'Flying Forest - Wolfen 30': 51476614,
    'Flying Forest - Wolfen 37': 51476615,
    'Flying Forest - Wolfen 31': 51476616,
    'Flying Forest - Wolfen 36': 51476617,
    'Flying Forest - Wolfen 33': 51476618,
    'Flying Forest - Wolfen 34': 51476619,
    'Flying Forest - Wolfen 32': 51476620,
    'Flying Forest - Wolfen 29': 51476621,
    'Flying Forest - Wolfen 35': 51476622,
    'Flying Forest - Wolfen 19': 51476656,
    'Wolfen City - Wolfen 02': 51476688,
    'Flying Forest - Wolfen 25': 51476689,
    'Flying Forest - Wolfen 27': 51476726,
    'Flying Forest - Wolfen 26': 51476727,
    'Flying Forest - Wolfen 28': 51476828,
    'Flying Forest - Wolfen 22': 51477112,
    'Flying Forest - Wolfen 18': 51477210,
    'Flying Forest - Wolfen 11': 51477235,
    'Flying Forest - Wolfen 13': 51477237,
    'The Quarry - Wolfen 23': 51477267,
    'Flying Forest - Wolfen 16': 51477270,
    'Hunters Domain - Wolfen 39': 51477465,
    'Hunters Domain - Wolfen 37': 51477466,
    'Hunters Domain - Wolfen 38': 51477467,
    'Hunters Domain - Wolfen 36': 51477469,
    'Hunters Domain - Wolfen 50': 51477486,
    'Wolfen City - Wolfen 08': 51477677,
    'Wolfen City - Wolfen 07': 51477678,
    'Wolfen City - Wolfen 13': 51477687,
    'Wolfen City - Wolfen 21': 51477699,
    'Hunters Domain - Wolfen 52': 51477731,
    'Hunters Domain - Wolfen 51': 51477732,
    'Wolfen City - Wolfen 14': 51477733,
    'Wolfen City - Wolfen 18': 51477734,
    'Wolfen City - Wolfen 25': 51477761,
    'Wolfen City - Wolfen 23': 51477762,
    'Wolfen City - Wolfen 24': 51477791,
    'The Quarry - Wolfen 22': 51477868,
    'The Quarry - Wolfen 16': 51478232,
    'Hunters Domain - Wolfen 60': 51478432,
    'Hunters Domain - Wolfen 61': 51478433,
    'Hunters Domain - Wolfen 72': 51478621,
    'Hunters Domain - Wolfen 70': 51478622,
    'Hunters Domain - Wolfen 73': 51478624,
    'Hunters Domain - Wolfen 71': 51478627,
    'Flying Forest - Wolfen 15': 51478672,
    'Hunters Domain - Wolfen 94': 51478754,
    'Hunters Domain - Wolfen 91': 51478755,
    'Hunters Domain - Wolfen 89': 51478756,
    'Hunters Domain - Wolfen 90': 51478757,
    'Hunters Domain - Wolfen 92': 51478758,
    'Hunters Domain - Wolfen 93': 51478759,
    'Forgotten Island - Wolfen 07': 51478944,
    'Forgotten Island - Wolfen 04': 51479059,
    'Forgotten Island - Wolfen 05': 51479060,
    'Flying Forest - Wolfen 05': 51479272,
    'Flying Forest - Wolfen 07': 51479454,
    'Flying Forest - Wolfen 08': 51479455,
    'Flying Forest - Wolfen 06': 51479456,
    'The Quarry - Wolfen 03': 51479999,
    'The Quarry - Wolfen 04': 51480010,
    'The Quarry - Wolfen 19': 51480017,
    'The Quarry - Wolfen 28': 51480078,
    'The Quarry - Wolfen 30': 51480079,
    'The Quarry - Wolfen 31': 51480093,
    'The Quarry - Wolfen 29': 51480096,
    'Flying Forest - Wolfen 04': 51480134,
    'Forgotten Island - Wolfen 06': 51480215,
    'Hunters Domain - Wolfen 40': 51480320,
    'The Quarry - Wolfen 26': 51480526,
    'The Quarry - Wolfen 27': 51480527,
    'Forgotten Island - Wolfen 08': 51480811,
    'Flying Forest - Wolfen 21': 51481077,
    'The Air Post - Wolfen 47': 51481285,
    'Hunters Domain - Wolfen 76': 51481445,
    'The Quarry - Wolfen 38': 51481569,
    'Hunters Domain - Wolfen 96': 51481602,
    'Hunters Domain - Wolfen 87': 51481790,
    'Hunters Domain - Wolfen 85': 51481791,
    'Hunters Domain - Wolfen 84': 51481792,
    'Hunters Domain - Wolfen 86': 51481793,
    'Hunters Domain - Wolfen 88': 51481794,
    'Hunters Domain - Wolfen 83': 51481795,
    'Hunters Domain - Wolfen 47': 51482330,
    'The Air Post - Wolfen 46': 51482421,
    'Hunters Domain - Wolfen 42': 51482743,
    'The Air Post - Wolfen 50': 51482758,
    'Hunters Domain - Wolfen 43': 51483133,
    'The Air Post - Wolfen 58': 51483203,
    'The Air Post - Wolfen 59': 51483204,
    'The Quarry - Wolfen 25': 51483339,
    'The Quarry - Wolfen 20': 51483392,
    'The Quarry - Wolfen 21': 51483394,
    'Hunters Domain - Wolfen 82': 51483398,
    'The Quarry - Wolfen 07': 51483436,
    'The Quarry - Wolfen 06': 51483437,
    'The Quarry - Wolfen 05': 51483466,
    'The Quarry - Wolfen 39': 51483511,
    'The Quarry - Wolfen 42': 51483513,
    'The Quarry - Wolfen 40': 51483515,
    'The Quarry - Wolfen 43': 51483516,
    'The Quarry - Wolfen 41': 51483518,
    'The Quarry - Wolfen 44': 51483528,
    'The Quarry - Wolfen 45': 51483538,
    'The Air Post - Wolfen 61': 51483595,
    'The Air Post - Wolfen 43': 51483597,
    'The Air Post - Wolfen 41': 51483598,
    'The Air Post - Wolfen 42': 51483600,
    'The Quarry - Wolfen 11': 51483644,
    'The Quarry - Wolfen 13': 51483645,
    'The Quarry - Wolfen 12': 51483646,
    'The Quarry - Wolfen 17': 51483721,
    'Hunters Domain - Wolfen 78': 51483801,
    'Hunters Domain - Wolfen 77': 51483817,
    'The Quarry - Wolfen 37': 51483841,
    'The Quarry - Wolfen 34': 51483842,
    'The Quarry - Wolfen 33': 51483843,
    'The Quarry - Wolfen 32': 51483845,
    'Hunters Domain - Wolfen 75': 51483856,
    'Hunters Domain - Wolfen 57': 51483940,
    'Hunters Domain - Wolfen 58': 51483943,
    'The Air Post - Wolfen 48': 51483944,
    'The Air Post - Wolfen 55': 51483946,
    'The Air Post - Wolfen 56': 51483949,
    'The Air Post - Wolfen 57': 51483950,
    'The Quarry - Wolfen 35': 51483988,
    'The Quarry - Wolfen 36': 51483989,
    'The Air Post - Wolfen 54': 51484067,
    'The Air Post - Wolfen 52': 51484078,
    'The Air Post - Wolfen 51': 51484079,
    'Hunters Domain - Wolfen 26': 51484312,
    'Hunters Domain - Wolfen 27': 51484313,
    'Hunters Domain - Wolfen 32': 51484349,
    'The Air Post - Wolfen 60': 51484380,
    'Hunters Domain - Wolfen 62': 51484403,
    'Hunters Domain - Wolfen 33': 51484485,
    'The Quarry - Wolfen 01': 51484602,
    'Hunters Domain - Wolfen 44': 51484610,
    'The Air Post - Wolfen 44': 51484613,
    'Hunters Domain - Wolfen 29': 51484797,
    'Hunters Domain - Wolfen 28': 51484804,
    'Hunters Domain - Wolfen 41': 51484978,
    'Hunters Domain - Wolfen 67': 51485389,
    'Hunters Domain - Wolfen 63': 51485391,
    'Hunters Domain - Wolfen 69': 51485393,
    'Hunters Domain - Wolfen 35': 51485424,
    'Hunters Domain - Wolfen 31': 51485443,
    'Hunters Domain - Wolfen 30': 51485444,
    'Hunters Domain - Wolfen 34': 51485474,
    'Hunters Domain - Wolfen 68': 51485751,
    'Flying Forest - Map Discovery': 51539537,
    "The Root - Root's Rune": 51539538,
    "Hunters Domain - Hunter's Domain's Rune": 51539539,
    "The Quarry - Quarry's Rune": 51539540,
    "The Air Post - Air Post's Rune": 51539541,
    "Forgotten Island - Forgotten Island's Rune": 51539542,
    "Flying Forest - Flying Forest's Rune": 51539543,
    'Blue Egg - Obtained': 51539544,
    'Receptacle - Obtained': 51539545,
}

# Confirmed PAL addresses.
ADDR_BOOMY_TYPE = 0x0042541C
ADDR_MAGIC_GAUGE_LEVEL = 0x0042545C
ADDR_MAGIC_GAUGE_STEP = 0x00425464
ADDR_MAGIC_GAUGE_CAP = 0x0042546C
ADDR_MONEY = 0x0048EABC

# Official Actor Manager path.
ADDR_ACTOR_MANAGER_GLOBAL = 0x004516A4
ACTOR_MANAGER_ACTIVE_LIST_OFFSET = 0x54
ACTOR_MANAGER_ACTIVE_COUNT_OFFSET = 0x58
ACTOR_MANAGER_MAX_ACTIVE = 4096

WOLFEN_VTABLE = 0x0043C870
WOLFEN_STATE_OFFSET = 0xB80
WOLFEN_STATE_PRESENT = 1
WOLFEN_STATE_FREED = 2
WOLFEN_DESCRIPTOR_OFFSET = 0x1C
WOLFEN_KEY_OFFSET = 0x28

EXPECTED_DISC_SERIAL_NORMALIZED = "SLES51473"
PINE_HOST = "127.0.0.1"
PINE_PORT = 28011

# ============================================================================
# 0.7.1 ZONE-SAFE NORMAL-RUN PLAYTEST — 2026-10-04
# Supersedes old prototype mappings. Runtime checks are zone-scoped.
# ============================================================================
PROTOTYPE_VERSION = "0.7.1-zonesafe"

ITEM_PROGRESSIVE_BOOMY = "Progressive Boomy"
ITEM_PROGRESSIVE_BRACELET = "Progressive Bracelet"
ITEM_MAGIC_BOUNCERS = "Magic Bouncers"
ITEM_CLIMBING_GLOVES = "Climbing Gloves"
ITEM_JAMGUT = "Jamgut Birdcall"
ITEM_TELESCOPE = "Telescope"
ITEM_PROGRESSIVE_BOARD = "Progressive Board"
ITEM_PROGRESSIVE_MAGIC_GAUGE = "Progressive Magic Gauge"

ITEM_NAME_TO_ID.update({
    ITEM_PROGRESSIVE_BOOMY: ITEM_ID_BASE + 21,
    ITEM_PROGRESSIVE_BRACELET: ITEM_ID_BASE + 22,
    ITEM_MAGIC_BOUNCERS: ITEM_ID_BASE + 23,
    ITEM_CLIMBING_GLOVES: ITEM_ID_BASE + 24,
    ITEM_JAMGUT: ITEM_ID_BASE + 25,
    ITEM_TELESCOPE: ITEM_ID_BASE + 26,
    ITEM_PROGRESSIVE_BOARD: ITEM_ID_BASE + 27,
    ITEM_PROGRESSIVE_MAGIC_GAUGE: ITEM_ID_BASE + 28,
})

ITEM_RUNES = (
    "Progressive Rune: Root's Rune",
    "Progressive Rune: Hunter's Domain Rune",
    "Progressive Rune: Quarry's Rune",
    "Progressive Rune: Air Post Rune",
    "Progressive Rune: Forgotten Island Rune",
)
ITEM_RUNE_SCENARIO_VARS = {
    "Progressive Rune: Root's Rune": 0x004254B4,
    "Progressive Rune: Hunter's Domain Rune": 0x0042551C,
    "Progressive Rune: Quarry's Rune": 0x0042554C,
    "Progressive Rune: Air Post Rune": 0x00425574,
    "Progressive Rune: Forgotten Island Rune": 0x00425594,
}
ITEM_SCENARIO_FLAGS.update({
    ITEM_MAGIC_BOUNCERS: 0x0042540C,
    ITEM_CLIMBING_GLOVES: 0x00425414,
    ITEM_MAGIC_REGENERATION: 0x00425434,
    ITEM_JAMGUT: 0x0042543C,
    ITEM_TELESCOPE: 0x00425444,
})

ADDR_BRACELET_BITFIELD = 0x00425424
ADDR_BOARD_LEVEL = 0x00425454
ADDR_LIFE_GAUGE = 0x00425474
ADDR_PLAYER_POINTER = 0x006F3D90
PLAYER_HP_OFFSET = 0x2D8
PLAYER_MAX_HP_OFFSET = 0x2DC
PLAYER_MAGIC_OBJECT_OFFSET = 0xAB8
MAGIC_CURRENT_OFFSET = 0x14
MAGIC_MAX_OFFSET = 0x18

ITEM_PROGRESSION_COUNTS = {
    ITEM_PROGRESSIVE_BOOMY: 3,
    ITEM_PROGRESSIVE_BRACELET: 8,
    ITEM_MAGIC_BOUNCERS: 1,
    ITEM_CLIMBING_GLOVES: 1,
    ITEM_MAGIC_REGENERATION: 1,
    ITEM_JAMGUT: 1,
    ITEM_TELESCOPE: 1,
    ITEM_PROGRESSIVE_BOARD: 2,
    'Receptacle': 1,
    'Blue Egg': 1,
    **{name: 1 for name in ITEM_RUNES},
}
ITEM_REWARD_COUNTS = {
    ITEM_PROGRESSIVE_LIFE_GAUGE: 4,
    ITEM_PROGRESSIVE_MAGIC_GAUGE: 3,
    ITEM_HP_RESTORE: 30,
    ITEM_MAGIC_RESTORE: 30,
    ITEM_ATTACK_BONUS: 5,
    ITEM_PROTECTION_BONUS: 5,
}
ITEM_USEFUL = frozenset((
    ITEM_PROGRESSIVE_LIFE_GAUGE,
    ITEM_PROGRESSIVE_MAGIC_GAUGE,
    ITEM_ATTACK_BONUS,
    ITEM_PROTECTION_BONUS,
))

ZONE_ORDER = ('Nativs City', 'Flying Forest', 'Hunters Domain', 'Wind Tower', 'The Quarry', 'Amber Quarry', 'The Root', 'The Air Post', 'Forgotten Island', 'Wolfen City', 'The Fortress')
WOLFEN_ZONE_KEY_TO_LOCATION = {'Nativs City': {984: 'Nativs City - Wolfen 01'}, 'Flying Forest': {3210: 'Flying Forest - Wolfen 01', 2656: 'Flying Forest - Wolfen 02', 2462: 'Flying Forest - Wolfen 03', 7077: 'Flying Forest - Wolfen 04', 2451: 'Flying Forest - Wolfen 05', 2453: 'Flying Forest - Wolfen 06', 3112: 'Flying Forest - Wolfen 07', 2335: 'Flying Forest - Wolfen 08', 6134: 'Flying Forest - Wolfen 09', 5456: 'Flying Forest - Wolfen 10', 5454: 'Flying Forest - Wolfen 11', 3270: 'Flying Forest - Wolfen 12', 4672: 'Flying Forest - Wolfen 13', 5272: 'Flying Forest - Wolfen 14', 2689: 'Flying Forest - Wolfen 15', 2614: 'Flying Forest - Wolfen 16', 2618: 'Flying Forest - Wolfen 17', 2615: 'Flying Forest - Wolfen 18', 2617: 'Flying Forest - Wolfen 19', 2616: 'Flying Forest - Wolfen 20', 2727: 'Flying Forest - Wolfen 21', 2619: 'Flying Forest - Wolfen 22', 2620: 'Flying Forest - Wolfen 23', 2621: 'Flying Forest - Wolfen 24', 2622: 'Flying Forest - Wolfen 25', 2828: 'Flying Forest - Wolfen 26', 2688: 'Flying Forest - Wolfen 27', 2726: 'Flying Forest - Wolfen 28', 2260: 'Flying Forest - Wolfen 29', 5455: 'Flying Forest - Wolfen 30', 3237: 'Flying Forest - Wolfen 31', 3235: 'Flying Forest - Wolfen 32', 2297: 'Flying Forest - Wolfen 33', 2342: 'Flying Forest - Wolfen 34', 2351: 'Flying Forest - Wolfen 35', 2398: 'Flying Forest - Wolfen 36', 2354: 'Flying Forest - Wolfen 37'}, 'Hunters Domain': {3258: 'Hunters Domain - Wolfen 01', 3260: 'Hunters Domain - Wolfen 02', 3285: 'Hunters Domain - Wolfen 03', 2496: 'Hunters Domain - Wolfen 04', 3255: 'Hunters Domain - Wolfen 05', 3604: 'Hunters Domain - Wolfen 06', 2266: 'Hunters Domain - Wolfen 07', 3593: 'Hunters Domain - Wolfen 08', 3601: 'Hunters Domain - Wolfen 09', 10824: 'Hunters Domain - Wolfen 10', 3366: 'Hunters Domain - Wolfen 11', 3368: 'Hunters Domain - Wolfen 12', 3554: 'Hunters Domain - Wolfen 13', 3553: 'Hunters Domain - Wolfen 14', 3555: 'Hunters Domain - Wolfen 15', 8250: 'Hunters Domain - Wolfen 16', 10794: 'Hunters Domain - Wolfen 17', 10157: 'Hunters Domain - Wolfen 18', 11224: 'Hunters Domain - Wolfen 19', 8747: 'Hunters Domain - Wolfen 20', 3775: 'Hunters Domain - Wolfen 21', 3776: 'Hunters Domain - Wolfen 22', 3941: 'Hunters Domain - Wolfen 23', 3934: 'Hunters Domain - Wolfen 24', 3936: 'Hunters Domain - Wolfen 25', 10312: 'Hunters Domain - Wolfen 26', 10313: 'Hunters Domain - Wolfen 27', 10804: 'Hunters Domain - Wolfen 28', 10797: 'Hunters Domain - Wolfen 29', 11444: 'Hunters Domain - Wolfen 30', 11443: 'Hunters Domain - Wolfen 31', 10349: 'Hunters Domain - Wolfen 32', 10485: 'Hunters Domain - Wolfen 33', 11474: 'Hunters Domain - Wolfen 34', 11424: 'Hunters Domain - Wolfen 35', 3469: 'Hunters Domain - Wolfen 36', 3466: 'Hunters Domain - Wolfen 37', 3467: 'Hunters Domain - Wolfen 38', 3465: 'Hunters Domain - Wolfen 39', 6320: 'Hunters Domain - Wolfen 40', 10978: 'Hunters Domain - Wolfen 41', 8743: 'Hunters Domain - Wolfen 42', 9133: 'Hunters Domain - Wolfen 43', 10610: 'Hunters Domain - Wolfen 44', 1744: 'Hunters Domain - Wolfen 45', 1742: 'Hunters Domain - Wolfen 46'}, 'Wind Tower': {8330: 'Wind Tower - Wolfen 01', 1885: 'Wind Tower - Wolfen 02'}, 'The Quarry': {10602: 'The Quarry - Wolfen 01', 1130: 'The Quarry - Wolfen 02', 5999: 'The Quarry - Wolfen 03', 6010: 'The Quarry - Wolfen 04', 9466: 'The Quarry - Wolfen 05', 9437: 'The Quarry - Wolfen 06', 9436: 'The Quarry - Wolfen 07', 1162: 'The Quarry - Wolfen 08', 1142: 'The Quarry - Wolfen 09', 1143: 'The Quarry - Wolfen 10', 9644: 'The Quarry - Wolfen 11', 9646: 'The Quarry - Wolfen 12', 9645: 'The Quarry - Wolfen 13', 1429: 'The Quarry - Wolfen 14', 823: 'The Quarry - Wolfen 15', 4232: 'The Quarry - Wolfen 16', 9721: 'The Quarry - Wolfen 17', 1437: 'The Quarry - Wolfen 18', 6017: 'The Quarry - Wolfen 19', 9392: 'The Quarry - Wolfen 20', 9394: 'The Quarry - Wolfen 21', 3868: 'The Quarry - Wolfen 22', 3267: 'The Quarry - Wolfen 23', 2556: 'The Quarry - Wolfen 24', 9339: 'The Quarry - Wolfen 25', 6526: 'The Quarry - Wolfen 26', 6527: 'The Quarry - Wolfen 27', 6078: 'The Quarry - Wolfen 28', 6096: 'The Quarry - Wolfen 29', 6079: 'The Quarry - Wolfen 30', 6093: 'The Quarry - Wolfen 31'}, 'Amber Quarry': {9845: 'Amber Quarry - Wolfen 01', 9843: 'Amber Quarry - Wolfen 02', 9842: 'Amber Quarry - Wolfen 03', 9988: 'Amber Quarry - Wolfen 04', 9989: 'Amber Quarry - Wolfen 05', 9841: 'Amber Quarry - Wolfen 06', 7569: 'Amber Quarry - Wolfen 07', 9511: 'Amber Quarry - Wolfen 08', 9515: 'Amber Quarry - Wolfen 09', 9518: 'Amber Quarry - Wolfen 10', 9513: 'Amber Quarry - Wolfen 11', 9516: 'Amber Quarry - Wolfen 12', 9528: 'Amber Quarry - Wolfen 13', 9538: 'Amber Quarry - Wolfen 14'}, 'The Root': {3486: 'The Root - Wolfen 01', 3732: 'The Root - Wolfen 02', 3731: 'The Root - Wolfen 03', 336: 'The Root - Wolfen 04', 331: 'The Root - Wolfen 05', 312: 'The Root - Wolfen 06', 330: 'The Root - Wolfen 07'}, 'The Air Post': {9940: 'The Air Post - Wolfen 01', 9943: 'The Air Post - Wolfen 02', 1357: 'The Air Post - Wolfen 03', 4432: 'The Air Post - Wolfen 04', 4433: 'The Air Post - Wolfen 05', 10403: 'The Air Post - Wolfen 06', 11391: 'The Air Post - Wolfen 07', 917: 'The Air Post - Wolfen 08', 1034: 'The Air Post - Wolfen 09', 1010: 'The Air Post - Wolfen 10', 11389: 'The Air Post - Wolfen 11', 11751: 'The Air Post - Wolfen 12', 11393: 'The Air Post - Wolfen 13', 4622: 'The Air Post - Wolfen 14', 4627: 'The Air Post - Wolfen 15', 4621: 'The Air Post - Wolfen 16', 4624: 'The Air Post - Wolfen 17', 1518: 'The Air Post - Wolfen 18', 9856: 'The Air Post - Wolfen 19', 7445: 'The Air Post - Wolfen 20', 9817: 'The Air Post - Wolfen 21', 9801: 'The Air Post - Wolfen 22', 418: 'The Air Post - Wolfen 23', 420: 'The Air Post - Wolfen 24', 430: 'The Air Post - Wolfen 25', 9398: 'The Air Post - Wolfen 26', 7795: 'The Air Post - Wolfen 27', 7792: 'The Air Post - Wolfen 28', 7791: 'The Air Post - Wolfen 29', 7793: 'The Air Post - Wolfen 30', 7790: 'The Air Post - Wolfen 31', 7794: 'The Air Post - Wolfen 32', 4756: 'The Air Post - Wolfen 33', 4757: 'The Air Post - Wolfen 34', 4755: 'The Air Post - Wolfen 35', 4758: 'The Air Post - Wolfen 36', 4759: 'The Air Post - Wolfen 37', 4754: 'The Air Post - Wolfen 38', 646: 'The Air Post - Wolfen 39', 7602: 'The Air Post - Wolfen 40', 9598: 'The Air Post - Wolfen 41', 9600: 'The Air Post - Wolfen 42', 9597: 'The Air Post - Wolfen 43', 10613: 'The Air Post - Wolfen 44', 1912: 'The Air Post - Wolfen 45', 8421: 'The Air Post - Wolfen 46', 7285: 'The Air Post - Wolfen 47', 9944: 'The Air Post - Wolfen 48', 1327: 'The Air Post - Wolfen 49', 8758: 'The Air Post - Wolfen 50', 10079: 'The Air Post - Wolfen 51', 10078: 'The Air Post - Wolfen 52', 1449: 'The Air Post - Wolfen 53', 10067: 'The Air Post - Wolfen 54', 9946: 'The Air Post - Wolfen 55', 9949: 'The Air Post - Wolfen 56', 9950: 'The Air Post - Wolfen 57', 9203: 'The Air Post - Wolfen 58', 9204: 'The Air Post - Wolfen 59', 10380: 'The Air Post - Wolfen 60', 9595: 'The Air Post - Wolfen 61'}, 'Forgotten Island': {2054: 'Forgotten Island - Wolfen 01', 2084: 'Forgotten Island - Wolfen 02', 2102: 'Forgotten Island - Wolfen 03', 5059: 'Forgotten Island - Wolfen 04', 5060: 'Forgotten Island - Wolfen 05', 6215: 'Forgotten Island - Wolfen 06', 4944: 'Forgotten Island - Wolfen 07', 6811: 'Forgotten Island - Wolfen 08'}, 'Wolfen City': {2688: 'Wolfen City - Wolfen 01', 1434: 'Wolfen City - Wolfen 02', 1443: 'Wolfen City - Wolfen 03', 1422: 'Wolfen City - Wolfen 04', 494: 'Wolfen City - Wolfen 05', 3678: 'Wolfen City - Wolfen 06', 3677: 'Wolfen City - Wolfen 07', 1750: 'Wolfen City - Wolfen 08', 752: 'Wolfen City - Wolfen 09', 1374: 'Wolfen City - Wolfen 10', 778: 'Wolfen City - Wolfen 11', 3687: 'Wolfen City - Wolfen 12', 3733: 'Wolfen City - Wolfen 13', 1641: 'Wolfen City - Wolfen 14', 1652: 'Wolfen City - Wolfen 15', 807: 'Wolfen City - Wolfen 16', 3734: 'Wolfen City - Wolfen 17', 1680: 'Wolfen City - Wolfen 18', 1822: 'Wolfen City - Wolfen 19', 3699: 'Wolfen City - Wolfen 20', 1787: 'Wolfen City - Wolfen 21', 3762: 'Wolfen City - Wolfen 22', 3791: 'Wolfen City - Wolfen 23', 3761: 'Wolfen City - Wolfen 24', 2333: 'Wolfen City - Wolfen 25', 2341: 'Wolfen City - Wolfen 26', 2337: 'Wolfen City - Wolfen 27', 2339: 'Wolfen City - Wolfen 28', 2335: 'Wolfen City - Wolfen 29', 1842: 'Wolfen City - Wolfen 30', 2004: 'Wolfen City - Wolfen 31', 1998: 'Wolfen City - Wolfen 32', 1999: 'Wolfen City - Wolfen 33', 1989: 'Wolfen City - Wolfen 34', 1268: 'Wolfen City - Wolfen 35', 1267: 'Wolfen City - Wolfen 36', 1270: 'Wolfen City - Wolfen 37', 1269: 'Wolfen City - Wolfen 38', 770: 'Wolfen City - Wolfen 39', 771: 'Wolfen City - Wolfen 40'}, 'The Fortress': {1133: 'The Fortress - Wolfen 01', 1126: 'The Fortress - Wolfen 02', 1134: 'The Fortress - Wolfen 03', 1128: 'The Fortress - Wolfen 04', 1147: 'The Fortress - Wolfen 05', 1125: 'The Fortress - Wolfen 06', 1132: 'The Fortress - Wolfen 07', 1122: 'The Fortress - Wolfen 08', 1121: 'The Fortress - Wolfen 09', 1129: 'The Fortress - Wolfen 10', 1131: 'The Fortress - Wolfen 11', 1124: 'The Fortress - Wolfen 12', 895: 'The Fortress - Wolfen 13'}}
WOLFEN_LOCATIONS_BY_ZONE = {'Nativs City': ('Nativs City - Wolfen 01',), 'Flying Forest': ('Flying Forest - Wolfen 01', 'Flying Forest - Wolfen 02', 'Flying Forest - Wolfen 03', 'Flying Forest - Wolfen 04', 'Flying Forest - Wolfen 05', 'Flying Forest - Wolfen 06', 'Flying Forest - Wolfen 07', 'Flying Forest - Wolfen 08', 'Flying Forest - Wolfen 09', 'Flying Forest - Wolfen 10', 'Flying Forest - Wolfen 11', 'Flying Forest - Wolfen 12', 'Flying Forest - Wolfen 13', 'Flying Forest - Wolfen 14', 'Flying Forest - Wolfen 15', 'Flying Forest - Wolfen 16', 'Flying Forest - Wolfen 17', 'Flying Forest - Wolfen 18', 'Flying Forest - Wolfen 19', 'Flying Forest - Wolfen 20', 'Flying Forest - Wolfen 21', 'Flying Forest - Wolfen 22', 'Flying Forest - Wolfen 23', 'Flying Forest - Wolfen 24', 'Flying Forest - Wolfen 25', 'Flying Forest - Wolfen 26', 'Flying Forest - Wolfen 27', 'Flying Forest - Wolfen 28', 'Flying Forest - Wolfen 29', 'Flying Forest - Wolfen 30', 'Flying Forest - Wolfen 31', 'Flying Forest - Wolfen 32', 'Flying Forest - Wolfen 33', 'Flying Forest - Wolfen 34', 'Flying Forest - Wolfen 35', 'Flying Forest - Wolfen 36', 'Flying Forest - Wolfen 37'), 'Hunters Domain': ('Hunters Domain - Wolfen 01', 'Hunters Domain - Wolfen 02', 'Hunters Domain - Wolfen 03', 'Hunters Domain - Wolfen 04', 'Hunters Domain - Wolfen 05', 'Hunters Domain - Wolfen 06', 'Hunters Domain - Wolfen 07', 'Hunters Domain - Wolfen 08', 'Hunters Domain - Wolfen 09', 'Hunters Domain - Wolfen 10', 'Hunters Domain - Wolfen 11', 'Hunters Domain - Wolfen 12', 'Hunters Domain - Wolfen 13', 'Hunters Domain - Wolfen 14', 'Hunters Domain - Wolfen 15', 'Hunters Domain - Wolfen 16', 'Hunters Domain - Wolfen 17', 'Hunters Domain - Wolfen 18', 'Hunters Domain - Wolfen 19', 'Hunters Domain - Wolfen 20', 'Hunters Domain - Wolfen 21', 'Hunters Domain - Wolfen 22', 'Hunters Domain - Wolfen 23', 'Hunters Domain - Wolfen 24', 'Hunters Domain - Wolfen 25', 'Hunters Domain - Wolfen 26', 'Hunters Domain - Wolfen 27', 'Hunters Domain - Wolfen 28', 'Hunters Domain - Wolfen 29', 'Hunters Domain - Wolfen 30', 'Hunters Domain - Wolfen 31', 'Hunters Domain - Wolfen 32', 'Hunters Domain - Wolfen 33', 'Hunters Domain - Wolfen 34', 'Hunters Domain - Wolfen 35', 'Hunters Domain - Wolfen 36', 'Hunters Domain - Wolfen 37', 'Hunters Domain - Wolfen 38', 'Hunters Domain - Wolfen 39', 'Hunters Domain - Wolfen 40', 'Hunters Domain - Wolfen 41', 'Hunters Domain - Wolfen 42', 'Hunters Domain - Wolfen 43', 'Hunters Domain - Wolfen 44', 'Hunters Domain - Wolfen 45', 'Hunters Domain - Wolfen 46'), 'Wind Tower': ('Wind Tower - Wolfen 01', 'Wind Tower - Wolfen 02'), 'The Quarry': ('The Quarry - Wolfen 01', 'The Quarry - Wolfen 02', 'The Quarry - Wolfen 03', 'The Quarry - Wolfen 04', 'The Quarry - Wolfen 05', 'The Quarry - Wolfen 06', 'The Quarry - Wolfen 07', 'The Quarry - Wolfen 08', 'The Quarry - Wolfen 09', 'The Quarry - Wolfen 10', 'The Quarry - Wolfen 11', 'The Quarry - Wolfen 12', 'The Quarry - Wolfen 13', 'The Quarry - Wolfen 14', 'The Quarry - Wolfen 15', 'The Quarry - Wolfen 16', 'The Quarry - Wolfen 17', 'The Quarry - Wolfen 18', 'The Quarry - Wolfen 19', 'The Quarry - Wolfen 20', 'The Quarry - Wolfen 21', 'The Quarry - Wolfen 22', 'The Quarry - Wolfen 23', 'The Quarry - Wolfen 24', 'The Quarry - Wolfen 25', 'The Quarry - Wolfen 26', 'The Quarry - Wolfen 27', 'The Quarry - Wolfen 28', 'The Quarry - Wolfen 29', 'The Quarry - Wolfen 30', 'The Quarry - Wolfen 31'), 'Amber Quarry': ('Amber Quarry - Wolfen 01', 'Amber Quarry - Wolfen 02', 'Amber Quarry - Wolfen 03', 'Amber Quarry - Wolfen 04', 'Amber Quarry - Wolfen 05', 'Amber Quarry - Wolfen 06', 'Amber Quarry - Wolfen 07', 'Amber Quarry - Wolfen 08', 'Amber Quarry - Wolfen 09', 'Amber Quarry - Wolfen 10', 'Amber Quarry - Wolfen 11', 'Amber Quarry - Wolfen 12', 'Amber Quarry - Wolfen 13', 'Amber Quarry - Wolfen 14'), 'The Root': ('The Root - Wolfen 01', 'The Root - Wolfen 02', 'The Root - Wolfen 03', 'The Root - Wolfen 04', 'The Root - Wolfen 05', 'The Root - Wolfen 06', 'The Root - Wolfen 07'), 'The Air Post': ('The Air Post - Wolfen 01', 'The Air Post - Wolfen 02', 'The Air Post - Wolfen 03', 'The Air Post - Wolfen 04', 'The Air Post - Wolfen 05', 'The Air Post - Wolfen 06', 'The Air Post - Wolfen 07', 'The Air Post - Wolfen 08', 'The Air Post - Wolfen 09', 'The Air Post - Wolfen 10', 'The Air Post - Wolfen 11', 'The Air Post - Wolfen 12', 'The Air Post - Wolfen 13', 'The Air Post - Wolfen 14', 'The Air Post - Wolfen 15', 'The Air Post - Wolfen 16', 'The Air Post - Wolfen 17', 'The Air Post - Wolfen 18', 'The Air Post - Wolfen 19', 'The Air Post - Wolfen 20', 'The Air Post - Wolfen 21', 'The Air Post - Wolfen 22', 'The Air Post - Wolfen 23', 'The Air Post - Wolfen 24', 'The Air Post - Wolfen 25', 'The Air Post - Wolfen 26', 'The Air Post - Wolfen 27', 'The Air Post - Wolfen 28', 'The Air Post - Wolfen 29', 'The Air Post - Wolfen 30', 'The Air Post - Wolfen 31', 'The Air Post - Wolfen 32', 'The Air Post - Wolfen 33', 'The Air Post - Wolfen 34', 'The Air Post - Wolfen 35', 'The Air Post - Wolfen 36', 'The Air Post - Wolfen 37', 'The Air Post - Wolfen 38', 'The Air Post - Wolfen 39', 'The Air Post - Wolfen 40', 'The Air Post - Wolfen 41', 'The Air Post - Wolfen 42', 'The Air Post - Wolfen 43', 'The Air Post - Wolfen 44', 'The Air Post - Wolfen 45', 'The Air Post - Wolfen 46', 'The Air Post - Wolfen 47', 'The Air Post - Wolfen 48', 'The Air Post - Wolfen 49', 'The Air Post - Wolfen 50', 'The Air Post - Wolfen 51', 'The Air Post - Wolfen 52', 'The Air Post - Wolfen 53', 'The Air Post - Wolfen 54', 'The Air Post - Wolfen 55', 'The Air Post - Wolfen 56', 'The Air Post - Wolfen 57', 'The Air Post - Wolfen 58', 'The Air Post - Wolfen 59', 'The Air Post - Wolfen 60', 'The Air Post - Wolfen 61'), 'Forgotten Island': ('Forgotten Island - Wolfen 01', 'Forgotten Island - Wolfen 02', 'Forgotten Island - Wolfen 03', 'Forgotten Island - Wolfen 04', 'Forgotten Island - Wolfen 05', 'Forgotten Island - Wolfen 06', 'Forgotten Island - Wolfen 07', 'Forgotten Island - Wolfen 08'), 'Wolfen City': ('Wolfen City - Wolfen 01', 'Wolfen City - Wolfen 02', 'Wolfen City - Wolfen 03', 'Wolfen City - Wolfen 04', 'Wolfen City - Wolfen 05', 'Wolfen City - Wolfen 06', 'Wolfen City - Wolfen 07', 'Wolfen City - Wolfen 08', 'Wolfen City - Wolfen 09', 'Wolfen City - Wolfen 10', 'Wolfen City - Wolfen 11', 'Wolfen City - Wolfen 12', 'Wolfen City - Wolfen 13', 'Wolfen City - Wolfen 14', 'Wolfen City - Wolfen 15', 'Wolfen City - Wolfen 16', 'Wolfen City - Wolfen 17', 'Wolfen City - Wolfen 18', 'Wolfen City - Wolfen 19', 'Wolfen City - Wolfen 20', 'Wolfen City - Wolfen 21', 'Wolfen City - Wolfen 22', 'Wolfen City - Wolfen 23', 'Wolfen City - Wolfen 24', 'Wolfen City - Wolfen 25', 'Wolfen City - Wolfen 26', 'Wolfen City - Wolfen 27', 'Wolfen City - Wolfen 28', 'Wolfen City - Wolfen 29', 'Wolfen City - Wolfen 30', 'Wolfen City - Wolfen 31', 'Wolfen City - Wolfen 32', 'Wolfen City - Wolfen 33', 'Wolfen City - Wolfen 34', 'Wolfen City - Wolfen 35', 'Wolfen City - Wolfen 36', 'Wolfen City - Wolfen 37', 'Wolfen City - Wolfen 38', 'Wolfen City - Wolfen 39', 'Wolfen City - Wolfen 40'), 'The Fortress': ('The Fortress - Wolfen 01', 'The Fortress - Wolfen 02', 'The Fortress - Wolfen 03', 'The Fortress - Wolfen 04', 'The Fortress - Wolfen 05', 'The Fortress - Wolfen 06', 'The Fortress - Wolfen 07', 'The Fortress - Wolfen 08', 'The Fortress - Wolfen 09', 'The Fortress - Wolfen 10', 'The Fortress - Wolfen 11', 'The Fortress - Wolfen 12', 'The Fortress - Wolfen 13')}
WOLFEN_KEY_TO_ZONES = {984: ['Nativs City'], 3210: ['Flying Forest'], 2656: ['Flying Forest'], 2462: ['Flying Forest'], 7077: ['Flying Forest'], 2451: ['Flying Forest'], 2453: ['Flying Forest'], 3112: ['Flying Forest'], 2335: ['Flying Forest', 'Wolfen City'], 6134: ['Flying Forest'], 5456: ['Flying Forest'], 5454: ['Flying Forest'], 3270: ['Flying Forest'], 4672: ['Flying Forest'], 5272: ['Flying Forest'], 2689: ['Flying Forest'], 2614: ['Flying Forest'], 2618: ['Flying Forest'], 2615: ['Flying Forest'], 2617: ['Flying Forest'], 2616: ['Flying Forest'], 2727: ['Flying Forest'], 2619: ['Flying Forest'], 2620: ['Flying Forest'], 2621: ['Flying Forest'], 2622: ['Flying Forest'], 2828: ['Flying Forest'], 2688: ['Flying Forest', 'Wolfen City'], 2726: ['Flying Forest'], 2260: ['Flying Forest'], 5455: ['Flying Forest'], 3237: ['Flying Forest'], 3235: ['Flying Forest'], 2297: ['Flying Forest'], 2342: ['Flying Forest'], 2351: ['Flying Forest'], 2398: ['Flying Forest'], 2354: ['Flying Forest'], 3258: ['Hunters Domain'], 3260: ['Hunters Domain'], 3285: ['Hunters Domain'], 2496: ['Hunters Domain'], 3255: ['Hunters Domain'], 3604: ['Hunters Domain'], 2266: ['Hunters Domain'], 3593: ['Hunters Domain'], 3601: ['Hunters Domain'], 10824: ['Hunters Domain'], 3366: ['Hunters Domain'], 3368: ['Hunters Domain'], 3554: ['Hunters Domain'], 3553: ['Hunters Domain'], 3555: ['Hunters Domain'], 8250: ['Hunters Domain'], 10794: ['Hunters Domain'], 10157: ['Hunters Domain'], 11224: ['Hunters Domain'], 8747: ['Hunters Domain'], 3775: ['Hunters Domain'], 3776: ['Hunters Domain'], 3941: ['Hunters Domain'], 3934: ['Hunters Domain'], 3936: ['Hunters Domain'], 10312: ['Hunters Domain'], 10313: ['Hunters Domain'], 10804: ['Hunters Domain'], 10797: ['Hunters Domain'], 11444: ['Hunters Domain'], 11443: ['Hunters Domain'], 10349: ['Hunters Domain'], 10485: ['Hunters Domain'], 11474: ['Hunters Domain'], 11424: ['Hunters Domain'], 3469: ['Hunters Domain'], 3466: ['Hunters Domain'], 3467: ['Hunters Domain'], 3465: ['Hunters Domain'], 6320: ['Hunters Domain'], 10978: ['Hunters Domain'], 8743: ['Hunters Domain'], 9133: ['Hunters Domain'], 10610: ['Hunters Domain'], 1744: ['Hunters Domain'], 1742: ['Hunters Domain'], 8330: ['Wind Tower'], 1885: ['Wind Tower'], 10602: ['The Quarry'], 1130: ['The Quarry'], 5999: ['The Quarry'], 6010: ['The Quarry'], 9466: ['The Quarry'], 9437: ['The Quarry'], 9436: ['The Quarry'], 1162: ['The Quarry'], 1142: ['The Quarry'], 1143: ['The Quarry'], 9644: ['The Quarry'], 9646: ['The Quarry'], 9645: ['The Quarry'], 1429: ['The Quarry'], 823: ['The Quarry'], 4232: ['The Quarry'], 9721: ['The Quarry'], 1437: ['The Quarry'], 6017: ['The Quarry'], 9392: ['The Quarry'], 9394: ['The Quarry'], 3868: ['The Quarry'], 3267: ['The Quarry'], 2556: ['The Quarry'], 9339: ['The Quarry'], 6526: ['The Quarry'], 6527: ['The Quarry'], 6078: ['The Quarry'], 6096: ['The Quarry'], 6079: ['The Quarry'], 6093: ['The Quarry'], 9845: ['Amber Quarry'], 9843: ['Amber Quarry'], 9842: ['Amber Quarry'], 9988: ['Amber Quarry'], 9989: ['Amber Quarry'], 9841: ['Amber Quarry'], 7569: ['Amber Quarry'], 9511: ['Amber Quarry'], 9515: ['Amber Quarry'], 9518: ['Amber Quarry'], 9513: ['Amber Quarry'], 9516: ['Amber Quarry'], 9528: ['Amber Quarry'], 9538: ['Amber Quarry'], 3486: ['The Root'], 3732: ['The Root'], 3731: ['The Root'], 336: ['The Root'], 331: ['The Root'], 312: ['The Root'], 330: ['The Root'], 9940: ['The Air Post'], 9943: ['The Air Post'], 1357: ['The Air Post'], 4432: ['The Air Post'], 4433: ['The Air Post'], 10403: ['The Air Post'], 11391: ['The Air Post'], 917: ['The Air Post'], 1034: ['The Air Post'], 1010: ['The Air Post'], 11389: ['The Air Post'], 11751: ['The Air Post'], 11393: ['The Air Post'], 4622: ['The Air Post'], 4627: ['The Air Post'], 4621: ['The Air Post'], 4624: ['The Air Post'], 1518: ['The Air Post'], 9856: ['The Air Post'], 7445: ['The Air Post'], 9817: ['The Air Post'], 9801: ['The Air Post'], 418: ['The Air Post'], 420: ['The Air Post'], 430: ['The Air Post'], 9398: ['The Air Post'], 7795: ['The Air Post'], 7792: ['The Air Post'], 7791: ['The Air Post'], 7793: ['The Air Post'], 7790: ['The Air Post'], 7794: ['The Air Post'], 4756: ['The Air Post'], 4757: ['The Air Post'], 4755: ['The Air Post'], 4758: ['The Air Post'], 4759: ['The Air Post'], 4754: ['The Air Post'], 646: ['The Air Post'], 7602: ['The Air Post'], 9598: ['The Air Post'], 9600: ['The Air Post'], 9597: ['The Air Post'], 10613: ['The Air Post'], 1912: ['The Air Post'], 8421: ['The Air Post'], 7285: ['The Air Post'], 9944: ['The Air Post'], 1327: ['The Air Post'], 8758: ['The Air Post'], 10079: ['The Air Post'], 10078: ['The Air Post'], 1449: ['The Air Post'], 10067: ['The Air Post'], 9946: ['The Air Post'], 9949: ['The Air Post'], 9950: ['The Air Post'], 9203: ['The Air Post'], 9204: ['The Air Post'], 10380: ['The Air Post'], 9595: ['The Air Post'], 2054: ['Forgotten Island'], 2084: ['Forgotten Island'], 2102: ['Forgotten Island'], 5059: ['Forgotten Island'], 5060: ['Forgotten Island'], 6215: ['Forgotten Island'], 4944: ['Forgotten Island'], 6811: ['Forgotten Island'], 1434: ['Wolfen City'], 1443: ['Wolfen City'], 1422: ['Wolfen City'], 494: ['Wolfen City'], 3678: ['Wolfen City'], 3677: ['Wolfen City'], 1750: ['Wolfen City'], 752: ['Wolfen City'], 1374: ['Wolfen City'], 778: ['Wolfen City'], 3687: ['Wolfen City'], 3733: ['Wolfen City'], 1641: ['Wolfen City'], 1652: ['Wolfen City'], 807: ['Wolfen City'], 3734: ['Wolfen City'], 1680: ['Wolfen City'], 1822: ['Wolfen City'], 3699: ['Wolfen City'], 1787: ['Wolfen City'], 3762: ['Wolfen City'], 3791: ['Wolfen City'], 3761: ['Wolfen City'], 2333: ['Wolfen City'], 2341: ['Wolfen City'], 2337: ['Wolfen City'], 2339: ['Wolfen City'], 1842: ['Wolfen City'], 2004: ['Wolfen City'], 1998: ['Wolfen City'], 1999: ['Wolfen City'], 1989: ['Wolfen City'], 1268: ['Wolfen City'], 1267: ['Wolfen City'], 1270: ['Wolfen City'], 1269: ['Wolfen City'], 770: ['Wolfen City'], 771: ['Wolfen City'], 1133: ['The Fortress'], 1126: ['The Fortress'], 1134: ['The Fortress'], 1128: ['The Fortress'], 1147: ['The Fortress'], 1125: ['The Fortress'], 1132: ['The Fortress'], 1122: ['The Fortress'], 1121: ['The Fortress'], 1129: ['The Fortress'], 1131: ['The Fortress'], 1124: ['The Fortress'], 895: ['The Fortress']}
# Legacy convenience table only. Runtime detection MUST use the zone-aware table above.
WOLFEN_KEY_TO_LOCATION = {key: locations[0] for key, locations in (
    (key, [WOLFEN_ZONE_KEY_TO_LOCATION[z][key] for z in WOLFEN_KEY_TO_ZONES[key]])
    for key in WOLFEN_KEY_TO_ZONES
)}

SPECIAL_LOCATION_CONDITIONS = {'Flying Forest - Map Discovery': ((4347564, 2),), "The Root - Root's Rune": ((4347060, 2),), "Hunters Domain - Hunter's Domain's Rune": ((4347164, 2),), "The Quarry - Quarry's Rune": ((4347212, 2),), "The Air Post - Air Post's Rune": ((4347252, 2),), "Forgotten Island - Forgotten Island's Rune": ((4347284, 2),), 'Hunters Domain - Boss Defeated': ((4347116, 2),), 'The Root - Map Discovery': ((4347556, 2),), 'The Quarry - Map Discovery': ((4347580, 2),), 'The Air Post - Map Discovery': ((4347588, 2),), 'Wolfen City - Map Discovery': ((4347604, 2),), 'Amber Quarry - Brazul First Encounter': ((4347180, 2),), 'The Fortress - Brazul Final Defeated': ((4347324, 2),)}
SPECIAL_LOCATION_ZONES = {'Flying Forest - Map Discovery': 'Flying Forest', "The Root - Root's Rune": 'The Root', "Hunters Domain - Hunter's Domain's Rune": 'Hunters Domain', "The Quarry - Quarry's Rune": 'The Quarry', "The Air Post - Air Post's Rune": 'The Air Post', "Forgotten Island - Forgotten Island's Rune": 'Forgotten Island', 'Hunters Domain - Boss Defeated': 'Hunters Domain', 'The Root - Map Discovery': 'The Root', 'The Quarry - Map Discovery': 'The Quarry', 'The Air Post - Map Discovery': 'The Air Post', 'Wolfen City - Map Discovery': 'Wolfen City', 'Amber Quarry - Brazul First Encounter': 'Amber Quarry', 'The Fortress - Brazul Final Defeated': 'The Fortress'}
SHOP_LOCATION_CONDITIONS = {'Nativs City - Shop - Basic Boomy': (7317488, 8), 'Nativs City - Shop - Yellow Bracelet': (7324888, 16), 'Nativs City - Shop - Telescope': (7324888, 2), 'Nativs City - Shop - Magic Board': (7324888, 4), 'Nativs City - Shop - Green Bracelet': (7324944, 2), 'Nativs City - Shop - Climbing Gloves': (7324944, 8), 'Nativs City - Shop - Extra Energy Bar 1': (7324904, 4), 'Nativs City - Shop - Blue Bracelet': (7324904, 1), 'Nativs City - Shop - Jamgut Birdcall': (7324904, 2), 'Nativs City - Shop - Speed Board': (7324912, 1), 'Nativs City - Shop - Golden Boomy': (7324896, 16), 'Nativs City - Shop - Silver Bracelet': (7324896, 8), 'Nativs City - Shop - Silver Boomy': (7324920, 8), 'Nativs City - Shop - Brown Bracelet': (7324920, 4), 'Nativs City - Shop - Magic Bouncers': (7324920, 16), 'Nativs City - Shop - Extra Energy Bar 2': (7324928, 4), 'Nativs City - Shop - Black Bracelet': (7324912, 8), 'Nativs City - Shop - Gold Bracelet': (7324928, 8)}
SHOP_LOCATION_ZONES = {'Nativs City - Shop - Basic Boomy': 'Nativs City', 'Nativs City - Shop - Yellow Bracelet': 'Nativs City', 'Nativs City - Shop - Telescope': 'Nativs City', 'Nativs City - Shop - Magic Board': 'Nativs City', 'Nativs City - Shop - Green Bracelet': 'Nativs City', 'Nativs City - Shop - Climbing Gloves': 'Nativs City', 'Nativs City - Shop - Extra Energy Bar 1': 'Nativs City', 'Nativs City - Shop - Blue Bracelet': 'Nativs City', 'Nativs City - Shop - Jamgut Birdcall': 'Nativs City', 'Nativs City - Shop - Speed Board': 'Nativs City', 'Nativs City - Shop - Golden Boomy': 'Nativs City', 'Nativs City - Shop - Silver Bracelet': 'Nativs City', 'Nativs City - Shop - Silver Boomy': 'Nativs City', 'Nativs City - Shop - Brown Bracelet': 'Nativs City', 'Nativs City - Shop - Magic Bouncers': 'Nativs City', 'Nativs City - Shop - Extra Energy Bar 2': 'Nativs City', 'Nativs City - Shop - Black Bracelet': 'Nativs City', 'Nativs City - Shop - Gold Bracelet': 'Nativs City'}

LOCATION_NAME_TO_ID = {'Nativs City - Wolfen 01': 51474001, 'Flying Forest - Wolfen 01': 51474002, 'Flying Forest - Wolfen 02': 51474003, 'Flying Forest - Wolfen 03': 51474004, 'Flying Forest - Wolfen 04': 51474005, 'Flying Forest - Wolfen 05': 51474006, 'Flying Forest - Wolfen 06': 51474007, 'Flying Forest - Wolfen 07': 51474008, 'Flying Forest - Wolfen 08': 51474009, 'Flying Forest - Wolfen 09': 51474010, 'Flying Forest - Wolfen 10': 51474011, 'Flying Forest - Wolfen 11': 51474012, 'Flying Forest - Wolfen 12': 51474013, 'Flying Forest - Wolfen 13': 51474014, 'Flying Forest - Wolfen 14': 51474015, 'Flying Forest - Wolfen 15': 51474016, 'Flying Forest - Wolfen 16': 51474017, 'Flying Forest - Wolfen 17': 51474018, 'Flying Forest - Wolfen 18': 51474019, 'Flying Forest - Wolfen 19': 51474020, 'Flying Forest - Wolfen 20': 51474021, 'Flying Forest - Wolfen 21': 51474022, 'Flying Forest - Wolfen 22': 51474023, 'Flying Forest - Wolfen 23': 51474024, 'Flying Forest - Wolfen 24': 51474025, 'Flying Forest - Wolfen 25': 51474026, 'Flying Forest - Wolfen 26': 51474027, 'Flying Forest - Wolfen 27': 51474028, 'Flying Forest - Wolfen 28': 51474029, 'Flying Forest - Wolfen 29': 51474030, 'Flying Forest - Wolfen 30': 51474031, 'Flying Forest - Wolfen 31': 51474032, 'Flying Forest - Wolfen 32': 51474033, 'Flying Forest - Wolfen 33': 51474034, 'Flying Forest - Wolfen 34': 51474035, 'Flying Forest - Wolfen 35': 51474036, 'Flying Forest - Wolfen 36': 51474037, 'Flying Forest - Wolfen 37': 51474038, 'Hunters Domain - Wolfen 01': 51474039, 'Hunters Domain - Wolfen 02': 51474040, 'Hunters Domain - Wolfen 03': 51474041, 'Hunters Domain - Wolfen 04': 51474042, 'Hunters Domain - Wolfen 05': 51474043, 'Hunters Domain - Wolfen 06': 51474044, 'Hunters Domain - Wolfen 07': 51474045, 'Hunters Domain - Wolfen 08': 51474046, 'Hunters Domain - Wolfen 09': 51474047, 'Hunters Domain - Wolfen 10': 51474048, 'Hunters Domain - Wolfen 11': 51474049, 'Hunters Domain - Wolfen 12': 51474050, 'Hunters Domain - Wolfen 13': 51474051, 'Hunters Domain - Wolfen 14': 51474052, 'Hunters Domain - Wolfen 15': 51474053, 'Hunters Domain - Wolfen 16': 51474054, 'Hunters Domain - Wolfen 17': 51474055, 'Hunters Domain - Wolfen 18': 51474056, 'Hunters Domain - Wolfen 19': 51474057, 'Hunters Domain - Wolfen 20': 51474058, 'Hunters Domain - Wolfen 21': 51474059, 'Hunters Domain - Wolfen 22': 51474060, 'Hunters Domain - Wolfen 23': 51474061, 'Hunters Domain - Wolfen 24': 51474062, 'Hunters Domain - Wolfen 25': 51474063, 'Hunters Domain - Wolfen 26': 51474064, 'Hunters Domain - Wolfen 27': 51474065, 'Hunters Domain - Wolfen 28': 51474066, 'Hunters Domain - Wolfen 29': 51474067, 'Hunters Domain - Wolfen 30': 51474068, 'Hunters Domain - Wolfen 31': 51474069, 'Hunters Domain - Wolfen 32': 51474070, 'Hunters Domain - Wolfen 33': 51474071, 'Hunters Domain - Wolfen 34': 51474072, 'Hunters Domain - Wolfen 35': 51474073, 'Hunters Domain - Wolfen 36': 51474074, 'Hunters Domain - Wolfen 37': 51474075, 'Hunters Domain - Wolfen 38': 51474076, 'Hunters Domain - Wolfen 39': 51474077, 'Hunters Domain - Wolfen 40': 51474078, 'Hunters Domain - Wolfen 41': 51474079, 'Hunters Domain - Wolfen 42': 51474080, 'Hunters Domain - Wolfen 43': 51474081, 'Hunters Domain - Wolfen 44': 51474082, 'Hunters Domain - Wolfen 45': 51474083, 'Hunters Domain - Wolfen 46': 51474084, 'Wind Tower - Wolfen 01': 51474085, 'Wind Tower - Wolfen 02': 51474086, 'The Quarry - Wolfen 01': 51474087, 'The Quarry - Wolfen 02': 51474088, 'The Quarry - Wolfen 03': 51474089, 'The Quarry - Wolfen 04': 51474090, 'The Quarry - Wolfen 05': 51474091, 'The Quarry - Wolfen 06': 51474092, 'The Quarry - Wolfen 07': 51474093, 'The Quarry - Wolfen 08': 51474094, 'The Quarry - Wolfen 09': 51474095, 'The Quarry - Wolfen 10': 51474096, 'The Quarry - Wolfen 11': 51474097, 'The Quarry - Wolfen 12': 51474098, 'The Quarry - Wolfen 13': 51474099, 'The Quarry - Wolfen 14': 51474100, 'The Quarry - Wolfen 15': 51474101, 'The Quarry - Wolfen 16': 51474102, 'The Quarry - Wolfen 17': 51474103, 'The Quarry - Wolfen 18': 51474104, 'The Quarry - Wolfen 19': 51474105, 'The Quarry - Wolfen 20': 51474106, 'The Quarry - Wolfen 21': 51474107, 'The Quarry - Wolfen 22': 51474108, 'The Quarry - Wolfen 23': 51474109, 'The Quarry - Wolfen 24': 51474110, 'The Quarry - Wolfen 25': 51474111, 'The Quarry - Wolfen 26': 51474112, 'The Quarry - Wolfen 27': 51474113, 'The Quarry - Wolfen 28': 51474114, 'The Quarry - Wolfen 29': 51474115, 'The Quarry - Wolfen 30': 51474116, 'The Quarry - Wolfen 31': 51474117, 'Amber Quarry - Wolfen 01': 51474118, 'Amber Quarry - Wolfen 02': 51474119, 'Amber Quarry - Wolfen 03': 51474120, 'Amber Quarry - Wolfen 04': 51474121, 'Amber Quarry - Wolfen 05': 51474122, 'Amber Quarry - Wolfen 06': 51474123, 'Amber Quarry - Wolfen 07': 51474124, 'Amber Quarry - Wolfen 08': 51474125, 'Amber Quarry - Wolfen 09': 51474126, 'Amber Quarry - Wolfen 10': 51474127, 'Amber Quarry - Wolfen 11': 51474128, 'Amber Quarry - Wolfen 12': 51474129, 'Amber Quarry - Wolfen 13': 51474130, 'Amber Quarry - Wolfen 14': 51474131, 'The Root - Wolfen 01': 51474132, 'The Root - Wolfen 02': 51474133, 'The Root - Wolfen 03': 51474134, 'The Root - Wolfen 04': 51474135, 'The Root - Wolfen 05': 51474136, 'The Root - Wolfen 06': 51474137, 'The Root - Wolfen 07': 51474138, 'The Air Post - Wolfen 01': 51474139, 'The Air Post - Wolfen 02': 51474140, 'The Air Post - Wolfen 03': 51474141, 'The Air Post - Wolfen 04': 51474142, 'The Air Post - Wolfen 05': 51474143, 'The Air Post - Wolfen 06': 51474144, 'The Air Post - Wolfen 07': 51474145, 'The Air Post - Wolfen 08': 51474146, 'The Air Post - Wolfen 09': 51474147, 'The Air Post - Wolfen 10': 51474148, 'The Air Post - Wolfen 11': 51474149, 'The Air Post - Wolfen 12': 51474150, 'The Air Post - Wolfen 13': 51474151, 'The Air Post - Wolfen 14': 51474152, 'The Air Post - Wolfen 15': 51474153, 'The Air Post - Wolfen 16': 51474154, 'The Air Post - Wolfen 17': 51474155, 'The Air Post - Wolfen 18': 51474156, 'The Air Post - Wolfen 19': 51474157, 'The Air Post - Wolfen 20': 51474158, 'The Air Post - Wolfen 21': 51474159, 'The Air Post - Wolfen 22': 51474160, 'The Air Post - Wolfen 23': 51474161, 'The Air Post - Wolfen 24': 51474162, 'The Air Post - Wolfen 25': 51474163, 'The Air Post - Wolfen 26': 51474164, 'The Air Post - Wolfen 27': 51474165, 'The Air Post - Wolfen 28': 51474166, 'The Air Post - Wolfen 29': 51474167, 'The Air Post - Wolfen 30': 51474168, 'The Air Post - Wolfen 31': 51474169, 'The Air Post - Wolfen 32': 51474170, 'The Air Post - Wolfen 33': 51474171, 'The Air Post - Wolfen 34': 51474172, 'The Air Post - Wolfen 35': 51474173, 'The Air Post - Wolfen 36': 51474174, 'The Air Post - Wolfen 37': 51474175, 'The Air Post - Wolfen 38': 51474176, 'The Air Post - Wolfen 39': 51474177, 'The Air Post - Wolfen 40': 51474178, 'The Air Post - Wolfen 41': 51474179, 'The Air Post - Wolfen 42': 51474180, 'The Air Post - Wolfen 43': 51474181, 'The Air Post - Wolfen 44': 51474182, 'The Air Post - Wolfen 45': 51474183, 'The Air Post - Wolfen 46': 51474184, 'The Air Post - Wolfen 47': 51474185, 'The Air Post - Wolfen 48': 51474186, 'The Air Post - Wolfen 49': 51474187, 'The Air Post - Wolfen 50': 51474188, 'The Air Post - Wolfen 51': 51474189, 'The Air Post - Wolfen 52': 51474190, 'The Air Post - Wolfen 53': 51474191, 'The Air Post - Wolfen 54': 51474192, 'The Air Post - Wolfen 55': 51474193, 'The Air Post - Wolfen 56': 51474194, 'The Air Post - Wolfen 57': 51474195, 'The Air Post - Wolfen 58': 51474196, 'The Air Post - Wolfen 59': 51474197, 'The Air Post - Wolfen 60': 51474198, 'The Air Post - Wolfen 61': 51474199, 'Forgotten Island - Wolfen 01': 51474200, 'Forgotten Island - Wolfen 02': 51474201, 'Forgotten Island - Wolfen 03': 51474202, 'Forgotten Island - Wolfen 04': 51474203, 'Forgotten Island - Wolfen 05': 51474204, 'Forgotten Island - Wolfen 06': 51474205, 'Forgotten Island - Wolfen 07': 51474206, 'Forgotten Island - Wolfen 08': 51474207, 'Wolfen City - Wolfen 01': 51474208, 'Wolfen City - Wolfen 02': 51474209, 'Wolfen City - Wolfen 03': 51474210, 'Wolfen City - Wolfen 04': 51474211, 'Wolfen City - Wolfen 05': 51474212, 'Wolfen City - Wolfen 06': 51474213, 'Wolfen City - Wolfen 07': 51474214, 'Wolfen City - Wolfen 08': 51474215, 'Wolfen City - Wolfen 09': 51474216, 'Wolfen City - Wolfen 10': 51474217, 'Wolfen City - Wolfen 11': 51474218, 'Wolfen City - Wolfen 12': 51474219, 'Wolfen City - Wolfen 13': 51474220, 'Wolfen City - Wolfen 14': 51474221, 'Wolfen City - Wolfen 15': 51474222, 'Wolfen City - Wolfen 16': 51474223, 'Wolfen City - Wolfen 17': 51474224, 'Wolfen City - Wolfen 18': 51474225, 'Wolfen City - Wolfen 19': 51474226, 'Wolfen City - Wolfen 20': 51474227, 'Wolfen City - Wolfen 21': 51474228, 'Wolfen City - Wolfen 22': 51474229, 'Wolfen City - Wolfen 23': 51474230, 'Wolfen City - Wolfen 24': 51474231, 'Wolfen City - Wolfen 25': 51474232, 'Wolfen City - Wolfen 26': 51474233, 'Wolfen City - Wolfen 27': 51474234, 'Wolfen City - Wolfen 28': 51474235, 'Wolfen City - Wolfen 29': 51474236, 'Wolfen City - Wolfen 30': 51474237, 'Wolfen City - Wolfen 31': 51474238, 'Wolfen City - Wolfen 32': 51474239, 'Wolfen City - Wolfen 33': 51474240, 'Wolfen City - Wolfen 34': 51474241, 'Wolfen City - Wolfen 35': 51474242, 'Wolfen City - Wolfen 36': 51474243, 'Wolfen City - Wolfen 37': 51474244, 'Wolfen City - Wolfen 38': 51474245, 'Wolfen City - Wolfen 39': 51474246, 'Wolfen City - Wolfen 40': 51474247, 'The Fortress - Wolfen 01': 51474248, 'The Fortress - Wolfen 02': 51474249, 'The Fortress - Wolfen 03': 51474250, 'The Fortress - Wolfen 04': 51474251, 'The Fortress - Wolfen 05': 51474252, 'The Fortress - Wolfen 06': 51474253, 'The Fortress - Wolfen 07': 51474254, 'The Fortress - Wolfen 08': 51474255, 'The Fortress - Wolfen 09': 51474256, 'The Fortress - Wolfen 10': 51474257, 'The Fortress - Wolfen 11': 51474258, 'The Fortress - Wolfen 12': 51474259, 'The Fortress - Wolfen 13': 51474260, 'Flying Forest - Map Discovery': 51474261, "The Root - Root's Rune": 51474262, "Hunters Domain - Hunter's Domain's Rune": 51474263, "The Quarry - Quarry's Rune": 51474264, "The Air Post - Air Post's Rune": 51474265, "Forgotten Island - Forgotten Island's Rune": 51474266, 'Hunters Domain - Boss Defeated': 51474267, 'The Root - Map Discovery': 51474268, 'The Quarry - Map Discovery': 51474269, 'The Air Post - Map Discovery': 51474270, 'Wolfen City - Map Discovery': 51474271, 'Amber Quarry - Brazul First Encounter': 51474272, 'The Fortress - Brazul Final Defeated': 51474273, 'Nativs City - Shop - Basic Boomy': 51474274, 'Nativs City - Shop - Yellow Bracelet': 51474275, 'Nativs City - Shop - Telescope': 51474276, 'Nativs City - Shop - Magic Board': 51474277, 'Nativs City - Shop - Green Bracelet': 51474278, 'Nativs City - Shop - Climbing Gloves': 51474279, 'Nativs City - Shop - Extra Energy Bar 1': 51474280, 'Nativs City - Shop - Blue Bracelet': 51474281, 'Nativs City - Shop - Jamgut Birdcall': 51474282, 'Nativs City - Shop - Speed Board': 51474283, 'Nativs City - Shop - Golden Boomy': 51474284, 'Nativs City - Shop - Silver Bracelet': 51474285, 'Nativs City - Shop - Silver Boomy': 51474286, 'Nativs City - Shop - Brown Bracelet': 51474287, 'Nativs City - Shop - Magic Bouncers': 51474288, 'Nativs City - Shop - Extra Energy Bar 2': 51474289, 'Nativs City - Shop - Black Bracelet': 51474290, 'Nativs City - Shop - Gold Bracelet': 51474291}
LOCATION_NAME_TO_ZONE = {'Nativs City - Wolfen 01': 'Nativs City', 'Flying Forest - Wolfen 01': 'Flying Forest', 'Flying Forest - Wolfen 02': 'Flying Forest', 'Flying Forest - Wolfen 03': 'Flying Forest', 'Flying Forest - Wolfen 04': 'Flying Forest', 'Flying Forest - Wolfen 05': 'Flying Forest', 'Flying Forest - Wolfen 06': 'Flying Forest', 'Flying Forest - Wolfen 07': 'Flying Forest', 'Flying Forest - Wolfen 08': 'Flying Forest', 'Flying Forest - Wolfen 09': 'Flying Forest', 'Flying Forest - Wolfen 10': 'Flying Forest', 'Flying Forest - Wolfen 11': 'Flying Forest', 'Flying Forest - Wolfen 12': 'Flying Forest', 'Flying Forest - Wolfen 13': 'Flying Forest', 'Flying Forest - Wolfen 14': 'Flying Forest', 'Flying Forest - Wolfen 15': 'Flying Forest', 'Flying Forest - Wolfen 16': 'Flying Forest', 'Flying Forest - Wolfen 17': 'Flying Forest', 'Flying Forest - Wolfen 18': 'Flying Forest', 'Flying Forest - Wolfen 19': 'Flying Forest', 'Flying Forest - Wolfen 20': 'Flying Forest', 'Flying Forest - Wolfen 21': 'Flying Forest', 'Flying Forest - Wolfen 22': 'Flying Forest', 'Flying Forest - Wolfen 23': 'Flying Forest', 'Flying Forest - Wolfen 24': 'Flying Forest', 'Flying Forest - Wolfen 25': 'Flying Forest', 'Flying Forest - Wolfen 26': 'Flying Forest', 'Flying Forest - Wolfen 27': 'Flying Forest', 'Flying Forest - Wolfen 28': 'Flying Forest', 'Flying Forest - Wolfen 29': 'Flying Forest', 'Flying Forest - Wolfen 30': 'Flying Forest', 'Flying Forest - Wolfen 31': 'Flying Forest', 'Flying Forest - Wolfen 32': 'Flying Forest', 'Flying Forest - Wolfen 33': 'Flying Forest', 'Flying Forest - Wolfen 34': 'Flying Forest', 'Flying Forest - Wolfen 35': 'Flying Forest', 'Flying Forest - Wolfen 36': 'Flying Forest', 'Flying Forest - Wolfen 37': 'Flying Forest', 'Hunters Domain - Wolfen 01': 'Hunters Domain', 'Hunters Domain - Wolfen 02': 'Hunters Domain', 'Hunters Domain - Wolfen 03': 'Hunters Domain', 'Hunters Domain - Wolfen 04': 'Hunters Domain', 'Hunters Domain - Wolfen 05': 'Hunters Domain', 'Hunters Domain - Wolfen 06': 'Hunters Domain', 'Hunters Domain - Wolfen 07': 'Hunters Domain', 'Hunters Domain - Wolfen 08': 'Hunters Domain', 'Hunters Domain - Wolfen 09': 'Hunters Domain', 'Hunters Domain - Wolfen 10': 'Hunters Domain', 'Hunters Domain - Wolfen 11': 'Hunters Domain', 'Hunters Domain - Wolfen 12': 'Hunters Domain', 'Hunters Domain - Wolfen 13': 'Hunters Domain', 'Hunters Domain - Wolfen 14': 'Hunters Domain', 'Hunters Domain - Wolfen 15': 'Hunters Domain', 'Hunters Domain - Wolfen 16': 'Hunters Domain', 'Hunters Domain - Wolfen 17': 'Hunters Domain', 'Hunters Domain - Wolfen 18': 'Hunters Domain', 'Hunters Domain - Wolfen 19': 'Hunters Domain', 'Hunters Domain - Wolfen 20': 'Hunters Domain', 'Hunters Domain - Wolfen 21': 'Hunters Domain', 'Hunters Domain - Wolfen 22': 'Hunters Domain', 'Hunters Domain - Wolfen 23': 'Hunters Domain', 'Hunters Domain - Wolfen 24': 'Hunters Domain', 'Hunters Domain - Wolfen 25': 'Hunters Domain', 'Hunters Domain - Wolfen 26': 'Hunters Domain', 'Hunters Domain - Wolfen 27': 'Hunters Domain', 'Hunters Domain - Wolfen 28': 'Hunters Domain', 'Hunters Domain - Wolfen 29': 'Hunters Domain', 'Hunters Domain - Wolfen 30': 'Hunters Domain', 'Hunters Domain - Wolfen 31': 'Hunters Domain', 'Hunters Domain - Wolfen 32': 'Hunters Domain', 'Hunters Domain - Wolfen 33': 'Hunters Domain', 'Hunters Domain - Wolfen 34': 'Hunters Domain', 'Hunters Domain - Wolfen 35': 'Hunters Domain', 'Hunters Domain - Wolfen 36': 'Hunters Domain', 'Hunters Domain - Wolfen 37': 'Hunters Domain', 'Hunters Domain - Wolfen 38': 'Hunters Domain', 'Hunters Domain - Wolfen 39': 'Hunters Domain', 'Hunters Domain - Wolfen 40': 'Hunters Domain', 'Hunters Domain - Wolfen 41': 'Hunters Domain', 'Hunters Domain - Wolfen 42': 'Hunters Domain', 'Hunters Domain - Wolfen 43': 'Hunters Domain', 'Hunters Domain - Wolfen 44': 'Hunters Domain', 'Hunters Domain - Wolfen 45': 'Hunters Domain', 'Hunters Domain - Wolfen 46': 'Hunters Domain', 'Wind Tower - Wolfen 01': 'Wind Tower', 'Wind Tower - Wolfen 02': 'Wind Tower', 'The Quarry - Wolfen 01': 'The Quarry', 'The Quarry - Wolfen 02': 'The Quarry', 'The Quarry - Wolfen 03': 'The Quarry', 'The Quarry - Wolfen 04': 'The Quarry', 'The Quarry - Wolfen 05': 'The Quarry', 'The Quarry - Wolfen 06': 'The Quarry', 'The Quarry - Wolfen 07': 'The Quarry', 'The Quarry - Wolfen 08': 'The Quarry', 'The Quarry - Wolfen 09': 'The Quarry', 'The Quarry - Wolfen 10': 'The Quarry', 'The Quarry - Wolfen 11': 'The Quarry', 'The Quarry - Wolfen 12': 'The Quarry', 'The Quarry - Wolfen 13': 'The Quarry', 'The Quarry - Wolfen 14': 'The Quarry', 'The Quarry - Wolfen 15': 'The Quarry', 'The Quarry - Wolfen 16': 'The Quarry', 'The Quarry - Wolfen 17': 'The Quarry', 'The Quarry - Wolfen 18': 'The Quarry', 'The Quarry - Wolfen 19': 'The Quarry', 'The Quarry - Wolfen 20': 'The Quarry', 'The Quarry - Wolfen 21': 'The Quarry', 'The Quarry - Wolfen 22': 'The Quarry', 'The Quarry - Wolfen 23': 'The Quarry', 'The Quarry - Wolfen 24': 'The Quarry', 'The Quarry - Wolfen 25': 'The Quarry', 'The Quarry - Wolfen 26': 'The Quarry', 'The Quarry - Wolfen 27': 'The Quarry', 'The Quarry - Wolfen 28': 'The Quarry', 'The Quarry - Wolfen 29': 'The Quarry', 'The Quarry - Wolfen 30': 'The Quarry', 'The Quarry - Wolfen 31': 'The Quarry', 'Amber Quarry - Wolfen 01': 'Amber Quarry', 'Amber Quarry - Wolfen 02': 'Amber Quarry', 'Amber Quarry - Wolfen 03': 'Amber Quarry', 'Amber Quarry - Wolfen 04': 'Amber Quarry', 'Amber Quarry - Wolfen 05': 'Amber Quarry', 'Amber Quarry - Wolfen 06': 'Amber Quarry', 'Amber Quarry - Wolfen 07': 'Amber Quarry', 'Amber Quarry - Wolfen 08': 'Amber Quarry', 'Amber Quarry - Wolfen 09': 'Amber Quarry', 'Amber Quarry - Wolfen 10': 'Amber Quarry', 'Amber Quarry - Wolfen 11': 'Amber Quarry', 'Amber Quarry - Wolfen 12': 'Amber Quarry', 'Amber Quarry - Wolfen 13': 'Amber Quarry', 'Amber Quarry - Wolfen 14': 'Amber Quarry', 'The Root - Wolfen 01': 'The Root', 'The Root - Wolfen 02': 'The Root', 'The Root - Wolfen 03': 'The Root', 'The Root - Wolfen 04': 'The Root', 'The Root - Wolfen 05': 'The Root', 'The Root - Wolfen 06': 'The Root', 'The Root - Wolfen 07': 'The Root', 'The Air Post - Wolfen 01': 'The Air Post', 'The Air Post - Wolfen 02': 'The Air Post', 'The Air Post - Wolfen 03': 'The Air Post', 'The Air Post - Wolfen 04': 'The Air Post', 'The Air Post - Wolfen 05': 'The Air Post', 'The Air Post - Wolfen 06': 'The Air Post', 'The Air Post - Wolfen 07': 'The Air Post', 'The Air Post - Wolfen 08': 'The Air Post', 'The Air Post - Wolfen 09': 'The Air Post', 'The Air Post - Wolfen 10': 'The Air Post', 'The Air Post - Wolfen 11': 'The Air Post', 'The Air Post - Wolfen 12': 'The Air Post', 'The Air Post - Wolfen 13': 'The Air Post', 'The Air Post - Wolfen 14': 'The Air Post', 'The Air Post - Wolfen 15': 'The Air Post', 'The Air Post - Wolfen 16': 'The Air Post', 'The Air Post - Wolfen 17': 'The Air Post', 'The Air Post - Wolfen 18': 'The Air Post', 'The Air Post - Wolfen 19': 'The Air Post', 'The Air Post - Wolfen 20': 'The Air Post', 'The Air Post - Wolfen 21': 'The Air Post', 'The Air Post - Wolfen 22': 'The Air Post', 'The Air Post - Wolfen 23': 'The Air Post', 'The Air Post - Wolfen 24': 'The Air Post', 'The Air Post - Wolfen 25': 'The Air Post', 'The Air Post - Wolfen 26': 'The Air Post', 'The Air Post - Wolfen 27': 'The Air Post', 'The Air Post - Wolfen 28': 'The Air Post', 'The Air Post - Wolfen 29': 'The Air Post', 'The Air Post - Wolfen 30': 'The Air Post', 'The Air Post - Wolfen 31': 'The Air Post', 'The Air Post - Wolfen 32': 'The Air Post', 'The Air Post - Wolfen 33': 'The Air Post', 'The Air Post - Wolfen 34': 'The Air Post', 'The Air Post - Wolfen 35': 'The Air Post', 'The Air Post - Wolfen 36': 'The Air Post', 'The Air Post - Wolfen 37': 'The Air Post', 'The Air Post - Wolfen 38': 'The Air Post', 'The Air Post - Wolfen 39': 'The Air Post', 'The Air Post - Wolfen 40': 'The Air Post', 'The Air Post - Wolfen 41': 'The Air Post', 'The Air Post - Wolfen 42': 'The Air Post', 'The Air Post - Wolfen 43': 'The Air Post', 'The Air Post - Wolfen 44': 'The Air Post', 'The Air Post - Wolfen 45': 'The Air Post', 'The Air Post - Wolfen 46': 'The Air Post', 'The Air Post - Wolfen 47': 'The Air Post', 'The Air Post - Wolfen 48': 'The Air Post', 'The Air Post - Wolfen 49': 'The Air Post', 'The Air Post - Wolfen 50': 'The Air Post', 'The Air Post - Wolfen 51': 'The Air Post', 'The Air Post - Wolfen 52': 'The Air Post', 'The Air Post - Wolfen 53': 'The Air Post', 'The Air Post - Wolfen 54': 'The Air Post', 'The Air Post - Wolfen 55': 'The Air Post', 'The Air Post - Wolfen 56': 'The Air Post', 'The Air Post - Wolfen 57': 'The Air Post', 'The Air Post - Wolfen 58': 'The Air Post', 'The Air Post - Wolfen 59': 'The Air Post', 'The Air Post - Wolfen 60': 'The Air Post', 'The Air Post - Wolfen 61': 'The Air Post', 'Forgotten Island - Wolfen 01': 'Forgotten Island', 'Forgotten Island - Wolfen 02': 'Forgotten Island', 'Forgotten Island - Wolfen 03': 'Forgotten Island', 'Forgotten Island - Wolfen 04': 'Forgotten Island', 'Forgotten Island - Wolfen 05': 'Forgotten Island', 'Forgotten Island - Wolfen 06': 'Forgotten Island', 'Forgotten Island - Wolfen 07': 'Forgotten Island', 'Forgotten Island - Wolfen 08': 'Forgotten Island', 'Wolfen City - Wolfen 01': 'Wolfen City', 'Wolfen City - Wolfen 02': 'Wolfen City', 'Wolfen City - Wolfen 03': 'Wolfen City', 'Wolfen City - Wolfen 04': 'Wolfen City', 'Wolfen City - Wolfen 05': 'Wolfen City', 'Wolfen City - Wolfen 06': 'Wolfen City', 'Wolfen City - Wolfen 07': 'Wolfen City', 'Wolfen City - Wolfen 08': 'Wolfen City', 'Wolfen City - Wolfen 09': 'Wolfen City', 'Wolfen City - Wolfen 10': 'Wolfen City', 'Wolfen City - Wolfen 11': 'Wolfen City', 'Wolfen City - Wolfen 12': 'Wolfen City', 'Wolfen City - Wolfen 13': 'Wolfen City', 'Wolfen City - Wolfen 14': 'Wolfen City', 'Wolfen City - Wolfen 15': 'Wolfen City', 'Wolfen City - Wolfen 16': 'Wolfen City', 'Wolfen City - Wolfen 17': 'Wolfen City', 'Wolfen City - Wolfen 18': 'Wolfen City', 'Wolfen City - Wolfen 19': 'Wolfen City', 'Wolfen City - Wolfen 20': 'Wolfen City', 'Wolfen City - Wolfen 21': 'Wolfen City', 'Wolfen City - Wolfen 22': 'Wolfen City', 'Wolfen City - Wolfen 23': 'Wolfen City', 'Wolfen City - Wolfen 24': 'Wolfen City', 'Wolfen City - Wolfen 25': 'Wolfen City', 'Wolfen City - Wolfen 26': 'Wolfen City', 'Wolfen City - Wolfen 27': 'Wolfen City', 'Wolfen City - Wolfen 28': 'Wolfen City', 'Wolfen City - Wolfen 29': 'Wolfen City', 'Wolfen City - Wolfen 30': 'Wolfen City', 'Wolfen City - Wolfen 31': 'Wolfen City', 'Wolfen City - Wolfen 32': 'Wolfen City', 'Wolfen City - Wolfen 33': 'Wolfen City', 'Wolfen City - Wolfen 34': 'Wolfen City', 'Wolfen City - Wolfen 35': 'Wolfen City', 'Wolfen City - Wolfen 36': 'Wolfen City', 'Wolfen City - Wolfen 37': 'Wolfen City', 'Wolfen City - Wolfen 38': 'Wolfen City', 'Wolfen City - Wolfen 39': 'Wolfen City', 'Wolfen City - Wolfen 40': 'Wolfen City', 'The Fortress - Wolfen 01': 'The Fortress', 'The Fortress - Wolfen 02': 'The Fortress', 'The Fortress - Wolfen 03': 'The Fortress', 'The Fortress - Wolfen 04': 'The Fortress', 'The Fortress - Wolfen 05': 'The Fortress', 'The Fortress - Wolfen 06': 'The Fortress', 'The Fortress - Wolfen 07': 'The Fortress', 'The Fortress - Wolfen 08': 'The Fortress', 'The Fortress - Wolfen 09': 'The Fortress', 'The Fortress - Wolfen 10': 'The Fortress', 'The Fortress - Wolfen 11': 'The Fortress', 'The Fortress - Wolfen 12': 'The Fortress', 'The Fortress - Wolfen 13': 'The Fortress', 'Flying Forest - Map Discovery': 'Flying Forest', "The Root - Root's Rune": 'The Root', "Hunters Domain - Hunter's Domain's Rune": 'Hunters Domain', "The Quarry - Quarry's Rune": 'The Quarry', "The Air Post - Air Post's Rune": 'The Air Post', "Forgotten Island - Forgotten Island's Rune": 'Forgotten Island', 'Hunters Domain - Boss Defeated': 'Hunters Domain', 'The Root - Map Discovery': 'The Root', 'The Quarry - Map Discovery': 'The Quarry', 'The Air Post - Map Discovery': 'The Air Post', 'Wolfen City - Map Discovery': 'Wolfen City', 'Amber Quarry - Brazul First Encounter': 'Amber Quarry', 'The Fortress - Brazul Final Defeated': 'The Fortress', 'Nativs City - Shop - Basic Boomy': 'Nativs City', 'Nativs City - Shop - Yellow Bracelet': 'Nativs City', 'Nativs City - Shop - Telescope': 'Nativs City', 'Nativs City - Shop - Magic Board': 'Nativs City', 'Nativs City - Shop - Green Bracelet': 'Nativs City', 'Nativs City - Shop - Climbing Gloves': 'Nativs City', 'Nativs City - Shop - Extra Energy Bar 1': 'Nativs City', 'Nativs City - Shop - Blue Bracelet': 'Nativs City', 'Nativs City - Shop - Jamgut Birdcall': 'Nativs City', 'Nativs City - Shop - Speed Board': 'Nativs City', 'Nativs City - Shop - Golden Boomy': 'Nativs City', 'Nativs City - Shop - Silver Bracelet': 'Nativs City', 'Nativs City - Shop - Silver Boomy': 'Nativs City', 'Nativs City - Shop - Brown Bracelet': 'Nativs City', 'Nativs City - Shop - Magic Bouncers': 'Nativs City', 'Nativs City - Shop - Extra Energy Bar 2': 'Nativs City', 'Nativs City - Shop - Black Bracelet': 'Nativs City', 'Nativs City - Shop - Gold Bracelet': 'Nativs City'}
LOCATION_NAMES_BY_ZONE = {'Nativs City': ('Nativs City - Wolfen 01', 'Nativs City - Shop - Basic Boomy', 'Nativs City - Shop - Yellow Bracelet', 'Nativs City - Shop - Telescope', 'Nativs City - Shop - Magic Board', 'Nativs City - Shop - Green Bracelet', 'Nativs City - Shop - Climbing Gloves', 'Nativs City - Shop - Extra Energy Bar 1', 'Nativs City - Shop - Blue Bracelet', 'Nativs City - Shop - Jamgut Birdcall', 'Nativs City - Shop - Speed Board', 'Nativs City - Shop - Golden Boomy', 'Nativs City - Shop - Silver Bracelet', 'Nativs City - Shop - Silver Boomy', 'Nativs City - Shop - Brown Bracelet', 'Nativs City - Shop - Magic Bouncers', 'Nativs City - Shop - Extra Energy Bar 2', 'Nativs City - Shop - Black Bracelet', 'Nativs City - Shop - Gold Bracelet'), 'Flying Forest': ('Flying Forest - Wolfen 01', 'Flying Forest - Wolfen 02', 'Flying Forest - Wolfen 03', 'Flying Forest - Wolfen 04', 'Flying Forest - Wolfen 05', 'Flying Forest - Wolfen 06', 'Flying Forest - Wolfen 07', 'Flying Forest - Wolfen 08', 'Flying Forest - Wolfen 09', 'Flying Forest - Wolfen 10', 'Flying Forest - Wolfen 11', 'Flying Forest - Wolfen 12', 'Flying Forest - Wolfen 13', 'Flying Forest - Wolfen 14', 'Flying Forest - Wolfen 15', 'Flying Forest - Wolfen 16', 'Flying Forest - Wolfen 17', 'Flying Forest - Wolfen 18', 'Flying Forest - Wolfen 19', 'Flying Forest - Wolfen 20', 'Flying Forest - Wolfen 21', 'Flying Forest - Wolfen 22', 'Flying Forest - Wolfen 23', 'Flying Forest - Wolfen 24', 'Flying Forest - Wolfen 25', 'Flying Forest - Wolfen 26', 'Flying Forest - Wolfen 27', 'Flying Forest - Wolfen 28', 'Flying Forest - Wolfen 29', 'Flying Forest - Wolfen 30', 'Flying Forest - Wolfen 31', 'Flying Forest - Wolfen 32', 'Flying Forest - Wolfen 33', 'Flying Forest - Wolfen 34', 'Flying Forest - Wolfen 35', 'Flying Forest - Wolfen 36', 'Flying Forest - Wolfen 37', 'Flying Forest - Map Discovery'), 'Hunters Domain': ('Hunters Domain - Wolfen 01', 'Hunters Domain - Wolfen 02', 'Hunters Domain - Wolfen 03', 'Hunters Domain - Wolfen 04', 'Hunters Domain - Wolfen 05', 'Hunters Domain - Wolfen 06', 'Hunters Domain - Wolfen 07', 'Hunters Domain - Wolfen 08', 'Hunters Domain - Wolfen 09', 'Hunters Domain - Wolfen 10', 'Hunters Domain - Wolfen 11', 'Hunters Domain - Wolfen 12', 'Hunters Domain - Wolfen 13', 'Hunters Domain - Wolfen 14', 'Hunters Domain - Wolfen 15', 'Hunters Domain - Wolfen 16', 'Hunters Domain - Wolfen 17', 'Hunters Domain - Wolfen 18', 'Hunters Domain - Wolfen 19', 'Hunters Domain - Wolfen 20', 'Hunters Domain - Wolfen 21', 'Hunters Domain - Wolfen 22', 'Hunters Domain - Wolfen 23', 'Hunters Domain - Wolfen 24', 'Hunters Domain - Wolfen 25', 'Hunters Domain - Wolfen 26', 'Hunters Domain - Wolfen 27', 'Hunters Domain - Wolfen 28', 'Hunters Domain - Wolfen 29', 'Hunters Domain - Wolfen 30', 'Hunters Domain - Wolfen 31', 'Hunters Domain - Wolfen 32', 'Hunters Domain - Wolfen 33', 'Hunters Domain - Wolfen 34', 'Hunters Domain - Wolfen 35', 'Hunters Domain - Wolfen 36', 'Hunters Domain - Wolfen 37', 'Hunters Domain - Wolfen 38', 'Hunters Domain - Wolfen 39', 'Hunters Domain - Wolfen 40', 'Hunters Domain - Wolfen 41', 'Hunters Domain - Wolfen 42', 'Hunters Domain - Wolfen 43', 'Hunters Domain - Wolfen 44', 'Hunters Domain - Wolfen 45', 'Hunters Domain - Wolfen 46', "Hunters Domain - Hunter's Domain's Rune", 'Hunters Domain - Boss Defeated'), 'Wind Tower': ('Wind Tower - Wolfen 01', 'Wind Tower - Wolfen 02'), 'The Quarry': ('The Quarry - Wolfen 01', 'The Quarry - Wolfen 02', 'The Quarry - Wolfen 03', 'The Quarry - Wolfen 04', 'The Quarry - Wolfen 05', 'The Quarry - Wolfen 06', 'The Quarry - Wolfen 07', 'The Quarry - Wolfen 08', 'The Quarry - Wolfen 09', 'The Quarry - Wolfen 10', 'The Quarry - Wolfen 11', 'The Quarry - Wolfen 12', 'The Quarry - Wolfen 13', 'The Quarry - Wolfen 14', 'The Quarry - Wolfen 15', 'The Quarry - Wolfen 16', 'The Quarry - Wolfen 17', 'The Quarry - Wolfen 18', 'The Quarry - Wolfen 19', 'The Quarry - Wolfen 20', 'The Quarry - Wolfen 21', 'The Quarry - Wolfen 22', 'The Quarry - Wolfen 23', 'The Quarry - Wolfen 24', 'The Quarry - Wolfen 25', 'The Quarry - Wolfen 26', 'The Quarry - Wolfen 27', 'The Quarry - Wolfen 28', 'The Quarry - Wolfen 29', 'The Quarry - Wolfen 30', 'The Quarry - Wolfen 31', "The Quarry - Quarry's Rune", 'The Quarry - Map Discovery'), 'Amber Quarry': ('Amber Quarry - Wolfen 01', 'Amber Quarry - Wolfen 02', 'Amber Quarry - Wolfen 03', 'Amber Quarry - Wolfen 04', 'Amber Quarry - Wolfen 05', 'Amber Quarry - Wolfen 06', 'Amber Quarry - Wolfen 07', 'Amber Quarry - Wolfen 08', 'Amber Quarry - Wolfen 09', 'Amber Quarry - Wolfen 10', 'Amber Quarry - Wolfen 11', 'Amber Quarry - Wolfen 12', 'Amber Quarry - Wolfen 13', 'Amber Quarry - Wolfen 14', 'Amber Quarry - Brazul First Encounter'), 'The Root': ('The Root - Wolfen 01', 'The Root - Wolfen 02', 'The Root - Wolfen 03', 'The Root - Wolfen 04', 'The Root - Wolfen 05', 'The Root - Wolfen 06', 'The Root - Wolfen 07', "The Root - Root's Rune", 'The Root - Map Discovery'), 'The Air Post': ('The Air Post - Wolfen 01', 'The Air Post - Wolfen 02', 'The Air Post - Wolfen 03', 'The Air Post - Wolfen 04', 'The Air Post - Wolfen 05', 'The Air Post - Wolfen 06', 'The Air Post - Wolfen 07', 'The Air Post - Wolfen 08', 'The Air Post - Wolfen 09', 'The Air Post - Wolfen 10', 'The Air Post - Wolfen 11', 'The Air Post - Wolfen 12', 'The Air Post - Wolfen 13', 'The Air Post - Wolfen 14', 'The Air Post - Wolfen 15', 'The Air Post - Wolfen 16', 'The Air Post - Wolfen 17', 'The Air Post - Wolfen 18', 'The Air Post - Wolfen 19', 'The Air Post - Wolfen 20', 'The Air Post - Wolfen 21', 'The Air Post - Wolfen 22', 'The Air Post - Wolfen 23', 'The Air Post - Wolfen 24', 'The Air Post - Wolfen 25', 'The Air Post - Wolfen 26', 'The Air Post - Wolfen 27', 'The Air Post - Wolfen 28', 'The Air Post - Wolfen 29', 'The Air Post - Wolfen 30', 'The Air Post - Wolfen 31', 'The Air Post - Wolfen 32', 'The Air Post - Wolfen 33', 'The Air Post - Wolfen 34', 'The Air Post - Wolfen 35', 'The Air Post - Wolfen 36', 'The Air Post - Wolfen 37', 'The Air Post - Wolfen 38', 'The Air Post - Wolfen 39', 'The Air Post - Wolfen 40', 'The Air Post - Wolfen 41', 'The Air Post - Wolfen 42', 'The Air Post - Wolfen 43', 'The Air Post - Wolfen 44', 'The Air Post - Wolfen 45', 'The Air Post - Wolfen 46', 'The Air Post - Wolfen 47', 'The Air Post - Wolfen 48', 'The Air Post - Wolfen 49', 'The Air Post - Wolfen 50', 'The Air Post - Wolfen 51', 'The Air Post - Wolfen 52', 'The Air Post - Wolfen 53', 'The Air Post - Wolfen 54', 'The Air Post - Wolfen 55', 'The Air Post - Wolfen 56', 'The Air Post - Wolfen 57', 'The Air Post - Wolfen 58', 'The Air Post - Wolfen 59', 'The Air Post - Wolfen 60', 'The Air Post - Wolfen 61', "The Air Post - Air Post's Rune", 'The Air Post - Map Discovery'), 'Forgotten Island': ('Forgotten Island - Wolfen 01', 'Forgotten Island - Wolfen 02', 'Forgotten Island - Wolfen 03', 'Forgotten Island - Wolfen 04', 'Forgotten Island - Wolfen 05', 'Forgotten Island - Wolfen 06', 'Forgotten Island - Wolfen 07', 'Forgotten Island - Wolfen 08', "Forgotten Island - Forgotten Island's Rune"), 'Wolfen City': ('Wolfen City - Wolfen 01', 'Wolfen City - Wolfen 02', 'Wolfen City - Wolfen 03', 'Wolfen City - Wolfen 04', 'Wolfen City - Wolfen 05', 'Wolfen City - Wolfen 06', 'Wolfen City - Wolfen 07', 'Wolfen City - Wolfen 08', 'Wolfen City - Wolfen 09', 'Wolfen City - Wolfen 10', 'Wolfen City - Wolfen 11', 'Wolfen City - Wolfen 12', 'Wolfen City - Wolfen 13', 'Wolfen City - Wolfen 14', 'Wolfen City - Wolfen 15', 'Wolfen City - Wolfen 16', 'Wolfen City - Wolfen 17', 'Wolfen City - Wolfen 18', 'Wolfen City - Wolfen 19', 'Wolfen City - Wolfen 20', 'Wolfen City - Wolfen 21', 'Wolfen City - Wolfen 22', 'Wolfen City - Wolfen 23', 'Wolfen City - Wolfen 24', 'Wolfen City - Wolfen 25', 'Wolfen City - Wolfen 26', 'Wolfen City - Wolfen 27', 'Wolfen City - Wolfen 28', 'Wolfen City - Wolfen 29', 'Wolfen City - Wolfen 30', 'Wolfen City - Wolfen 31', 'Wolfen City - Wolfen 32', 'Wolfen City - Wolfen 33', 'Wolfen City - Wolfen 34', 'Wolfen City - Wolfen 35', 'Wolfen City - Wolfen 36', 'Wolfen City - Wolfen 37', 'Wolfen City - Wolfen 38', 'Wolfen City - Wolfen 39', 'Wolfen City - Wolfen 40', 'Wolfen City - Map Discovery'), 'The Fortress': ('The Fortress - Wolfen 01', 'The Fortress - Wolfen 02', 'The Fortress - Wolfen 03', 'The Fortress - Wolfen 04', 'The Fortress - Wolfen 05', 'The Fortress - Wolfen 06', 'The Fortress - Wolfen 07', 'The Fortress - Wolfen 08', 'The Fortress - Wolfen 09', 'The Fortress - Wolfen 10', 'The Fortress - Wolfen 11', 'The Fortress - Wolfen 12', 'The Fortress - Wolfen 13', 'The Fortress - Brazul Final Defeated')}
STARTER_LOCATION_NAME = "Nativs City - Wolfen 01"

# Final runtime goal: exact live Brazul-final transition. Credits probes were rejected.
ADDR_GOAL_BRAZUL_FINAL = 0x004255BC
GOAL_BRAZUL_FINAL_FROM = 1
GOAL_BRAZUL_FINAL_VALUE = 2
GOAL_ZONE = "The Fortress"


# ============================================================================
# 0.7.2 PLAYTEST PATCH — corrected natural Wolfen numbering + shop hotfix
# Generated from the validated natural-run audit; unresolved Fortress 04 is not guessed.
# ============================================================================
PROTOTYPE_VERSION = "0.7.2-wolfenfix-shop"
WOLFEN_ZONE_KEY_TO_LOCATION = {'Nativs City': {984: 'Nativs City - Wolfen 01'},
 'Flying Forest': {3210: 'Flying Forest - Wolfen 01',
                   2656: 'Flying Forest - Wolfen 02',
                   2462: 'Flying Forest - Wolfen 03',
                   7077: 'Flying Forest - Wolfen 04',
                   2451: 'Flying Forest - Wolfen 05',
                   2453: 'Flying Forest - Wolfen 06',
                   3112: 'Flying Forest - Wolfen 07',
                   2335: 'Flying Forest - Wolfen 08',
                   6134: 'Flying Forest - Wolfen 09',
                   5456: 'Flying Forest - Wolfen 10',
                   5454: 'Flying Forest - Wolfen 11',
                   3270: 'Flying Forest - Wolfen 12',
                   4672: 'Flying Forest - Wolfen 13',
                   5272: 'Flying Forest - Wolfen 14',
                   2689: 'Flying Forest - Wolfen 15',
                   2614: 'Flying Forest - Wolfen 16',
                   2618: 'Flying Forest - Wolfen 17',
                   2615: 'Flying Forest - Wolfen 18',
                   2617: 'Flying Forest - Wolfen 19',
                   2616: 'Flying Forest - Wolfen 20',
                   2727: 'Flying Forest - Wolfen 21',
                   2619: 'Flying Forest - Wolfen 22',
                   2620: 'Flying Forest - Wolfen 23',
                   2621: 'Flying Forest - Wolfen 24',
                   2622: 'Flying Forest - Wolfen 25',
                   2828: 'Flying Forest - Wolfen 26',
                   2688: 'Flying Forest - Wolfen 27',
                   2726: 'Flying Forest - Wolfen 28',
                   2260: 'Flying Forest - Wolfen 29',
                   5455: 'Flying Forest - Wolfen 30',
                   3237: 'Flying Forest - Wolfen 31',
                   3235: 'Flying Forest - Wolfen 32',
                   2297: 'Flying Forest - Wolfen 33',
                   2342: 'Flying Forest - Wolfen 34',
                   2351: 'Flying Forest - Wolfen 35',
                   2398: 'Flying Forest - Wolfen 36',
                   2354: 'Flying Forest - Wolfen 37'},
 'Hunters Domain': {3258: 'Hunters Domain - Wolfen 01',
                    3260: 'Hunters Domain - Wolfen 02',
                    3285: 'Hunters Domain - Wolfen 03',
                    2496: 'Hunters Domain - Wolfen 04',
                    3255: 'Hunters Domain - Wolfen 05',
                    3604: 'Hunters Domain - Wolfen 06',
                    2266: 'Hunters Domain - Wolfen 07',
                    3593: 'Hunters Domain - Wolfen 08',
                    3601: 'Hunters Domain - Wolfen 09',
                    10824: 'Hunters Domain - Wolfen 10',
                    3366: 'Hunters Domain - Wolfen 11',
                    3368: 'Hunters Domain - Wolfen 12',
                    3554: 'Hunters Domain - Wolfen 13',
                    3553: 'Hunters Domain - Wolfen 14',
                    3555: 'Hunters Domain - Wolfen 15',
                    8250: 'Hunters Domain - Wolfen 16',
                    10794: 'Hunters Domain - Wolfen 17',
                    10157: 'Hunters Domain - Wolfen 18',
                    11224: 'Hunters Domain - Wolfen 19',
                    8747: 'Hunters Domain - Wolfen 20',
                    3775: 'Hunters Domain - Wolfen 21',
                    3776: 'Hunters Domain - Wolfen 22',
                    3941: 'Hunters Domain - Wolfen 23',
                    3934: 'Hunters Domain - Wolfen 24',
                    3936: 'Hunters Domain - Wolfen 25',
                    10610: 'Hunters Domain - Wolfen 26',
                    1742: 'Hunters Domain - Wolfen 27',
                    1744: 'Hunters Domain - Wolfen 28',
                    10313: 'Hunters Domain - Wolfen 29',
                    10312: 'Hunters Domain - Wolfen 30',
                    10804: 'Hunters Domain - Wolfen 31',
                    10797: 'Hunters Domain - Wolfen 32',
                    11444: 'Hunters Domain - Wolfen 33',
                    11443: 'Hunters Domain - Wolfen 34',
                    10349: 'Hunters Domain - Wolfen 35',
                    10485: 'Hunters Domain - Wolfen 36',
                    3469: 'Hunters Domain - Wolfen 37',
                    3467: 'Hunters Domain - Wolfen 38',
                    3465: 'Hunters Domain - Wolfen 39',
                    3466: 'Hunters Domain - Wolfen 40',
                    6320: 'Hunters Domain - Wolfen 41',
                    10978: 'Hunters Domain - Wolfen 42',
                    8743: 'Hunters Domain - Wolfen 43',
                    9133: 'Hunters Domain - Wolfen 44',
                    11474: 'Hunters Domain - Wolfen 45',
                    11424: 'Hunters Domain - Wolfen 46'},
 'Wind Tower': {8330: 'Wind Tower - Wolfen 01', 1885: 'Wind Tower - Wolfen 02'},
 'The Quarry': {10602: 'The Quarry - Wolfen 01',
                1130: 'The Quarry - Wolfen 02',
                5999: 'The Quarry - Wolfen 03',
                6010: 'The Quarry - Wolfen 04',
                1162: 'The Quarry - Wolfen 05',
                1142: 'The Quarry - Wolfen 06',
                1143: 'The Quarry - Wolfen 07',
                9644: 'The Quarry - Wolfen 08',
                9646: 'The Quarry - Wolfen 09',
                9645: 'The Quarry - Wolfen 10',
                9466: 'The Quarry - Wolfen 11',
                9437: 'The Quarry - Wolfen 12',
                9436: 'The Quarry - Wolfen 13',
                1429: 'The Quarry - Wolfen 14',
                823: 'The Quarry - Wolfen 15',
                4232: 'The Quarry - Wolfen 16',
                9721: 'The Quarry - Wolfen 17',
                1437: 'The Quarry - Wolfen 18',
                6017: 'The Quarry - Wolfen 19',
                9392: 'The Quarry - Wolfen 20',
                9394: 'The Quarry - Wolfen 21',
                3868: 'The Quarry - Wolfen 22',
                3267: 'The Quarry - Wolfen 23',
                2556: 'The Quarry - Wolfen 24',
                9339: 'The Quarry - Wolfen 25',
                6526: 'The Quarry - Wolfen 26',
                6527: 'The Quarry - Wolfen 27',
                6078: 'The Quarry - Wolfen 28',
                6096: 'The Quarry - Wolfen 29',
                6079: 'The Quarry - Wolfen 30',
                6093: 'The Quarry - Wolfen 31'},
 'Amber Quarry': {9845: 'Amber Quarry - Wolfen 01',
                  9843: 'Amber Quarry - Wolfen 02',
                  9842: 'Amber Quarry - Wolfen 03',
                  9988: 'Amber Quarry - Wolfen 04',
                  9989: 'Amber Quarry - Wolfen 05',
                  9841: 'Amber Quarry - Wolfen 06',
                  7569: 'Amber Quarry - Wolfen 07',
                  9511: 'Amber Quarry - Wolfen 08',
                  9528: 'Amber Quarry - Wolfen 09',
                  9538: 'Amber Quarry - Wolfen 10',
                  9513: 'Amber Quarry - Wolfen 11',
                  9518: 'Amber Quarry - Wolfen 12',
                  9515: 'Amber Quarry - Wolfen 13',
                  9516: 'Amber Quarry - Wolfen 14'},
 'The Root': {3486: 'The Root - Wolfen 01',
              336: 'The Root - Wolfen 02',
              331: 'The Root - Wolfen 03',
              330: 'The Root - Wolfen 04',
              312: 'The Root - Wolfen 05',
              3732: 'The Root - Wolfen 06',
              3731: 'The Root - Wolfen 07'},
 'The Air Post': {9940: 'The Air Post - Wolfen 01',
                  9943: 'The Air Post - Wolfen 02',
                  1357: 'The Air Post - Wolfen 03',
                  1912: 'The Air Post - Wolfen 04',
                  8421: 'The Air Post - Wolfen 05',
                  7285: 'The Air Post - Wolfen 06',
                  9944: 'The Air Post - Wolfen 07',
                  1327: 'The Air Post - Wolfen 08',
                  8758: 'The Air Post - Wolfen 09',
                  10078: 'The Air Post - Wolfen 10',
                  10079: 'The Air Post - Wolfen 11',
                  4432: 'The Air Post - Wolfen 12',
                  4433: 'The Air Post - Wolfen 13',
                  1449: 'The Air Post - Wolfen 14',
                  10403: 'The Air Post - Wolfen 15',
                  11391: 'The Air Post - Wolfen 16',
                  917: 'The Air Post - Wolfen 17',
                  1034: 'The Air Post - Wolfen 18',
                  1010: 'The Air Post - Wolfen 19',
                  11389: 'The Air Post - Wolfen 20',
                  11751: 'The Air Post - Wolfen 21',
                  11393: 'The Air Post - Wolfen 22',
                  4621: 'The Air Post - Wolfen 23',
                  4624: 'The Air Post - Wolfen 24',
                  4627: 'The Air Post - Wolfen 25',
                  4622: 'The Air Post - Wolfen 26',
                  1518: 'The Air Post - Wolfen 27',
                  7445: 'The Air Post - Wolfen 28',
                  9817: 'The Air Post - Wolfen 29',
                  9801: 'The Air Post - Wolfen 30',
                  418: 'The Air Post - Wolfen 31',
                  420: 'The Air Post - Wolfen 32',
                  430: 'The Air Post - Wolfen 33',
                  7602: 'The Air Post - Wolfen 34',
                  9398: 'The Air Post - Wolfen 35',
                  7795: 'The Air Post - Wolfen 36',
                  7792: 'The Air Post - Wolfen 37',
                  7791: 'The Air Post - Wolfen 38',
                  7793: 'The Air Post - Wolfen 39',
                  7790: 'The Air Post - Wolfen 40',
                  7794: 'The Air Post - Wolfen 41',
                  4756: 'The Air Post - Wolfen 42',
                  4757: 'The Air Post - Wolfen 43',
                  4755: 'The Air Post - Wolfen 44',
                  4758: 'The Air Post - Wolfen 45',
                  4754: 'The Air Post - Wolfen 46',
                  4759: 'The Air Post - Wolfen 47',
                  646: 'The Air Post - Wolfen 48',
                  9598: 'The Air Post - Wolfen 49',
                  9597: 'The Air Post - Wolfen 50',
                  9600: 'The Air Post - Wolfen 51',
                  10613: 'The Air Post - Wolfen 52',
                  9856: 'The Air Post - Wolfen 53',
                  10067: 'The Air Post - Wolfen 54',
                  9946: 'The Air Post - Wolfen 55',
                  9949: 'The Air Post - Wolfen 56',
                  9950: 'The Air Post - Wolfen 57',
                  10380: 'The Air Post - Wolfen 58',
                  9204: 'The Air Post - Wolfen 59',
                  9203: 'The Air Post - Wolfen 60',
                  9595: 'The Air Post - Wolfen 61'},
 'Forgotten Island': {2054: 'Forgotten Island - Wolfen 01',
                      2084: 'Forgotten Island - Wolfen 02',
                      2102: 'Forgotten Island - Wolfen 03',
                      6811: 'Forgotten Island - Wolfen 04',
                      5060: 'Forgotten Island - Wolfen 05',
                      5059: 'Forgotten Island - Wolfen 06',
                      6215: 'Forgotten Island - Wolfen 07',
                      4944: 'Forgotten Island - Wolfen 08'},
 'Wolfen City': {2688: 'Wolfen City - Wolfen 01',
                 1434: 'Wolfen City - Wolfen 02',
                 1443: 'Wolfen City - Wolfen 03',
                 1422: 'Wolfen City - Wolfen 04',
                 494: 'Wolfen City - Wolfen 05',
                 3678: 'Wolfen City - Wolfen 06',
                 3677: 'Wolfen City - Wolfen 07',
                 1750: 'Wolfen City - Wolfen 08',
                 1680: 'Wolfen City - Wolfen 09',
                 3734: 'Wolfen City - Wolfen 10',
                 807: 'Wolfen City - Wolfen 11',
                 1652: 'Wolfen City - Wolfen 12',
                 3733: 'Wolfen City - Wolfen 13',
                 3687: 'Wolfen City - Wolfen 14',
                 778: 'Wolfen City - Wolfen 15',
                 1641: 'Wolfen City - Wolfen 16',
                 3699: 'Wolfen City - Wolfen 17',
                 1822: 'Wolfen City - Wolfen 18',
                 1787: 'Wolfen City - Wolfen 19',
                 752: 'Wolfen City - Wolfen 20',
                 1374: 'Wolfen City - Wolfen 21',
                 770: 'Wolfen City - Wolfen 22',
                 771: 'Wolfen City - Wolfen 23',
                 3791: 'Wolfen City - Wolfen 24',
                 3761: 'Wolfen City - Wolfen 25',
                 3762: 'Wolfen City - Wolfen 26',
                 2333: 'Wolfen City - Wolfen 27',
                 2341: 'Wolfen City - Wolfen 28',
                 2335: 'Wolfen City - Wolfen 29',
                 2337: 'Wolfen City - Wolfen 30',
                 2339: 'Wolfen City - Wolfen 31',
                 1842: 'Wolfen City - Wolfen 32',
                 2004: 'Wolfen City - Wolfen 33',
                 1998: 'Wolfen City - Wolfen 34',
                 1999: 'Wolfen City - Wolfen 35',
                 1989: 'Wolfen City - Wolfen 36',
                 1267: 'Wolfen City - Wolfen 37',
                 1268: 'Wolfen City - Wolfen 38',
                 1270: 'Wolfen City - Wolfen 39',
                 1269: 'Wolfen City - Wolfen 40'},
 'The Fortress': {1133: 'The Fortress - Wolfen 01',
                  1126: 'The Fortress - Wolfen 02',
                  1134: 'The Fortress - Wolfen 03',
                  1128: 'The Fortress - Wolfen 04',
                  1147: 'The Fortress - Wolfen 05',
                  1125: 'The Fortress - Wolfen 06',
                  1132: 'The Fortress - Wolfen 07',
                  1122: 'The Fortress - Wolfen 08',
                  1121: 'The Fortress - Wolfen 09',
                  1129: 'The Fortress - Wolfen 10',
                  1131: 'The Fortress - Wolfen 11',
                  1124: 'The Fortress - Wolfen 12',
                  895: 'The Fortress - Wolfen 13'}}
WOLFEN_KEY_TO_LOCATION = {984: 'Nativs City - Wolfen 01',
 3210: 'Flying Forest - Wolfen 01',
 2656: 'Flying Forest - Wolfen 02',
 2462: 'Flying Forest - Wolfen 03',
 7077: 'Flying Forest - Wolfen 04',
 2451: 'Flying Forest - Wolfen 05',
 2453: 'Flying Forest - Wolfen 06',
 3112: 'Flying Forest - Wolfen 07',
 2335: 'Flying Forest - Wolfen 08',
 6134: 'Flying Forest - Wolfen 09',
 5456: 'Flying Forest - Wolfen 10',
 5454: 'Flying Forest - Wolfen 11',
 3270: 'Flying Forest - Wolfen 12',
 4672: 'Flying Forest - Wolfen 13',
 5272: 'Flying Forest - Wolfen 14',
 2689: 'Flying Forest - Wolfen 15',
 2614: 'Flying Forest - Wolfen 16',
 2618: 'Flying Forest - Wolfen 17',
 2615: 'Flying Forest - Wolfen 18',
 2617: 'Flying Forest - Wolfen 19',
 2616: 'Flying Forest - Wolfen 20',
 2727: 'Flying Forest - Wolfen 21',
 2619: 'Flying Forest - Wolfen 22',
 2620: 'Flying Forest - Wolfen 23',
 2621: 'Flying Forest - Wolfen 24',
 2622: 'Flying Forest - Wolfen 25',
 2828: 'Flying Forest - Wolfen 26',
 2688: 'Flying Forest - Wolfen 27',
 2726: 'Flying Forest - Wolfen 28',
 2260: 'Flying Forest - Wolfen 29',
 5455: 'Flying Forest - Wolfen 30',
 3237: 'Flying Forest - Wolfen 31',
 3235: 'Flying Forest - Wolfen 32',
 2297: 'Flying Forest - Wolfen 33',
 2342: 'Flying Forest - Wolfen 34',
 2351: 'Flying Forest - Wolfen 35',
 2398: 'Flying Forest - Wolfen 36',
 2354: 'Flying Forest - Wolfen 37',
 3258: 'Hunters Domain - Wolfen 01',
 3260: 'Hunters Domain - Wolfen 02',
 3285: 'Hunters Domain - Wolfen 03',
 2496: 'Hunters Domain - Wolfen 04',
 3255: 'Hunters Domain - Wolfen 05',
 3604: 'Hunters Domain - Wolfen 06',
 2266: 'Hunters Domain - Wolfen 07',
 3593: 'Hunters Domain - Wolfen 08',
 3601: 'Hunters Domain - Wolfen 09',
 10824: 'Hunters Domain - Wolfen 10',
 3366: 'Hunters Domain - Wolfen 11',
 3368: 'Hunters Domain - Wolfen 12',
 3554: 'Hunters Domain - Wolfen 13',
 3553: 'Hunters Domain - Wolfen 14',
 3555: 'Hunters Domain - Wolfen 15',
 8250: 'Hunters Domain - Wolfen 16',
 10794: 'Hunters Domain - Wolfen 17',
 10157: 'Hunters Domain - Wolfen 18',
 11224: 'Hunters Domain - Wolfen 19',
 8747: 'Hunters Domain - Wolfen 20',
 3775: 'Hunters Domain - Wolfen 21',
 3776: 'Hunters Domain - Wolfen 22',
 3941: 'Hunters Domain - Wolfen 23',
 3934: 'Hunters Domain - Wolfen 24',
 3936: 'Hunters Domain - Wolfen 25',
 10610: 'Hunters Domain - Wolfen 26',
 1742: 'Hunters Domain - Wolfen 27',
 1744: 'Hunters Domain - Wolfen 28',
 10313: 'Hunters Domain - Wolfen 29',
 10312: 'Hunters Domain - Wolfen 30',
 10804: 'Hunters Domain - Wolfen 31',
 10797: 'Hunters Domain - Wolfen 32',
 11444: 'Hunters Domain - Wolfen 33',
 11443: 'Hunters Domain - Wolfen 34',
 10349: 'Hunters Domain - Wolfen 35',
 10485: 'Hunters Domain - Wolfen 36',
 3469: 'Hunters Domain - Wolfen 37',
 3467: 'Hunters Domain - Wolfen 38',
 3465: 'Hunters Domain - Wolfen 39',
 3466: 'Hunters Domain - Wolfen 40',
 6320: 'Hunters Domain - Wolfen 41',
 10978: 'Hunters Domain - Wolfen 42',
 8743: 'Hunters Domain - Wolfen 43',
 9133: 'Hunters Domain - Wolfen 44',
 11474: 'Hunters Domain - Wolfen 45',
 11424: 'Hunters Domain - Wolfen 46',
 8330: 'Wind Tower - Wolfen 01',
 1885: 'Wind Tower - Wolfen 02',
 10602: 'The Quarry - Wolfen 01',
 1130: 'The Quarry - Wolfen 02',
 5999: 'The Quarry - Wolfen 03',
 6010: 'The Quarry - Wolfen 04',
 1162: 'The Quarry - Wolfen 05',
 1142: 'The Quarry - Wolfen 06',
 1143: 'The Quarry - Wolfen 07',
 9644: 'The Quarry - Wolfen 08',
 9646: 'The Quarry - Wolfen 09',
 9645: 'The Quarry - Wolfen 10',
 9466: 'The Quarry - Wolfen 11',
 9437: 'The Quarry - Wolfen 12',
 9436: 'The Quarry - Wolfen 13',
 1429: 'The Quarry - Wolfen 14',
 823: 'The Quarry - Wolfen 15',
 4232: 'The Quarry - Wolfen 16',
 9721: 'The Quarry - Wolfen 17',
 1437: 'The Quarry - Wolfen 18',
 6017: 'The Quarry - Wolfen 19',
 9392: 'The Quarry - Wolfen 20',
 9394: 'The Quarry - Wolfen 21',
 3868: 'The Quarry - Wolfen 22',
 3267: 'The Quarry - Wolfen 23',
 2556: 'The Quarry - Wolfen 24',
 9339: 'The Quarry - Wolfen 25',
 6526: 'The Quarry - Wolfen 26',
 6527: 'The Quarry - Wolfen 27',
 6078: 'The Quarry - Wolfen 28',
 6096: 'The Quarry - Wolfen 29',
 6079: 'The Quarry - Wolfen 30',
 6093: 'The Quarry - Wolfen 31',
 9845: 'Amber Quarry - Wolfen 01',
 9843: 'Amber Quarry - Wolfen 02',
 9842: 'Amber Quarry - Wolfen 03',
 9988: 'Amber Quarry - Wolfen 04',
 9989: 'Amber Quarry - Wolfen 05',
 9841: 'Amber Quarry - Wolfen 06',
 7569: 'Amber Quarry - Wolfen 07',
 9511: 'Amber Quarry - Wolfen 08',
 9528: 'Amber Quarry - Wolfen 09',
 9538: 'Amber Quarry - Wolfen 10',
 9513: 'Amber Quarry - Wolfen 11',
 9518: 'Amber Quarry - Wolfen 12',
 9515: 'Amber Quarry - Wolfen 13',
 9516: 'Amber Quarry - Wolfen 14',
 3486: 'The Root - Wolfen 01',
 336: 'The Root - Wolfen 02',
 331: 'The Root - Wolfen 03',
 330: 'The Root - Wolfen 04',
 312: 'The Root - Wolfen 05',
 3732: 'The Root - Wolfen 06',
 3731: 'The Root - Wolfen 07',
 9940: 'The Air Post - Wolfen 01',
 9943: 'The Air Post - Wolfen 02',
 1357: 'The Air Post - Wolfen 03',
 1912: 'The Air Post - Wolfen 04',
 8421: 'The Air Post - Wolfen 05',
 7285: 'The Air Post - Wolfen 06',
 9944: 'The Air Post - Wolfen 07',
 1327: 'The Air Post - Wolfen 08',
 8758: 'The Air Post - Wolfen 09',
 10078: 'The Air Post - Wolfen 10',
 10079: 'The Air Post - Wolfen 11',
 4432: 'The Air Post - Wolfen 12',
 4433: 'The Air Post - Wolfen 13',
 1449: 'The Air Post - Wolfen 14',
 10403: 'The Air Post - Wolfen 15',
 11391: 'The Air Post - Wolfen 16',
 917: 'The Air Post - Wolfen 17',
 1034: 'The Air Post - Wolfen 18',
 1010: 'The Air Post - Wolfen 19',
 11389: 'The Air Post - Wolfen 20',
 11751: 'The Air Post - Wolfen 21',
 11393: 'The Air Post - Wolfen 22',
 4621: 'The Air Post - Wolfen 23',
 4624: 'The Air Post - Wolfen 24',
 4627: 'The Air Post - Wolfen 25',
 4622: 'The Air Post - Wolfen 26',
 1518: 'The Air Post - Wolfen 27',
 7445: 'The Air Post - Wolfen 28',
 9817: 'The Air Post - Wolfen 29',
 9801: 'The Air Post - Wolfen 30',
 418: 'The Air Post - Wolfen 31',
 420: 'The Air Post - Wolfen 32',
 430: 'The Air Post - Wolfen 33',
 7602: 'The Air Post - Wolfen 34',
 9398: 'The Air Post - Wolfen 35',
 7795: 'The Air Post - Wolfen 36',
 7792: 'The Air Post - Wolfen 37',
 7791: 'The Air Post - Wolfen 38',
 7793: 'The Air Post - Wolfen 39',
 7790: 'The Air Post - Wolfen 40',
 7794: 'The Air Post - Wolfen 41',
 4756: 'The Air Post - Wolfen 42',
 4757: 'The Air Post - Wolfen 43',
 4755: 'The Air Post - Wolfen 44',
 4758: 'The Air Post - Wolfen 45',
 4754: 'The Air Post - Wolfen 46',
 4759: 'The Air Post - Wolfen 47',
 646: 'The Air Post - Wolfen 48',
 9598: 'The Air Post - Wolfen 49',
 9597: 'The Air Post - Wolfen 50',
 9600: 'The Air Post - Wolfen 51',
 10613: 'The Air Post - Wolfen 52',
 9856: 'The Air Post - Wolfen 53',
 10067: 'The Air Post - Wolfen 54',
 9946: 'The Air Post - Wolfen 55',
 9949: 'The Air Post - Wolfen 56',
 9950: 'The Air Post - Wolfen 57',
 10380: 'The Air Post - Wolfen 58',
 9204: 'The Air Post - Wolfen 59',
 9203: 'The Air Post - Wolfen 60',
 9595: 'The Air Post - Wolfen 61',
 2054: 'Forgotten Island - Wolfen 01',
 2084: 'Forgotten Island - Wolfen 02',
 2102: 'Forgotten Island - Wolfen 03',
 6811: 'Forgotten Island - Wolfen 04',
 5060: 'Forgotten Island - Wolfen 05',
 5059: 'Forgotten Island - Wolfen 06',
 6215: 'Forgotten Island - Wolfen 07',
 4944: 'Forgotten Island - Wolfen 08',
 1434: 'Wolfen City - Wolfen 02',
 1443: 'Wolfen City - Wolfen 03',
 1422: 'Wolfen City - Wolfen 04',
 494: 'Wolfen City - Wolfen 05',
 3678: 'Wolfen City - Wolfen 06',
 3677: 'Wolfen City - Wolfen 07',
 1750: 'Wolfen City - Wolfen 08',
 1680: 'Wolfen City - Wolfen 09',
 3734: 'Wolfen City - Wolfen 10',
 807: 'Wolfen City - Wolfen 11',
 1652: 'Wolfen City - Wolfen 12',
 3733: 'Wolfen City - Wolfen 13',
 3687: 'Wolfen City - Wolfen 14',
 778: 'Wolfen City - Wolfen 15',
 1641: 'Wolfen City - Wolfen 16',
 3699: 'Wolfen City - Wolfen 17',
 1822: 'Wolfen City - Wolfen 18',
 1787: 'Wolfen City - Wolfen 19',
 752: 'Wolfen City - Wolfen 20',
 1374: 'Wolfen City - Wolfen 21',
 770: 'Wolfen City - Wolfen 22',
 771: 'Wolfen City - Wolfen 23',
 3791: 'Wolfen City - Wolfen 24',
 3761: 'Wolfen City - Wolfen 25',
 3762: 'Wolfen City - Wolfen 26',
 2333: 'Wolfen City - Wolfen 27',
 2341: 'Wolfen City - Wolfen 28',
 2337: 'Wolfen City - Wolfen 30',
 2339: 'Wolfen City - Wolfen 31',
 1842: 'Wolfen City - Wolfen 32',
 2004: 'Wolfen City - Wolfen 33',
 1998: 'Wolfen City - Wolfen 34',
 1999: 'Wolfen City - Wolfen 35',
 1989: 'Wolfen City - Wolfen 36',
 1267: 'Wolfen City - Wolfen 37',
 1268: 'Wolfen City - Wolfen 38',
 1270: 'Wolfen City - Wolfen 39',
 1269: 'Wolfen City - Wolfen 40',
 1133: 'The Fortress - Wolfen 01',
 1126: 'The Fortress - Wolfen 02',
 1134: 'The Fortress - Wolfen 03',
 1128: 'The Fortress - Wolfen 04',
 1147: 'The Fortress - Wolfen 05',
 1125: 'The Fortress - Wolfen 06',
 1132: 'The Fortress - Wolfen 07',
 1122: 'The Fortress - Wolfen 08',
 1121: 'The Fortress - Wolfen 09',
 1129: 'The Fortress - Wolfen 10',
 1131: 'The Fortress - Wolfen 11',
 1124: 'The Fortress - Wolfen 12',
 895: 'The Fortress - Wolfen 13'}
WOLFEN_KEY_TO_ZONES = {984: ['Nativs City'],
 3210: ['Flying Forest'],
 2656: ['Flying Forest'],
 2462: ['Flying Forest'],
 7077: ['Flying Forest'],
 2451: ['Flying Forest'],
 2453: ['Flying Forest'],
 3112: ['Flying Forest'],
 2335: ['Flying Forest', 'Wolfen City'],
 6134: ['Flying Forest'],
 5456: ['Flying Forest'],
 5454: ['Flying Forest'],
 3270: ['Flying Forest'],
 4672: ['Flying Forest'],
 5272: ['Flying Forest'],
 2689: ['Flying Forest'],
 2614: ['Flying Forest'],
 2618: ['Flying Forest'],
 2615: ['Flying Forest'],
 2617: ['Flying Forest'],
 2616: ['Flying Forest'],
 2727: ['Flying Forest'],
 2619: ['Flying Forest'],
 2620: ['Flying Forest'],
 2621: ['Flying Forest'],
 2622: ['Flying Forest'],
 2828: ['Flying Forest'],
 2688: ['Flying Forest', 'Wolfen City'],
 2726: ['Flying Forest'],
 2260: ['Flying Forest'],
 5455: ['Flying Forest'],
 3237: ['Flying Forest'],
 3235: ['Flying Forest'],
 2297: ['Flying Forest'],
 2342: ['Flying Forest'],
 2351: ['Flying Forest'],
 2398: ['Flying Forest'],
 2354: ['Flying Forest'],
 3258: ['Hunters Domain'],
 3260: ['Hunters Domain'],
 3285: ['Hunters Domain'],
 2496: ['Hunters Domain'],
 3255: ['Hunters Domain'],
 3604: ['Hunters Domain'],
 2266: ['Hunters Domain'],
 3593: ['Hunters Domain'],
 3601: ['Hunters Domain'],
 10824: ['Hunters Domain'],
 3366: ['Hunters Domain'],
 3368: ['Hunters Domain'],
 3554: ['Hunters Domain'],
 3553: ['Hunters Domain'],
 3555: ['Hunters Domain'],
 8250: ['Hunters Domain'],
 10794: ['Hunters Domain'],
 10157: ['Hunters Domain'],
 11224: ['Hunters Domain'],
 8747: ['Hunters Domain'],
 3775: ['Hunters Domain'],
 3776: ['Hunters Domain'],
 3941: ['Hunters Domain'],
 3934: ['Hunters Domain'],
 3936: ['Hunters Domain'],
 10610: ['Hunters Domain'],
 1742: ['Hunters Domain'],
 1744: ['Hunters Domain'],
 10313: ['Hunters Domain'],
 10312: ['Hunters Domain'],
 10804: ['Hunters Domain'],
 10797: ['Hunters Domain'],
 11444: ['Hunters Domain'],
 11443: ['Hunters Domain'],
 10349: ['Hunters Domain'],
 10485: ['Hunters Domain'],
 3469: ['Hunters Domain'],
 3467: ['Hunters Domain'],
 3465: ['Hunters Domain'],
 3466: ['Hunters Domain'],
 6320: ['Hunters Domain'],
 10978: ['Hunters Domain'],
 8743: ['Hunters Domain'],
 9133: ['Hunters Domain'],
 11474: ['Hunters Domain'],
 11424: ['Hunters Domain'],
 8330: ['Wind Tower'],
 1885: ['Wind Tower'],
 10602: ['The Quarry'],
 1130: ['The Quarry'],
 5999: ['The Quarry'],
 6010: ['The Quarry'],
 1162: ['The Quarry'],
 1142: ['The Quarry'],
 1143: ['The Quarry'],
 9644: ['The Quarry'],
 9646: ['The Quarry'],
 9645: ['The Quarry'],
 9466: ['The Quarry'],
 9437: ['The Quarry'],
 9436: ['The Quarry'],
 1429: ['The Quarry'],
 823: ['The Quarry'],
 4232: ['The Quarry'],
 9721: ['The Quarry'],
 1437: ['The Quarry'],
 6017: ['The Quarry'],
 9392: ['The Quarry'],
 9394: ['The Quarry'],
 3868: ['The Quarry'],
 3267: ['The Quarry'],
 2556: ['The Quarry'],
 9339: ['The Quarry'],
 6526: ['The Quarry'],
 6527: ['The Quarry'],
 6078: ['The Quarry'],
 6096: ['The Quarry'],
 6079: ['The Quarry'],
 6093: ['The Quarry'],
 9845: ['Amber Quarry'],
 9843: ['Amber Quarry'],
 9842: ['Amber Quarry'],
 9988: ['Amber Quarry'],
 9989: ['Amber Quarry'],
 9841: ['Amber Quarry'],
 7569: ['Amber Quarry'],
 9511: ['Amber Quarry'],
 9528: ['Amber Quarry'],
 9538: ['Amber Quarry'],
 9513: ['Amber Quarry'],
 9518: ['Amber Quarry'],
 9515: ['Amber Quarry'],
 9516: ['Amber Quarry'],
 3486: ['The Root'],
 336: ['The Root'],
 331: ['The Root'],
 330: ['The Root'],
 312: ['The Root'],
 3732: ['The Root'],
 3731: ['The Root'],
 9940: ['The Air Post'],
 9943: ['The Air Post'],
 1357: ['The Air Post'],
 1912: ['The Air Post'],
 8421: ['The Air Post'],
 7285: ['The Air Post'],
 9944: ['The Air Post'],
 1327: ['The Air Post'],
 8758: ['The Air Post'],
 10078: ['The Air Post'],
 10079: ['The Air Post'],
 4432: ['The Air Post'],
 4433: ['The Air Post'],
 1449: ['The Air Post'],
 10403: ['The Air Post'],
 11391: ['The Air Post'],
 917: ['The Air Post'],
 1034: ['The Air Post'],
 1010: ['The Air Post'],
 11389: ['The Air Post'],
 11751: ['The Air Post'],
 11393: ['The Air Post'],
 4621: ['The Air Post'],
 4624: ['The Air Post'],
 4627: ['The Air Post'],
 4622: ['The Air Post'],
 1518: ['The Air Post'],
 7445: ['The Air Post'],
 9817: ['The Air Post'],
 9801: ['The Air Post'],
 418: ['The Air Post'],
 420: ['The Air Post'],
 430: ['The Air Post'],
 7602: ['The Air Post'],
 9398: ['The Air Post'],
 7795: ['The Air Post'],
 7792: ['The Air Post'],
 7791: ['The Air Post'],
 7793: ['The Air Post'],
 7790: ['The Air Post'],
 7794: ['The Air Post'],
 4756: ['The Air Post'],
 4757: ['The Air Post'],
 4755: ['The Air Post'],
 4758: ['The Air Post'],
 4754: ['The Air Post'],
 4759: ['The Air Post'],
 646: ['The Air Post'],
 9598: ['The Air Post'],
 9597: ['The Air Post'],
 9600: ['The Air Post'],
 10613: ['The Air Post'],
 9856: ['The Air Post'],
 10067: ['The Air Post'],
 9946: ['The Air Post'],
 9949: ['The Air Post'],
 9950: ['The Air Post'],
 10380: ['The Air Post'],
 9204: ['The Air Post'],
 9203: ['The Air Post'],
 9595: ['The Air Post'],
 2054: ['Forgotten Island'],
 2084: ['Forgotten Island'],
 2102: ['Forgotten Island'],
 6811: ['Forgotten Island'],
 5060: ['Forgotten Island'],
 5059: ['Forgotten Island'],
 6215: ['Forgotten Island'],
 4944: ['Forgotten Island'],
 1434: ['Wolfen City'],
 1443: ['Wolfen City'],
 1422: ['Wolfen City'],
 494: ['Wolfen City'],
 3678: ['Wolfen City'],
 3677: ['Wolfen City'],
 1750: ['Wolfen City'],
 1680: ['Wolfen City'],
 3734: ['Wolfen City'],
 807: ['Wolfen City'],
 1652: ['Wolfen City'],
 3733: ['Wolfen City'],
 3687: ['Wolfen City'],
 778: ['Wolfen City'],
 1641: ['Wolfen City'],
 3699: ['Wolfen City'],
 1822: ['Wolfen City'],
 1787: ['Wolfen City'],
 752: ['Wolfen City'],
 1374: ['Wolfen City'],
 770: ['Wolfen City'],
 771: ['Wolfen City'],
 3791: ['Wolfen City'],
 3761: ['Wolfen City'],
 3762: ['Wolfen City'],
 2333: ['Wolfen City'],
 2341: ['Wolfen City'],
 2337: ['Wolfen City'],
 2339: ['Wolfen City'],
 1842: ['Wolfen City'],
 2004: ['Wolfen City'],
 1998: ['Wolfen City'],
 1999: ['Wolfen City'],
 1989: ['Wolfen City'],
 1267: ['Wolfen City'],
 1268: ['Wolfen City'],
 1270: ['Wolfen City'],
 1269: ['Wolfen City'],
 1133: ['The Fortress'],
 1126: ['The Fortress'],
 1134: ['The Fortress'],
 1128: ['The Fortress'],
 1147: ['The Fortress'],
 1125: ['The Fortress'],
 1132: ['The Fortress'],
 1122: ['The Fortress'],
 1121: ['The Fortress'],
 1129: ['The Fortress'],
 1131: ['The Fortress'],
 1124: ['The Fortress'],
 895: ['The Fortress']}
SHOP_VANILLA_REWARD_STATE = {'Nativs City - Shop - Basic Boomy': {'address': 4346908, 'kind': 'u32'},
 'Nativs City - Shop - Yellow Bracelet': {'address': 4346916, 'kind': 'u32'},
 'Nativs City - Shop - Telescope': {'address': 4346948, 'kind': 'u32'},
 'Nativs City - Shop - Magic Board': {'address': 4346964, 'kind': 'u32'},
 'Nativs City - Shop - Green Bracelet': {'address': 4346916, 'kind': 'u32'},
 'Nativs City - Shop - Climbing Gloves': {'address': 4346900, 'kind': 'u32'},
 'Nativs City - Shop - Extra Energy Bar 1': {'address': 4346996, 'kind': 'life_gauge'},
 'Nativs City - Shop - Blue Bracelet': {'address': 4346916, 'kind': 'u32'},
 'Nativs City - Shop - Jamgut Birdcall': {'address': 4346940, 'kind': 'u32'},
 'Nativs City - Shop - Speed Board': {'address': 4346964, 'kind': 'u32'},
 'Nativs City - Shop - Golden Boomy': {'address': 4346908, 'kind': 'u32'},
 'Nativs City - Shop - Silver Bracelet': {'address': 4346916, 'kind': 'u32'},
 'Nativs City - Shop - Silver Boomy': {'address': 4346908, 'kind': 'u32'},
 'Nativs City - Shop - Brown Bracelet': {'address': 4346916, 'kind': 'u32'},
 'Nativs City - Shop - Magic Bouncers': {'address': 4346892, 'kind': 'u32'},
 'Nativs City - Shop - Extra Energy Bar 2': {'address': 4346996, 'kind': 'life_gauge'},
 'Nativs City - Shop - Black Bracelet': {'address': 4346916, 'kind': 'u32'},
 'Nativs City - Shop - Gold Bracelet': {'address': 4346916, 'kind': 'u32'}}
ADDR_GOAL_CREDITS = 0x0044982C
GOAL_CREDITS_FROM = 0
GOAL_CREDITS_VALUE = 4


# ============================================================================
# 0.7.3 VALIDATION PLAYTEST — EVERYTHING FOUND / FAST TRAVELS / KEYITEM PROBES
# 2026-10-04. This block intentionally supersedes the 0.7.2 tables above.
# ============================================================================
PROTOTYPE_VERSION = "0.7.3-validation-all-found"
AP_BUILD_VERSION = PROTOTYPE_VERSION

FAST_TRAVEL_VTABLE = 0x00441250
FAST_TRAVEL_STATE_OFFSET = 0x2A0
FAST_TRAVEL_STATE_OFF = 0
FAST_TRAVEL_STATE_ON = 1
FAST_TRAVEL_DESCRIPTOR_OFFSET = 0x1C
FAST_TRAVEL_KEY_OFFSET = 0x28

# Zone-scoped descriptor candidates observed on live actor+0x2A0 0->1 activation.
# Used as live identities for this validation build; not claimed as universal
# persistent master keys unless separately proven.
FAST_TRAVEL_ZONE_KEY_TO_LOCATION = {
    "Flying Forest": {
        0x0DB7: "Flying Forest - Fast Travel 01",
        0x0FB0: "Flying Forest - Fast Travel 02",
    },
    "Hunters Domain": {
        0x1307: "Hunters Domain - Fast Travel 02",
        0x130D: "Hunters Domain - Fast Travel 03",
    },
    "The Quarry": {
        0x2842: "The Quarry - Fast Travel 01",
        0x0AEA: "The Quarry - Fast Travel 02",
        0x0BF8: "The Quarry - Fast Travel 03",
    },
    "Amber Quarry": {
        0x0088: "Amber Quarry - Fast Travel 01",
    },
    "The Root": {
        0x0A72: "The Root - Fast Travel 01",
        0x0B54: "The Root - Fast Travel 02",
        0x0ACE: "The Root - Fast Travel 03",
        0x0C26: "The Root - Fast Travel 04",
    },
    "The Air Post": {
        0x0D8D: "The Air Post - Fast Travel 01",
        0x0E18: "The Air Post - Fast Travel 02",
        0x0DA5: "The Air Post - Fast Travel 03",
        0x0FF0: "The Air Post - Fast Travel 04",
    },
    "Forgotten Island": {
        0x073D: "Forgotten Island - Fast Travel 01",
        0x1115: "Forgotten Island - Fast Travel 02",
        0x063A: "Forgotten Island - Fast Travel 03",
        0x0620: "Forgotten Island - Fast Travel 04",
        0x0594: "Forgotten Island - Fast Travel 05",
    },
    "Wolfen City": {
        0x03D9: "Wolfen City - Fast Travel 01",
        0x045B: "Wolfen City - Fast Travel 03",
        0x044B: "Wolfen City - Fast Travel 04",
    },
    "The Fortress": {
        0x02D1: "The Fortress - Fast Travel 01",
    },
}
FAST_TRAVEL_KEY_TO_ZONES = {}
for _zone, _rows in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items():
    for _key in _rows:
        FAST_TRAVEL_KEY_TO_ZONES.setdefault(_key, []).append(_zone)
FAST_TRAVEL_LOCATION_ZONES = {
    _name: _zone
    for _zone, _rows in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items()
    for _name in _rows.values()
}

# Re-enable the later-confirmed Flying Forest Rune.
_flying_rune_item = "Progressive Rune: Flying Forest Rune"
if _flying_rune_item not in ITEM_RUNES:
    ITEM_RUNES = tuple(ITEM_RUNES) + (_flying_rune_item,)
ITEM_RUNE_SCENARIO_VARS = dict(ITEM_RUNE_SCENARIO_VARS)
ITEM_RUNE_SCENARIO_VARS[_flying_rune_item] = 0x004254E4
ITEM_PROGRESSION_COUNTS = dict(ITEM_PROGRESSION_COUNTS)
ITEM_PROGRESSION_COUNTS[_flying_rune_item] = 1

# Safe AP checks whose natural state can be validated independently.
SPECIAL_LOCATION_CONDITIONS = dict(SPECIAL_LOCATION_CONDITIONS)
SPECIAL_LOCATION_ZONES = dict(SPECIAL_LOCATION_ZONES)
SPECIAL_LOCATION_CONDITIONS.update({
    "Flying Forest - Flying Forest's Rune": ((0x004254E4, 2),),
    "Flying Forest - HP Upgrade": ((0x004255EC, 2),),
    "Forgotten Island - Frank Exorcised": ((0x004253F4, 1), (0x00425584, 2)),
})
SPECIAL_LOCATION_ZONES.update({
    "Flying Forest - Flying Forest's Rune": "Flying Forest",
    "Flying Forest - HP Upgrade": "Flying Forest",
    "Forgotten Island - Frank Exorcised": "Forgotten Island",
})

# Item->location correspondence used only to prevent AP-delivered rune writes
# from self-triggering their own LocationCheck.
ITEM_TO_SPECIAL_LOCATION = {
    "Progressive Rune: Flying Forest Rune": "Flying Forest - Flying Forest's Rune",
    "Progressive Rune: Root's Rune": "The Root - Root's Rune",
    "Progressive Rune: Hunter's Domain Rune": "Hunters Domain - Hunter's Domain's Rune",
    "Progressive Rune: Quarry's Rune": "The Quarry - Quarry's Rune",
    "Progressive Rune: Air Post Rune": "The Air Post - Air Post's Rune",
    "Progressive Rune: Forgotten Island Rune": "Forgotten Island - Forgotten Island's Rune",
}

# Debug-only probes: NEVER send LocationChecks. They prove discovered addresses
# during the natural run while avoiding self-trigger loops from AP item writes.
DEBUG_VALIDATION_PROBES = {
    "Blue Egg": {"address": 0x004253EC, "target": 1},
    "Magic Bouncers": {"address": 0x0042540C, "target": 1},
    "Climbing Gloves": {"address": 0x00425414, "target": 1},
    "Boomy Type": {"address": 0x0042541C},
    "Bracelet Bitfield": {"address": 0x00425424},
    "Magic Regeneration": {"address": 0x00425434, "target": 1},
    "Jamgut Birdcall": {"address": 0x0042543C, "target": 1},
    "Telescope": {"address": 0x00425444, "target": 1},
    "Receptacle": {"address": 0x0042544C, "target": 1},
    "Board Level": {"address": 0x00425454},
    "Magic Gauge Level": {"address": 0x0042545C},
    "Life Gauge": {"address": 0x00425474},
    "Flying Forest Rune": {"address": 0x004254E4, "target": 2},
    "Root Rune": {"address": 0x004254B4, "target": 2},
    "Hunter's Domain Rune": {"address": 0x0042551C, "target": 2},
    "Quarry Rune": {"address": 0x0042554C, "target": 2},
    "Air Post Rune": {"address": 0x00425574, "target": 2},
    "Forgotten Island Rune": {"address": 0x00425594, "target": 2},
    "Hunters Domain Map Backing (volatile)": {"address": 0x006F53D4, "target": 0},
}

# Append validation locations without changing IDs already used by 0.7.2.
LOCATION_NAME_TO_ID = dict(LOCATION_NAME_TO_ID)
LOCATION_NAME_TO_ZONE = dict(LOCATION_NAME_TO_ZONE)
_next_location_id = max(LOCATION_NAME_TO_ID.values()) + 1
_new_location_zones = dict(FAST_TRAVEL_LOCATION_ZONES)
_new_location_zones.update(SPECIAL_LOCATION_ZONES)
for _name, _zone in _new_location_zones.items():
    if _name not in LOCATION_NAME_TO_ID:
        LOCATION_NAME_TO_ID[_name] = _next_location_id
        _next_location_id += 1
    LOCATION_NAME_TO_ZONE[_name] = _zone

LOCATION_NAMES_BY_ZONE = {
    _zone: tuple(_name for _name in LOCATION_NAME_TO_ID if LOCATION_NAME_TO_ZONE.get(_name) == _zone)
    for _zone in ZONE_ORDER
}


# ============================================================================
# 0.7.3 HOTFIX 2026-10-04 — USER MANUAL ORDER + INVENTORY/SHOP VALIDATION
# Location/item IDs intentionally unchanged for seed compatibility.
# ============================================================================
WOLFEN_ZONE_KEY_TO_LOCATION = {'Nativs City': {984: 'Nativs City - Wolfen 01'}, 'Flying Forest': {2335: 'Flying Forest - Wolfen 01', 2688: 'Flying Forest - Wolfen 02', 2342: 'Flying Forest - Wolfen 03', 6134: 'Flying Forest - Wolfen 04', 5272: 'Flying Forest - Wolfen 05', 5456: 'Flying Forest - Wolfen 06', 5454: 'Flying Forest - Wolfen 07', 5455: 'Flying Forest - Wolfen 08', 2260: 'Flying Forest - Wolfen 09', 2297: 'Flying Forest - Wolfen 10', 3235: 'Flying Forest - Wolfen 11', 2351: 'Flying Forest - Wolfen 12', 3237: 'Flying Forest - Wolfen 13', 2398: 'Flying Forest - Wolfen 14', 4672: 'Flying Forest - Wolfen 15', 3270: 'Flying Forest - Wolfen 16', 2354: 'Flying Forest - Wolfen 17', 3210: 'Flying Forest - Wolfen 18', 2656: 'Flying Forest - Wolfen 19', 2462: 'Flying Forest - Wolfen 20', 7077: 'Flying Forest - Wolfen 21', 3112: 'Flying Forest - Wolfen 22', 2453: 'Flying Forest - Wolfen 23', 2451: 'Flying Forest - Wolfen 24', 2689: 'Flying Forest - Wolfen 25', 2727: 'Flying Forest - Wolfen 26', 2726: 'Flying Forest - Wolfen 27', 2828: 'Flying Forest - Wolfen 28', 2621: 'Flying Forest - Wolfen 29', 2614: 'Flying Forest - Wolfen 30', 2616: 'Flying Forest - Wolfen 31', 2620: 'Flying Forest - Wolfen 32', 2618: 'Flying Forest - Wolfen 33', 2619: 'Flying Forest - Wolfen 34', 2622: 'Flying Forest - Wolfen 35', 2617: 'Flying Forest - Wolfen 36', 2615: 'Flying Forest - Wolfen 37'}, 'Hunters Domain': {3258: 'Hunters Domain - Wolfen 01', 3260: 'Hunters Domain - Wolfen 02', 3285: 'Hunters Domain - Wolfen 03', 2496: 'Hunters Domain - Wolfen 04', 3255: 'Hunters Domain - Wolfen 05', 3604: 'Hunters Domain - Wolfen 06', 2266: 'Hunters Domain - Wolfen 07', 3593: 'Hunters Domain - Wolfen 08', 3601: 'Hunters Domain - Wolfen 09', 10824: 'Hunters Domain - Wolfen 10', 3366: 'Hunters Domain - Wolfen 11', 3368: 'Hunters Domain - Wolfen 12', 3554: 'Hunters Domain - Wolfen 13', 3553: 'Hunters Domain - Wolfen 14', 3555: 'Hunters Domain - Wolfen 15', 8250: 'Hunters Domain - Wolfen 16', 10794: 'Hunters Domain - Wolfen 17', 10157: 'Hunters Domain - Wolfen 18', 11224: 'Hunters Domain - Wolfen 19', 8747: 'Hunters Domain - Wolfen 20', 3775: 'Hunters Domain - Wolfen 21', 3776: 'Hunters Domain - Wolfen 22', 3941: 'Hunters Domain - Wolfen 23', 3934: 'Hunters Domain - Wolfen 24', 3936: 'Hunters Domain - Wolfen 25', 10312: 'Hunters Domain - Wolfen 26', 10313: 'Hunters Domain - Wolfen 27', 10804: 'Hunters Domain - Wolfen 28', 10797: 'Hunters Domain - Wolfen 29', 11444: 'Hunters Domain - Wolfen 30', 11443: 'Hunters Domain - Wolfen 31', 10349: 'Hunters Domain - Wolfen 32', 10485: 'Hunters Domain - Wolfen 33', 11474: 'Hunters Domain - Wolfen 34', 11424: 'Hunters Domain - Wolfen 35', 3469: 'Hunters Domain - Wolfen 36', 3466: 'Hunters Domain - Wolfen 37', 3467: 'Hunters Domain - Wolfen 38', 3465: 'Hunters Domain - Wolfen 39', 6320: 'Hunters Domain - Wolfen 40', 10978: 'Hunters Domain - Wolfen 41', 8743: 'Hunters Domain - Wolfen 42', 9133: 'Hunters Domain - Wolfen 43', 10610: 'Hunters Domain - Wolfen 44', 1744: 'Hunters Domain - Wolfen 45', 1742: 'Hunters Domain - Wolfen 46'}, 'Wind Tower': {8330: 'Wind Tower - Wolfen 01', 1885: 'Wind Tower - Wolfen 02'}, 'The Quarry': {10602: 'The Quarry - Wolfen 01', 1130: 'The Quarry - Wolfen 02', 5999: 'The Quarry - Wolfen 03', 6010: 'The Quarry - Wolfen 04', 1162: 'The Quarry - Wolfen 05', 1142: 'The Quarry - Wolfen 06', 1143: 'The Quarry - Wolfen 07', 9644: 'The Quarry - Wolfen 08', 9646: 'The Quarry - Wolfen 09', 9645: 'The Quarry - Wolfen 10', 9466: 'The Quarry - Wolfen 11', 9437: 'The Quarry - Wolfen 12', 9436: 'The Quarry - Wolfen 13', 1429: 'The Quarry - Wolfen 14', 823: 'The Quarry - Wolfen 15', 4232: 'The Quarry - Wolfen 16', 9721: 'The Quarry - Wolfen 17', 1437: 'The Quarry - Wolfen 18', 6017: 'The Quarry - Wolfen 19', 9392: 'The Quarry - Wolfen 20', 9394: 'The Quarry - Wolfen 21', 3868: 'The Quarry - Wolfen 22', 3267: 'The Quarry - Wolfen 23', 2556: 'The Quarry - Wolfen 24', 9339: 'The Quarry - Wolfen 25', 6526: 'The Quarry - Wolfen 26', 6527: 'The Quarry - Wolfen 27', 6078: 'The Quarry - Wolfen 28', 6096: 'The Quarry - Wolfen 29', 6079: 'The Quarry - Wolfen 30', 6093: 'The Quarry - Wolfen 31'}, 'Amber Quarry': {9845: 'Amber Quarry - Wolfen 01', 9843: 'Amber Quarry - Wolfen 02', 9842: 'Amber Quarry - Wolfen 03', 9988: 'Amber Quarry - Wolfen 04', 9989: 'Amber Quarry - Wolfen 05', 9841: 'Amber Quarry - Wolfen 06', 7569: 'Amber Quarry - Wolfen 07', 9511: 'Amber Quarry - Wolfen 08', 9528: 'Amber Quarry - Wolfen 09', 9538: 'Amber Quarry - Wolfen 10', 9513: 'Amber Quarry - Wolfen 11', 9518: 'Amber Quarry - Wolfen 12', 9515: 'Amber Quarry - Wolfen 13', 9516: 'Amber Quarry - Wolfen 14'}, 'The Root': {3486: 'The Root - Wolfen 01', 336: 'The Root - Wolfen 02', 331: 'The Root - Wolfen 03', 330: 'The Root - Wolfen 04', 312: 'The Root - Wolfen 05', 3732: 'The Root - Wolfen 06', 3731: 'The Root - Wolfen 07'}, 'The Air Post': {9940: 'The Air Post - Wolfen 01', 9943: 'The Air Post - Wolfen 02', 1357: 'The Air Post - Wolfen 03', 1912: 'The Air Post - Wolfen 04', 8421: 'The Air Post - Wolfen 05', 7285: 'The Air Post - Wolfen 06', 9944: 'The Air Post - Wolfen 07', 1327: 'The Air Post - Wolfen 08', 8758: 'The Air Post - Wolfen 09', 10078: 'The Air Post - Wolfen 10', 10079: 'The Air Post - Wolfen 11', 4432: 'The Air Post - Wolfen 12', 4433: 'The Air Post - Wolfen 13', 1449: 'The Air Post - Wolfen 14', 10403: 'The Air Post - Wolfen 15', 11391: 'The Air Post - Wolfen 16', 917: 'The Air Post - Wolfen 17', 1034: 'The Air Post - Wolfen 18', 1010: 'The Air Post - Wolfen 19', 11389: 'The Air Post - Wolfen 20', 11751: 'The Air Post - Wolfen 21', 11393: 'The Air Post - Wolfen 22', 4621: 'The Air Post - Wolfen 23', 4624: 'The Air Post - Wolfen 24', 4627: 'The Air Post - Wolfen 25', 4622: 'The Air Post - Wolfen 26', 1518: 'The Air Post - Wolfen 27', 7445: 'The Air Post - Wolfen 28', 9817: 'The Air Post - Wolfen 29', 9801: 'The Air Post - Wolfen 30', 418: 'The Air Post - Wolfen 31', 420: 'The Air Post - Wolfen 32', 430: 'The Air Post - Wolfen 33', 7602: 'The Air Post - Wolfen 34', 9398: 'The Air Post - Wolfen 35', 7795: 'The Air Post - Wolfen 36', 7792: 'The Air Post - Wolfen 37', 7791: 'The Air Post - Wolfen 38', 7793: 'The Air Post - Wolfen 39', 7790: 'The Air Post - Wolfen 40', 7794: 'The Air Post - Wolfen 41', 4756: 'The Air Post - Wolfen 42', 4757: 'The Air Post - Wolfen 43', 4755: 'The Air Post - Wolfen 44', 4758: 'The Air Post - Wolfen 45', 4754: 'The Air Post - Wolfen 46', 4759: 'The Air Post - Wolfen 47', 646: 'The Air Post - Wolfen 48', 9598: 'The Air Post - Wolfen 49', 9597: 'The Air Post - Wolfen 50', 9600: 'The Air Post - Wolfen 51', 10613: 'The Air Post - Wolfen 52', 9856: 'The Air Post - Wolfen 53', 10067: 'The Air Post - Wolfen 54', 9946: 'The Air Post - Wolfen 55', 9949: 'The Air Post - Wolfen 56', 9950: 'The Air Post - Wolfen 57', 10380: 'The Air Post - Wolfen 58', 9204: 'The Air Post - Wolfen 59', 9203: 'The Air Post - Wolfen 60', 9595: 'The Air Post - Wolfen 61'}, 'Forgotten Island': {2054: 'Forgotten Island - Wolfen 01', 2084: 'Forgotten Island - Wolfen 02', 2102: 'Forgotten Island - Wolfen 03', 6811: 'Forgotten Island - Wolfen 04', 5060: 'Forgotten Island - Wolfen 05', 5059: 'Forgotten Island - Wolfen 06', 6215: 'Forgotten Island - Wolfen 07', 4944: 'Forgotten Island - Wolfen 08'}, 'Wolfen City': {2688: 'Wolfen City - Wolfen 01', 1434: 'Wolfen City - Wolfen 02', 1443: 'Wolfen City - Wolfen 03', 1422: 'Wolfen City - Wolfen 04', 494: 'Wolfen City - Wolfen 05', 3678: 'Wolfen City - Wolfen 06', 3677: 'Wolfen City - Wolfen 07', 1750: 'Wolfen City - Wolfen 08', 1680: 'Wolfen City - Wolfen 09', 3734: 'Wolfen City - Wolfen 10', 807: 'Wolfen City - Wolfen 11', 1652: 'Wolfen City - Wolfen 12', 3733: 'Wolfen City - Wolfen 13', 3687: 'Wolfen City - Wolfen 14', 778: 'Wolfen City - Wolfen 15', 1641: 'Wolfen City - Wolfen 16', 3699: 'Wolfen City - Wolfen 17', 1822: 'Wolfen City - Wolfen 18', 1787: 'Wolfen City - Wolfen 19', 752: 'Wolfen City - Wolfen 20', 1374: 'Wolfen City - Wolfen 21', 770: 'Wolfen City - Wolfen 22', 771: 'Wolfen City - Wolfen 23', 3791: 'Wolfen City - Wolfen 24', 3761: 'Wolfen City - Wolfen 25', 3762: 'Wolfen City - Wolfen 26', 2333: 'Wolfen City - Wolfen 27', 2341: 'Wolfen City - Wolfen 28', 2335: 'Wolfen City - Wolfen 29', 2337: 'Wolfen City - Wolfen 30', 2339: 'Wolfen City - Wolfen 31', 1842: 'Wolfen City - Wolfen 32', 2004: 'Wolfen City - Wolfen 33', 1998: 'Wolfen City - Wolfen 34', 1999: 'Wolfen City - Wolfen 35', 1989: 'Wolfen City - Wolfen 36', 1267: 'Wolfen City - Wolfen 37', 1268: 'Wolfen City - Wolfen 38', 1270: 'Wolfen City - Wolfen 39', 1269: 'Wolfen City - Wolfen 40'}, 'The Fortress': {1133: 'The Fortress - Wolfen 01', 1126: 'The Fortress - Wolfen 02', 1134: 'The Fortress - Wolfen 03', 1128: 'The Fortress - Wolfen 05', 1147: 'The Fortress - Wolfen 06', 1125: 'The Fortress - Wolfen 07', 1132: 'The Fortress - Wolfen 08', 1122: 'The Fortress - Wolfen 09', 1121: 'The Fortress - Wolfen 10', 1129: 'The Fortress - Wolfen 11', 1131: 'The Fortress - Wolfen 12', 1124: 'The Fortress - Wolfen 13'}}
WOLFEN_LOCATIONS_BY_ZONE = {'Nativs City': ('Nativs City - Wolfen 01',), 'Flying Forest': ('Flying Forest - Wolfen 01', 'Flying Forest - Wolfen 02', 'Flying Forest - Wolfen 03', 'Flying Forest - Wolfen 04', 'Flying Forest - Wolfen 05', 'Flying Forest - Wolfen 06', 'Flying Forest - Wolfen 07', 'Flying Forest - Wolfen 08', 'Flying Forest - Wolfen 09', 'Flying Forest - Wolfen 10', 'Flying Forest - Wolfen 11', 'Flying Forest - Wolfen 12', 'Flying Forest - Wolfen 13', 'Flying Forest - Wolfen 14', 'Flying Forest - Wolfen 15', 'Flying Forest - Wolfen 16', 'Flying Forest - Wolfen 17', 'Flying Forest - Wolfen 18', 'Flying Forest - Wolfen 19', 'Flying Forest - Wolfen 20', 'Flying Forest - Wolfen 21', 'Flying Forest - Wolfen 22', 'Flying Forest - Wolfen 23', 'Flying Forest - Wolfen 24', 'Flying Forest - Wolfen 25', 'Flying Forest - Wolfen 26', 'Flying Forest - Wolfen 27', 'Flying Forest - Wolfen 28', 'Flying Forest - Wolfen 29', 'Flying Forest - Wolfen 30', 'Flying Forest - Wolfen 31', 'Flying Forest - Wolfen 32', 'Flying Forest - Wolfen 33', 'Flying Forest - Wolfen 34', 'Flying Forest - Wolfen 35', 'Flying Forest - Wolfen 36', 'Flying Forest - Wolfen 37'), 'Hunters Domain': ('Hunters Domain - Wolfen 01', 'Hunters Domain - Wolfen 02', 'Hunters Domain - Wolfen 03', 'Hunters Domain - Wolfen 04', 'Hunters Domain - Wolfen 05', 'Hunters Domain - Wolfen 06', 'Hunters Domain - Wolfen 07', 'Hunters Domain - Wolfen 08', 'Hunters Domain - Wolfen 09', 'Hunters Domain - Wolfen 10', 'Hunters Domain - Wolfen 11', 'Hunters Domain - Wolfen 12', 'Hunters Domain - Wolfen 13', 'Hunters Domain - Wolfen 14', 'Hunters Domain - Wolfen 15', 'Hunters Domain - Wolfen 16', 'Hunters Domain - Wolfen 17', 'Hunters Domain - Wolfen 18', 'Hunters Domain - Wolfen 19', 'Hunters Domain - Wolfen 20', 'Hunters Domain - Wolfen 21', 'Hunters Domain - Wolfen 22', 'Hunters Domain - Wolfen 23', 'Hunters Domain - Wolfen 24', 'Hunters Domain - Wolfen 25', 'Hunters Domain - Wolfen 26', 'Hunters Domain - Wolfen 27', 'Hunters Domain - Wolfen 28', 'Hunters Domain - Wolfen 29', 'Hunters Domain - Wolfen 30', 'Hunters Domain - Wolfen 31', 'Hunters Domain - Wolfen 32', 'Hunters Domain - Wolfen 33', 'Hunters Domain - Wolfen 34', 'Hunters Domain - Wolfen 35', 'Hunters Domain - Wolfen 36', 'Hunters Domain - Wolfen 37', 'Hunters Domain - Wolfen 38', 'Hunters Domain - Wolfen 39', 'Hunters Domain - Wolfen 40', 'Hunters Domain - Wolfen 41', 'Hunters Domain - Wolfen 42', 'Hunters Domain - Wolfen 43', 'Hunters Domain - Wolfen 44', 'Hunters Domain - Wolfen 45', 'Hunters Domain - Wolfen 46'), 'Wind Tower': ('Wind Tower - Wolfen 01', 'Wind Tower - Wolfen 02'), 'The Quarry': ('The Quarry - Wolfen 01', 'The Quarry - Wolfen 02', 'The Quarry - Wolfen 03', 'The Quarry - Wolfen 04', 'The Quarry - Wolfen 05', 'The Quarry - Wolfen 06', 'The Quarry - Wolfen 07', 'The Quarry - Wolfen 08', 'The Quarry - Wolfen 09', 'The Quarry - Wolfen 10', 'The Quarry - Wolfen 11', 'The Quarry - Wolfen 12', 'The Quarry - Wolfen 13', 'The Quarry - Wolfen 14', 'The Quarry - Wolfen 15', 'The Quarry - Wolfen 16', 'The Quarry - Wolfen 17', 'The Quarry - Wolfen 18', 'The Quarry - Wolfen 19', 'The Quarry - Wolfen 20', 'The Quarry - Wolfen 21', 'The Quarry - Wolfen 22', 'The Quarry - Wolfen 23', 'The Quarry - Wolfen 24', 'The Quarry - Wolfen 25', 'The Quarry - Wolfen 26', 'The Quarry - Wolfen 27', 'The Quarry - Wolfen 28', 'The Quarry - Wolfen 29', 'The Quarry - Wolfen 30', 'The Quarry - Wolfen 31'), 'Amber Quarry': ('Amber Quarry - Wolfen 01', 'Amber Quarry - Wolfen 02', 'Amber Quarry - Wolfen 03', 'Amber Quarry - Wolfen 04', 'Amber Quarry - Wolfen 05', 'Amber Quarry - Wolfen 06', 'Amber Quarry - Wolfen 07', 'Amber Quarry - Wolfen 08', 'Amber Quarry - Wolfen 09', 'Amber Quarry - Wolfen 10', 'Amber Quarry - Wolfen 11', 'Amber Quarry - Wolfen 12', 'Amber Quarry - Wolfen 13', 'Amber Quarry - Wolfen 14'), 'The Root': ('The Root - Wolfen 01', 'The Root - Wolfen 02', 'The Root - Wolfen 03', 'The Root - Wolfen 04', 'The Root - Wolfen 05', 'The Root - Wolfen 06', 'The Root - Wolfen 07'), 'The Air Post': ('The Air Post - Wolfen 01', 'The Air Post - Wolfen 02', 'The Air Post - Wolfen 03', 'The Air Post - Wolfen 04', 'The Air Post - Wolfen 05', 'The Air Post - Wolfen 06', 'The Air Post - Wolfen 07', 'The Air Post - Wolfen 08', 'The Air Post - Wolfen 09', 'The Air Post - Wolfen 10', 'The Air Post - Wolfen 11', 'The Air Post - Wolfen 12', 'The Air Post - Wolfen 13', 'The Air Post - Wolfen 14', 'The Air Post - Wolfen 15', 'The Air Post - Wolfen 16', 'The Air Post - Wolfen 17', 'The Air Post - Wolfen 18', 'The Air Post - Wolfen 19', 'The Air Post - Wolfen 20', 'The Air Post - Wolfen 21', 'The Air Post - Wolfen 22', 'The Air Post - Wolfen 23', 'The Air Post - Wolfen 24', 'The Air Post - Wolfen 25', 'The Air Post - Wolfen 26', 'The Air Post - Wolfen 27', 'The Air Post - Wolfen 28', 'The Air Post - Wolfen 29', 'The Air Post - Wolfen 30', 'The Air Post - Wolfen 31', 'The Air Post - Wolfen 32', 'The Air Post - Wolfen 33', 'The Air Post - Wolfen 34', 'The Air Post - Wolfen 35', 'The Air Post - Wolfen 36', 'The Air Post - Wolfen 37', 'The Air Post - Wolfen 38', 'The Air Post - Wolfen 39', 'The Air Post - Wolfen 40', 'The Air Post - Wolfen 41', 'The Air Post - Wolfen 42', 'The Air Post - Wolfen 43', 'The Air Post - Wolfen 44', 'The Air Post - Wolfen 45', 'The Air Post - Wolfen 46', 'The Air Post - Wolfen 47', 'The Air Post - Wolfen 48', 'The Air Post - Wolfen 49', 'The Air Post - Wolfen 50', 'The Air Post - Wolfen 51', 'The Air Post - Wolfen 52', 'The Air Post - Wolfen 53', 'The Air Post - Wolfen 54', 'The Air Post - Wolfen 55', 'The Air Post - Wolfen 56', 'The Air Post - Wolfen 57', 'The Air Post - Wolfen 58', 'The Air Post - Wolfen 59', 'The Air Post - Wolfen 60', 'The Air Post - Wolfen 61'), 'Forgotten Island': ('Forgotten Island - Wolfen 01', 'Forgotten Island - Wolfen 02', 'Forgotten Island - Wolfen 03', 'Forgotten Island - Wolfen 04', 'Forgotten Island - Wolfen 05', 'Forgotten Island - Wolfen 06', 'Forgotten Island - Wolfen 07', 'Forgotten Island - Wolfen 08'), 'Wolfen City': ('Wolfen City - Wolfen 01', 'Wolfen City - Wolfen 02', 'Wolfen City - Wolfen 03', 'Wolfen City - Wolfen 04', 'Wolfen City - Wolfen 05', 'Wolfen City - Wolfen 06', 'Wolfen City - Wolfen 07', 'Wolfen City - Wolfen 08', 'Wolfen City - Wolfen 09', 'Wolfen City - Wolfen 10', 'Wolfen City - Wolfen 11', 'Wolfen City - Wolfen 12', 'Wolfen City - Wolfen 13', 'Wolfen City - Wolfen 14', 'Wolfen City - Wolfen 15', 'Wolfen City - Wolfen 16', 'Wolfen City - Wolfen 17', 'Wolfen City - Wolfen 18', 'Wolfen City - Wolfen 19', 'Wolfen City - Wolfen 20', 'Wolfen City - Wolfen 21', 'Wolfen City - Wolfen 22', 'Wolfen City - Wolfen 23', 'Wolfen City - Wolfen 24', 'Wolfen City - Wolfen 25', 'Wolfen City - Wolfen 26', 'Wolfen City - Wolfen 27', 'Wolfen City - Wolfen 28', 'Wolfen City - Wolfen 29', 'Wolfen City - Wolfen 30', 'Wolfen City - Wolfen 31', 'Wolfen City - Wolfen 32', 'Wolfen City - Wolfen 33', 'Wolfen City - Wolfen 34', 'Wolfen City - Wolfen 35', 'Wolfen City - Wolfen 36', 'Wolfen City - Wolfen 37', 'Wolfen City - Wolfen 38', 'Wolfen City - Wolfen 39', 'Wolfen City - Wolfen 40'), 'The Fortress': ('The Fortress - Wolfen 01', 'The Fortress - Wolfen 02', 'The Fortress - Wolfen 03', 'The Fortress - Wolfen 04', 'The Fortress - Wolfen 05', 'The Fortress - Wolfen 06', 'The Fortress - Wolfen 07', 'The Fortress - Wolfen 08', 'The Fortress - Wolfen 09', 'The Fortress - Wolfen 10', 'The Fortress - Wolfen 11', 'The Fortress - Wolfen 12', 'The Fortress - Wolfen 13')}
WOLFEN_KEY_TO_ZONES = {984: ['Nativs City'], 2335: ['Flying Forest', 'Wolfen City'], 2688: ['Flying Forest', 'Wolfen City'], 2342: ['Flying Forest'], 6134: ['Flying Forest'], 5272: ['Flying Forest'], 5456: ['Flying Forest'], 5454: ['Flying Forest'], 5455: ['Flying Forest'], 2260: ['Flying Forest'], 2297: ['Flying Forest'], 3235: ['Flying Forest'], 2351: ['Flying Forest'], 3237: ['Flying Forest'], 2398: ['Flying Forest'], 4672: ['Flying Forest'], 3270: ['Flying Forest'], 2354: ['Flying Forest'], 3210: ['Flying Forest'], 2656: ['Flying Forest'], 2462: ['Flying Forest'], 7077: ['Flying Forest'], 3112: ['Flying Forest'], 2453: ['Flying Forest'], 2451: ['Flying Forest'], 2689: ['Flying Forest'], 2727: ['Flying Forest'], 2726: ['Flying Forest'], 2828: ['Flying Forest'], 2621: ['Flying Forest'], 2614: ['Flying Forest'], 2616: ['Flying Forest'], 2620: ['Flying Forest'], 2618: ['Flying Forest'], 2619: ['Flying Forest'], 2622: ['Flying Forest'], 2617: ['Flying Forest'], 2615: ['Flying Forest'], 3258: ['Hunters Domain'], 3260: ['Hunters Domain'], 3285: ['Hunters Domain'], 2496: ['Hunters Domain'], 3255: ['Hunters Domain'], 3604: ['Hunters Domain'], 2266: ['Hunters Domain'], 3593: ['Hunters Domain'], 3601: ['Hunters Domain'], 10824: ['Hunters Domain'], 3366: ['Hunters Domain'], 3368: ['Hunters Domain'], 3554: ['Hunters Domain'], 3553: ['Hunters Domain'], 3555: ['Hunters Domain'], 8250: ['Hunters Domain'], 10794: ['Hunters Domain'], 10157: ['Hunters Domain'], 11224: ['Hunters Domain'], 8747: ['Hunters Domain'], 3775: ['Hunters Domain'], 3776: ['Hunters Domain'], 3941: ['Hunters Domain'], 3934: ['Hunters Domain'], 3936: ['Hunters Domain'], 10312: ['Hunters Domain'], 10313: ['Hunters Domain'], 10804: ['Hunters Domain'], 10797: ['Hunters Domain'], 11444: ['Hunters Domain'], 11443: ['Hunters Domain'], 10349: ['Hunters Domain'], 10485: ['Hunters Domain'], 11474: ['Hunters Domain'], 11424: ['Hunters Domain'], 3469: ['Hunters Domain'], 3466: ['Hunters Domain'], 3467: ['Hunters Domain'], 3465: ['Hunters Domain'], 6320: ['Hunters Domain'], 10978: ['Hunters Domain'], 8743: ['Hunters Domain'], 9133: ['Hunters Domain'], 10610: ['Hunters Domain'], 1744: ['Hunters Domain'], 1742: ['Hunters Domain'], 8330: ['Wind Tower'], 1885: ['Wind Tower'], 10602: ['The Quarry'], 1130: ['The Quarry'], 5999: ['The Quarry'], 6010: ['The Quarry'], 1162: ['The Quarry'], 1142: ['The Quarry'], 1143: ['The Quarry'], 9644: ['The Quarry'], 9646: ['The Quarry'], 9645: ['The Quarry'], 9466: ['The Quarry'], 9437: ['The Quarry'], 9436: ['The Quarry'], 1429: ['The Quarry'], 823: ['The Quarry'], 4232: ['The Quarry'], 9721: ['The Quarry'], 1437: ['The Quarry'], 6017: ['The Quarry'], 9392: ['The Quarry'], 9394: ['The Quarry'], 3868: ['The Quarry'], 3267: ['The Quarry'], 2556: ['The Quarry'], 9339: ['The Quarry'], 6526: ['The Quarry'], 6527: ['The Quarry'], 6078: ['The Quarry'], 6096: ['The Quarry'], 6079: ['The Quarry'], 6093: ['The Quarry'], 9845: ['Amber Quarry'], 9843: ['Amber Quarry'], 9842: ['Amber Quarry'], 9988: ['Amber Quarry'], 9989: ['Amber Quarry'], 9841: ['Amber Quarry'], 7569: ['Amber Quarry'], 9511: ['Amber Quarry'], 9528: ['Amber Quarry'], 9538: ['Amber Quarry'], 9513: ['Amber Quarry'], 9518: ['Amber Quarry'], 9515: ['Amber Quarry'], 9516: ['Amber Quarry'], 3486: ['The Root'], 336: ['The Root'], 331: ['The Root'], 330: ['The Root'], 312: ['The Root'], 3732: ['The Root'], 3731: ['The Root'], 9940: ['The Air Post'], 9943: ['The Air Post'], 1357: ['The Air Post'], 1912: ['The Air Post'], 8421: ['The Air Post'], 7285: ['The Air Post'], 9944: ['The Air Post'], 1327: ['The Air Post'], 8758: ['The Air Post'], 10078: ['The Air Post'], 10079: ['The Air Post'], 4432: ['The Air Post'], 4433: ['The Air Post'], 1449: ['The Air Post'], 10403: ['The Air Post'], 11391: ['The Air Post'], 917: ['The Air Post'], 1034: ['The Air Post'], 1010: ['The Air Post'], 11389: ['The Air Post'], 11751: ['The Air Post'], 11393: ['The Air Post'], 4621: ['The Air Post'], 4624: ['The Air Post'], 4627: ['The Air Post'], 4622: ['The Air Post'], 1518: ['The Air Post'], 7445: ['The Air Post'], 9817: ['The Air Post'], 9801: ['The Air Post'], 418: ['The Air Post'], 420: ['The Air Post'], 430: ['The Air Post'], 7602: ['The Air Post'], 9398: ['The Air Post'], 7795: ['The Air Post'], 7792: ['The Air Post'], 7791: ['The Air Post'], 7793: ['The Air Post'], 7790: ['The Air Post'], 7794: ['The Air Post'], 4756: ['The Air Post'], 4757: ['The Air Post'], 4755: ['The Air Post'], 4758: ['The Air Post'], 4754: ['The Air Post'], 4759: ['The Air Post'], 646: ['The Air Post'], 9598: ['The Air Post'], 9597: ['The Air Post'], 9600: ['The Air Post'], 10613: ['The Air Post'], 9856: ['The Air Post'], 10067: ['The Air Post'], 9946: ['The Air Post'], 9949: ['The Air Post'], 9950: ['The Air Post'], 10380: ['The Air Post'], 9204: ['The Air Post'], 9203: ['The Air Post'], 9595: ['The Air Post'], 2054: ['Forgotten Island'], 2084: ['Forgotten Island'], 2102: ['Forgotten Island'], 6811: ['Forgotten Island'], 5060: ['Forgotten Island'], 5059: ['Forgotten Island'], 6215: ['Forgotten Island'], 4944: ['Forgotten Island'], 1434: ['Wolfen City'], 1443: ['Wolfen City'], 1422: ['Wolfen City'], 494: ['Wolfen City'], 3678: ['Wolfen City'], 3677: ['Wolfen City'], 1750: ['Wolfen City'], 1680: ['Wolfen City'], 3734: ['Wolfen City'], 807: ['Wolfen City'], 1652: ['Wolfen City'], 3733: ['Wolfen City'], 3687: ['Wolfen City'], 778: ['Wolfen City'], 1641: ['Wolfen City'], 3699: ['Wolfen City'], 1822: ['Wolfen City'], 1787: ['Wolfen City'], 752: ['Wolfen City'], 1374: ['Wolfen City'], 770: ['Wolfen City'], 771: ['Wolfen City'], 3791: ['Wolfen City'], 3761: ['Wolfen City'], 3762: ['Wolfen City'], 2333: ['Wolfen City'], 2341: ['Wolfen City'], 2337: ['Wolfen City'], 2339: ['Wolfen City'], 1842: ['Wolfen City'], 2004: ['Wolfen City'], 1998: ['Wolfen City'], 1999: ['Wolfen City'], 1989: ['Wolfen City'], 1267: ['Wolfen City'], 1268: ['Wolfen City'], 1270: ['Wolfen City'], 1269: ['Wolfen City'], 1133: ['The Fortress'], 1126: ['The Fortress'], 1134: ['The Fortress'], 1128: ['The Fortress'], 1147: ['The Fortress'], 1125: ['The Fortress'], 1132: ['The Fortress'], 1122: ['The Fortress'], 1121: ['The Fortress'], 1129: ['The Fortress'], 1131: ['The Fortress'], 1124: ['The Fortress']}
WOLFEN_KEY_TO_LOCATION = {
    key: WOLFEN_ZONE_KEY_TO_LOCATION[zones[0]][key]
    for key, zones in WOLFEN_KEY_TO_ZONES.items()
}
WOLFEN_LOCATION_DESCRIPTIONS = {'Flying Forest - Wolfen 01': 'Validation duplicate-key reconstruction (0x091F); exact 01/02 order to confirm in live playtest.', 'Flying Forest - Wolfen 02': 'Validation duplicate-key reconstruction (0x0A80); exact 01/02 order to confirm in live playtest.', 'Flying Forest - Wolfen 03': 'Scrawny / Fists / Blue Outfit', 'Flying Forest - Wolfen 04': 'Scrawny / Fists / Blue Outfit', 'Flying Forest - Wolfen 05': 'Scrawny / Spiked Club / Blue Outfit', 'Flying Forest - Wolfen 06': 'Wolfen on cannon', 'Flying Forest - Wolfen 07': 'Wolfen / Fists / Blue Outfit', 'Flying Forest - Wolfen 08': 'Wolfen / Fists / Yellow Outfit', 'Hunters Domain - Wolfen 11': 'Gun / Blue Outfit', 'Hunters Domain - Wolfen 12': 'Gun / Blue Outfit', 'Hunters Domain - Wolfen 13': 'Club / Blue Outfit', 'Hunters Domain - Wolfen 14': 'Fists / Black Outfit', 'Hunters Domain - Wolfen 15': 'Fists / Black Outfit', 'Hunters Domain - Wolfen 16': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 17': 'Scrawny / Sniper / Blue Outfit', 'Hunters Domain - Wolfen 18': 'Scrawny / Sniper / Blue Outfit', 'Hunters Domain - Wolfen 19': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 20': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 21': 'Scrawny / Club / Blue Outfit', 'Hunters Domain - Wolfen 22': 'Scrawny / Club / Blue Outfit', 'Hunters Domain - Wolfen 23': 'Scrawny / Club / Blue Outfit', 'Hunters Domain - Wolfen 24': 'Scrawny / Club / Blue Outfit', 'Hunters Domain - Wolfen 25': 'Scrawny / Club / Blue Outfit', 'Hunters Domain - Wolfen 26': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 27': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 28': 'Scrawny / Sniper / Blue Outfit', 'Hunters Domain - Wolfen 29': 'Scrawny / Sniper / Blue Outfit', 'Hunters Domain - Wolfen 30': 'Scrawny / Fists / Blue Outfit', 'Hunters Domain - Wolfen 31': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 32': 'Scrawny / Gun / Blue Outfit', 'Hunters Domain - Wolfen 33': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 34': 'Scrawny / Fists / Blue Outfit', 'Hunters Domain - Wolfen 35': 'Scrawny / Fists / Blue Outfit', 'Hunters Domain - Wolfen 36': 'Scrawny / Fists / Blue Outfit', 'Hunters Domain - Wolfen 37': 'Scrawny / Fists / Yellow Outfit', 'Hunters Domain - Wolfen 38': 'Scrawny / Fists / Yellow Outfit', 'Hunters Domain - Wolfen 39': 'Scrawny / Fists / Yellow Outfit', 'Hunters Domain - Wolfen 40': 'Scrawny / Gun / Blue Outfit', 'Hunters Domain - Wolfen 41': 'Scrawny / Sniper / Blue Outfit', 'Hunters Domain - Wolfen 42': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 43': 'Scrawny / Fists / Blue Outfit', 'Hunters Domain - Wolfen 44': 'Grunt / Fists / Blue Outfit', 'Hunters Domain - Wolfen 45': 'Scrawny / Gun / Blue Outfit', 'Hunters Domain - Wolfen 46': 'Scrawny / Gun / Blue Outfit', 'Wind Tower - Wolfen 01': 'Scrawny / Rocket Gun / Blue Outfit', 'Wind Tower - Wolfen 02': 'Scrawny / Gun / Blue Outfit', 'The Quarry - Wolfen 05': 'Scrawny / Club / Blue Outfit', 'The Quarry - Wolfen 06': 'Scrawny / Gun / Blue Outfit', 'The Quarry - Wolfen 07': 'Scrawny / Gun / Blue Outfit', 'The Quarry - Wolfen 08': 'Scrawny / Gun / Blue Outfit', 'The Quarry - Wolfen 09': 'Grunt / Fists / Blue Outfit', 'The Quarry - Wolfen 10': 'Scrawny / Fists / Yellow Outfit', 'The Quarry - Wolfen 11': 'Scrawny / Fists / Yellow Outfit', 'The Quarry - Wolfen 12': 'Scrawny / Fists / Yellow Outfit', 'The Quarry - Wolfen 13': 'Grunt / Fists / Blue Outfit', 'The Quarry - Wolfen 17': 'Grunt / Fists / Black Outfit', 'The Quarry - Wolfen 19': 'Grunt / Fists / Black Outfit', 'Amber Quarry - Wolfen 01': 'Scrawny / Fists / Blue Outfit', 'Amber Quarry - Wolfen 02': 'Scrawny / Fists / Yellow Outfit', 'Amber Quarry - Wolfen 03': 'Grunt / Fists / Black Outfit', 'Amber Quarry - Wolfen 04': 'Scrawny / Fists / Blue Outfit', 'Amber Quarry - Wolfen 05': 'Scrawny / Fists / Yellow Outfit', 'Amber Quarry - Wolfen 06': 'Grunt / Fists / Black Outfit', 'Amber Quarry - Wolfen 07': 'Scrawny / Fists / Blue Outfit', 'Amber Quarry - Wolfen 08': 'Grunt / Fists / Blue Outfit', 'Amber Quarry - Wolfen 09': 'Scrawny / Fists / Blue Outfit', 'Amber Quarry - Wolfen 10': 'Grunt / Fists / Blue Outfit', 'Amber Quarry - Wolfen 11': 'Scrawny / Sniper / Blue Outfit', 'Amber Quarry - Wolfen 12': 'Scrawny / Sniper / Blue Outfit', 'Amber Quarry - Wolfen 13': 'Scrawny / Sniper / Blue Outfit', 'Amber Quarry - Wolfen 14': 'Scrawny / Sniper / Blue Outfit', 'The Root - Wolfen 01': 'Scrawny / Rocket Gun / Blue Outfit', 'The Root - Wolfen 02': 'Scrawny / Fists / Blue Outfit', 'The Root - Wolfen 03': 'Scrawny / Gun / Blue Outfit', 'The Root - Wolfen 04': 'Scrawny / Gun / Blue Outfit', 'The Root - Wolfen 05': 'Scrawny / Gun / Blue Outfit', 'The Root - Wolfen 06': 'Scrawny / Sniper / Blue Outfit', 'The Root - Wolfen 07': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 01': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 02': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 03': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 04': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 05': 'Scrawny / Fists / Blue Outfit', 'The Air Post - Wolfen 06': 'Scrawny / Club / Blue Outfit', 'The Air Post - Wolfen 07': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 08': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 09': 'Scrawny / Club / Blue Outfit', 'The Air Post - Wolfen 10': 'Grunt / Fists / Black Outfit', 'The Air Post - Wolfen 11': 'Grunt / Club / Yellow Outfit', 'The Air Post - Wolfen 12': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 13': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 14': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 15': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 16': 'Grunt / Club / Brown Outfit', 'The Air Post - Wolfen 17': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 18': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 19': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 20': 'Grunt / Fists / Yellow Outfit', 'The Air Post - Wolfen 21': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 22': 'Grunt / Club / Yellow Outfit', 'The Air Post - Wolfen 23': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 24': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 25': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 26': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 27': 'Scrawny / Gun / Yellow Outfit', 'The Air Post - Wolfen 28': 'Scrawny / Fists / Blue Outfit', 'The Air Post - Wolfen 29': 'Grunt / Fists / Black Outfit', 'The Air Post - Wolfen 30': 'Scrawny / Rocket Gun / Blue Outfit', 'The Air Post - Wolfen 31': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 32': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 33': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 34': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 35': 'Grunt / Fists / Blue Outfit', 'The Air Post - Wolfen 36': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 37': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 38': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 39': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 40': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 41': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 42': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 43': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 44': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 45': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 46': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 47': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 48': 'Scrawny / Gun / Blue Outfit', 'The Air Post - Wolfen 49': 'Grunt / Club / Blue Outfit', 'The Air Post - Wolfen 50': 'Grunt / Club / Yellow Outfit', 'The Air Post - Wolfen 51': 'Grunt / Fists / Yellow Outfit', 'The Air Post - Wolfen 52': 'Scrawny / Rocket Gun / Blue Outfit', 'The Air Post - Wolfen 53': 'Scrawny / Rocket Gun / Blue Outfit', 'The Air Post - Wolfen 54': 'Grunt / Fists / Yellow Outfit', 'The Air Post - Wolfen 55': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 56': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 57': 'Scrawny / Sniper / Blue Outfit', 'The Air Post - Wolfen 58': 'Scrawny / Rocket Gun / Blue Outfit', 'The Air Post - Wolfen 59': 'Scrawny / Club / Blue Outfit', 'The Air Post - Wolfen 60': 'Scrawny / Club / Blue Outfit', 'The Air Post - Wolfen 61': 'Grunt / Fists / Black Outfit', 'Forgotten Island - Wolfen 04': 'Scrawny / Fists / Yellow Outfit', 'Forgotten Island - Wolfen 05': 'Grunt / Club / Yellow Outfit', 'Forgotten Island - Wolfen 06': 'Grunt / Fists / Blue Outfit', 'Forgotten Island - Wolfen 07': 'Scrawny / Rocket Gun / Yellow Outfit', 'Forgotten Island - Wolfen 08': 'Kronos / Fists / Black Outfit', 'Wolfen City - Wolfen 01': 'Scrawny / Gun / Blue Outfit', 'Wolfen City - Wolfen 02': 'Grunt / Fists / Yellow Outfit', 'Wolfen City - Wolfen 03': 'Scrawny / Fists / Blue Outfit', 'Wolfen City - Wolfen 04': 'Grunt / Fists / Yellow Outfit', 'Wolfen City - Wolfen 05': 'Scrawny / Fists / Blue Outfit', 'Wolfen City - Wolfen 06': 'Scrawny / Club / Blue Outfit', 'Wolfen City - Wolfen 07': 'Scrawny / Club / Blue Outfit', 'Wolfen City - Wolfen 08': 'Kronos / Fists / Black Outfit', 'Wolfen City - Wolfen 09': 'Grunt / Club / Blue Outfit', 'Wolfen City - Wolfen 10': 'Kronos / Fists / Black Outfit', 'Wolfen City - Wolfen 11': 'Scrawny / Gun / Yellow Outfit', 'Wolfen City - Wolfen 12': 'Grunt / Fists / Blue Outfit', 'Wolfen City - Wolfen 13': 'Scrawny / Sniper / Blue Outfit', 'Wolfen City - Wolfen 14': 'Scrawny / Sniper / Blue Outfit', 'Wolfen City - Wolfen 15': 'Scrawny / Gun / Yellow Outfit', 'Wolfen City - Wolfen 16': 'Kronos / Fists / Black Outfit', 'Wolfen City - Wolfen 17': 'Grunt / Fists / Yellow Outfit', 'Wolfen City - Wolfen 18': 'Grunt / Club / Blue Outfit', 'Wolfen City - Wolfen 19': 'Scrawny / Gun / Blue Outfit', 'Wolfen City - Wolfen 20': 'Grunt / Club / Blue Outfit', 'Wolfen City - Wolfen 21': 'Kronos / Fists / Black Outfit', 'Wolfen City - Wolfen 22': 'Scrawny / Gun / Yellow Outfit', 'Wolfen City - Wolfen 23': 'Scrawny / Gun / Yellow Outfit', 'Wolfen City - Wolfen 24': 'Scrawny / Gun / Blue Outfit', 'Wolfen City - Wolfen 25': 'Scrawny / Gun / Blue Outfit', 'Wolfen City - Wolfen 26': 'Scrawny / Gun / Blue Outfit', 'Wolfen City - Wolfen 27': 'Grunt / Fists / Blue Outfit', 'Wolfen City - Wolfen 28': 'Grunt / Fists / Blue Outfit', 'Wolfen City - Wolfen 29': 'Grunt / Fists / Blue Outfit', 'Wolfen City - Wolfen 32': 'Scrawny / Sniper / Blue Outfit', 'Wolfen City - Wolfen 33': 'Kronos / Fists / Black Outfit', 'Wolfen City - Wolfen 34': 'Scrawny / Sniper / Blue Outfit', 'Wolfen City - Wolfen 35': 'Scrawny / Sniper / Blue Outfit', 'Wolfen City - Wolfen 36': 'Scrawny / Sniper / Blue Outfit', 'Wolfen City - Wolfen 37': 'Scrawny / Fists / Blue Outfit', 'Wolfen City - Wolfen 39': 'Scrawny / Fists / Blue Outfit', 'Wolfen City - Wolfen 40': 'Scrawny / Fists / Blue Outfit', 'The Fortress - Wolfen 04': 'UNMAPPED — exact Wolfen #04 key still not found; 0x037F is Aton, not this Wolfen.'}

# White bracelet (bit 0) is owned from the start; the seven AP copies unlock
# Yellow..Gold (bits 1..7). Old test seeds containing an eighth copy are safe:
# clients cap at the full 0xFF inventory.
ITEM_PROGRESSION_COUNTS = dict(ITEM_PROGRESSION_COUNTS)
ITEM_PROGRESSION_COUNTS[ITEM_PROGRESSIVE_BRACELET] = 7

# The Hunters Domain map backing oscillates constantly and is not a useful
# debug probe. Keep the actual map LocationCheck logic separate.
DEBUG_VALIDATION_PROBES = dict(DEBUG_VALIDATION_PROBES)
DEBUG_VALIDATION_PROBES.pop("Hunters Domain Map Backing (volatile)", None)


# ============================================================================
# 0.7.3 HOTFIX2 — MANUAL AUDIT ORDER (2026-10-04)
# Same Location IDs/build string: existing 0.7.3 seeds remain compatible.
# ============================================================================
WOLFEN_ZONE_KEY_TO_LOCATION["Flying Forest"] = {2342: 'Flying Forest - Wolfen 01',
 6134: 'Flying Forest - Wolfen 02',
 5272: 'Flying Forest - Wolfen 03',
 5456: 'Flying Forest - Wolfen 04',
 5454: 'Flying Forest - Wolfen 05',
 5455: 'Flying Forest - Wolfen 06',
 2260: 'Flying Forest - Wolfen 07',
 2335: 'Flying Forest - Wolfen 08',
 2297: 'Flying Forest - Wolfen 09',
 3235: 'Flying Forest - Wolfen 10',
 3237: 'Flying Forest - Wolfen 11',
 2351: 'Flying Forest - Wolfen 12',
 2398: 'Flying Forest - Wolfen 13',
 4672: 'Flying Forest - Wolfen 14',
 3270: 'Flying Forest - Wolfen 15',
 2354: 'Flying Forest - Wolfen 16',
 3210: 'Flying Forest - Wolfen 17',
 2656: 'Flying Forest - Wolfen 18',
 2462: 'Flying Forest - Wolfen 19',
 7077: 'Flying Forest - Wolfen 20',
 3112: 'Flying Forest - Wolfen 21',
 2453: 'Flying Forest - Wolfen 22',
 2451: 'Flying Forest - Wolfen 23',
 2688: 'Flying Forest - Wolfen 24',
 2689: 'Flying Forest - Wolfen 25',
 2727: 'Flying Forest - Wolfen 26',
 2726: 'Flying Forest - Wolfen 27',
 2828: 'Flying Forest - Wolfen 28',
 2621: 'Flying Forest - Wolfen 29',
 2614: 'Flying Forest - Wolfen 30',
 2616: 'Flying Forest - Wolfen 31',
 2620: 'Flying Forest - Wolfen 32',
 2618: 'Flying Forest - Wolfen 33',
 2619: 'Flying Forest - Wolfen 34',
 2622: 'Flying Forest - Wolfen 35',
 2617: 'Flying Forest - Wolfen 36',
 2615: 'Flying Forest - Wolfen 37'}
WOLFEN_ZONE_KEY_TO_LOCATION["Hunters Domain"] = {3258: 'Hunters Domain - Wolfen 01',
 3260: 'Hunters Domain - Wolfen 02',
 2496: 'Hunters Domain - Wolfen 03',
 3285: 'Hunters Domain - Wolfen 04',
 3255: 'Hunters Domain - Wolfen 05',
 3604: 'Hunters Domain - Wolfen 06',
 2266: 'Hunters Domain - Wolfen 07',
 3601: 'Hunters Domain - Wolfen 08',
 10824: 'Hunters Domain - Wolfen 09',
 3593: 'Hunters Domain - Wolfen 10',
 3366: 'Hunters Domain - Wolfen 11',
 3368: 'Hunters Domain - Wolfen 12',
 3554: 'Hunters Domain - Wolfen 13',
 3553: 'Hunters Domain - Wolfen 14',
 3555: 'Hunters Domain - Wolfen 15',
 8250: 'Hunters Domain - Wolfen 16',
 10794: 'Hunters Domain - Wolfen 17',
 10157: 'Hunters Domain - Wolfen 18',
 11224: 'Hunters Domain - Wolfen 19',
 8747: 'Hunters Domain - Wolfen 20',
 3775: 'Hunters Domain - Wolfen 21',
 3776: 'Hunters Domain - Wolfen 22',
 3941: 'Hunters Domain - Wolfen 23',
 3934: 'Hunters Domain - Wolfen 24',
 3936: 'Hunters Domain - Wolfen 25',
 10610: 'Hunters Domain - Wolfen 26',
 1742: 'Hunters Domain - Wolfen 27',
 1744: 'Hunters Domain - Wolfen 28',
 10313: 'Hunters Domain - Wolfen 29',
 10312: 'Hunters Domain - Wolfen 30',
 10804: 'Hunters Domain - Wolfen 31',
 10797: 'Hunters Domain - Wolfen 32',
 11444: 'Hunters Domain - Wolfen 33',
 11443: 'Hunters Domain - Wolfen 34',
 10349: 'Hunters Domain - Wolfen 35',
 10485: 'Hunters Domain - Wolfen 36',
 3469: 'Hunters Domain - Wolfen 37',
 3467: 'Hunters Domain - Wolfen 38',
 3465: 'Hunters Domain - Wolfen 39',
 3466: 'Hunters Domain - Wolfen 40',
 6320: 'Hunters Domain - Wolfen 41',
 10978: 'Hunters Domain - Wolfen 42',
 8743: 'Hunters Domain - Wolfen 43',
 9133: 'Hunters Domain - Wolfen 44',
 11474: 'Hunters Domain - Wolfen 45',
 11424: 'Hunters Domain - Wolfen 46'}
WOLFEN_KEY_TO_ZONES = {}
for _zone, _mapping in WOLFEN_ZONE_KEY_TO_LOCATION.items():
    for _key in _mapping:
        WOLFEN_KEY_TO_ZONES.setdefault(_key, []).append(_zone)
WOLFEN_KEY_TO_LOCATION = {
    _key: WOLFEN_ZONE_KEY_TO_LOCATION[_zones[0]][_key]
    for _key, _zones in WOLFEN_KEY_TO_ZONES.items()
}


# ============================================================================
# 0.7.4 BALANCE + LOGIC PATCH (2026-10-04)
# Grounded in the user's chronological audit/export.
# ============================================================================

PROTOTYPE_VERSION = "0.7.4-balance-logic"

ITEM_NOOTIES_5 = "Nooties +5"
ITEM_NOOTIES_10 = "Nooties +10"
ITEM_NOOTIES_20 = "Nooties +20"
ITEM_NOOTIES_30 = "Nooties +30"
ITEM_NOOTIES_40 = "Nooties +40"

ITEM_HP_RESTORE_10 = "HP Restore +10"
ITEM_HP_RESTORE_20 = "HP Restore +20"
ITEM_HP_RESTORE_30 = "HP Restore +30"

ITEM_MAGIC_RESTORE_10 = "Magic Restore +10"
ITEM_MAGIC_RESTORE_15 = "Magic Restore +15"
ITEM_MAGIC_RESTORE_20 = "Magic Restore +20"
ITEM_MAGIC_RESTORE_30 = "Magic Restore +30"

ITEM_ATTACK_2 = "+2% Attack"
ITEM_ATTACK_8 = "+8% Attack"
ITEM_PROTECTION_2 = "+2% Protection"
ITEM_PROTECTION_8 = "+8% Protection"

ITEM_NAME_TO_ID = dict(ITEM_NAME_TO_ID)
ITEM_NAME_TO_ID.update({
    ITEM_NOOTIES_5: ITEM_ID_BASE + 29,
    ITEM_NOOTIES_10: ITEM_ID_BASE + 30,
    ITEM_NOOTIES_20: ITEM_ID_BASE + 31,
    ITEM_NOOTIES_30: ITEM_ID_BASE + 32,
    ITEM_NOOTIES_40: ITEM_ID_BASE + 33,
    ITEM_HP_RESTORE_10: ITEM_ID_BASE + 34,
    ITEM_HP_RESTORE_20: ITEM_ID_BASE + 35,
    ITEM_HP_RESTORE_30: ITEM_ID_BASE + 36,
    ITEM_MAGIC_RESTORE_10: ITEM_ID_BASE + 37,
    ITEM_MAGIC_RESTORE_15: ITEM_ID_BASE + 38,
    ITEM_MAGIC_RESTORE_20: ITEM_ID_BASE + 39,
    ITEM_MAGIC_RESTORE_30: ITEM_ID_BASE + 40,
    ITEM_ATTACK_2: ITEM_ID_BASE + 41,
    ITEM_ATTACK_8: ITEM_ID_BASE + 42,
    ITEM_PROTECTION_2: ITEM_ID_BASE + 43,
    ITEM_PROTECTION_8: ITEM_ID_BASE + 44,
})

ITEM_MONEY_VALUES = {
    ITEM_NOOTIES_5: 5,
    ITEM_NOOTIES_10: 10,
    ITEM_NOOTIES_20: 20,
    ITEM_NOOTIES_30: 30,
    ITEM_NOOTIES_40: 40,
}
ITEM_HP_RESTORE_AMOUNTS = {
    ITEM_HP_RESTORE_10: 10,
    ITEM_HP_RESTORE_20: 20,
    ITEM_HP_RESTORE_30: 30,
}
ITEM_MAGIC_RESTORE_AMOUNTS = {
    ITEM_MAGIC_RESTORE_10: 10,
    ITEM_MAGIC_RESTORE_15: 15,
    ITEM_MAGIC_RESTORE_20: 20,
    ITEM_MAGIC_RESTORE_30: 30,
}

# 2 + 2 + 5 + 8 + 8 = 25% total for each combat direction.
ITEM_COMBAT_BONUSES = {
    ITEM_ATTACK_2: {"effect": "damage", "percent": 2},
    ITEM_ATTACK_BONUS: {"effect": "damage", "percent": 5},
    ITEM_ATTACK_8: {"effect": "damage", "percent": 8},
    ITEM_PROTECTION_2: {"effect": "protection", "percent": 2},
    ITEM_PROTECTION_BONUS: {"effect": "protection", "percent": 5},
    ITEM_PROTECTION_8: {"effect": "protection", "percent": 8},
}
ITEM_COMBAT_BONUS_CAP_PERCENT = 25

ITEM_REWARD_COUNTS = {
    ITEM_PROGRESSIVE_LIFE_GAUGE: 4,
    ITEM_PROGRESSIVE_MAGIC_GAUGE: 3,
    ITEM_HP_RESTORE_10: 12,
    ITEM_HP_RESTORE_20: 10,
    ITEM_HP_RESTORE_30: 8,
    ITEM_MAGIC_RESTORE_10: 10,
    ITEM_MAGIC_RESTORE_15: 10,
    ITEM_MAGIC_RESTORE_20: 8,
    ITEM_MAGIC_RESTORE_30: 4,
    ITEM_ATTACK_2: 2,
    ITEM_ATTACK_BONUS: 1,
    ITEM_ATTACK_8: 2,
    ITEM_PROTECTION_2: 2,
    ITEM_PROTECTION_BONUS: 1,
    ITEM_PROTECTION_8: 2,
}

ITEM_USEFUL = frozenset((
    ITEM_PROGRESSIVE_LIFE_GAUGE,
    ITEM_PROGRESSIVE_MAGIC_GAUGE,
    ITEM_ATTACK_2, ITEM_ATTACK_BONUS, ITEM_ATTACK_8,
    ITEM_PROTECTION_2, ITEM_PROTECTION_BONUS, ITEM_PROTECTION_8,
))
ITEM_CONSUMABLE_FILLER = frozenset(tuple(ITEM_HP_RESTORE_AMOUNTS) + tuple(ITEM_MAGIC_RESTORE_AMOUNTS))
ITEM_NOOTIES = tuple(ITEM_MONEY_VALUES)

BRACELET_ZONE_LOCATIONS = (
    "Flying Forest - Wolfen 08",
    "Hunters Domain - Wolfen 08",
    "The Quarry - Wolfen 08",
    "The Root - Wolfen 02",
    "The Air Post - Wolfen 08",
    "Forgotten Island - Wolfen 02",
    "Wolfen City - Wolfen 08",
)

FF_BOARD_LOCK_START = 17
FF_CLIMB_LOCK_START = 24
HD_ADVANCED_LOCK_START = 26
QUARRY_SPEED_LOCK_START = 20

EARLY_ZONE_FORBIDDEN_ITEMS = frozenset((
    ITEM_NOOTIES_30, ITEM_NOOTIES_40,
    ITEM_HP_RESTORE_30, ITEM_MAGIC_RESTORE_30,
    ITEM_ATTACK_8, ITEM_PROTECTION_8,
))
MID_ZONE_FORBIDDEN_ITEMS = frozenset((ITEM_NOOTIES_40,))


# ============================================================================
# 0.7.6 SUBZONE + SHOP THRESHOLD PLAYTEST PATCH (2026-10-04)
# Keeps all Location IDs, progression logic and runtime keys from 0.7.4.
# Only Wolfen display names are enriched for hint readability.
# Several boundaries are intentionally provisional for the next full run.
# ============================================================================
PROTOTYPE_VERSION = "0.7.6-shop-thresholds-subzones"
WOLFEN_DISPLAY_NAME_OVERRIDES = {'Nativs City - Wolfen 01': 'Nativs City - Wolfen 01', 'Flying Forest - Wolfen 01': 'Flying Forest - Entrance - Wolfen 01 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 02': 'Flying Forest - Entrance - Wolfen 02 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 03': 'Flying Forest - Entrance - Wolfen 03 - Scrawny Blue Outfit (Club)', 'Flying Forest - Wolfen 04': 'Flying Forest - Entrance - Wolfen 04 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 05': 'Flying Forest - Entrance - Wolfen 05 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 06': 'Flying Forest - Entrance - Wolfen 06 - Scrawny Yellow Outfit (Fists)', 'Flying Forest - Wolfen 07': 'Flying Forest - Entrance - Wolfen 07 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 08': 'Flying Forest - Entrance - Wolfen 08 - Grunt Blue Outfit (Fists)', 'Flying Forest - Wolfen 09': 'Flying Forest - Entrance - Wolfen 09 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 10': 'Flying Forest - Entrance - Wolfen 10 - Scrawny Yellow Outfit (Fists)', 'Flying Forest - Wolfen 11': 'Flying Forest - Entrance - Wolfen 11 - Scrawny Yellow Outfit (Fists)', 'Flying Forest - Wolfen 12': 'Flying Forest - Entrance - Wolfen 12', 'Flying Forest - Wolfen 13': 'Flying Forest - Entrance - Wolfen 13 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 14': 'Flying Forest - Wolfun Camp - Wolfen 14 - Scrawny Blue Outfit (Club)', 'Flying Forest - Wolfen 15': 'Flying Forest - Wolfun Camp - Wolfen 15 - Scrawny Blue Outfit (Club)', 'Flying Forest - Wolfen 16': 'Flying Forest - Wolfun Camp - Wolfen 16 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 17': 'Flying Forest - Wolfun Camp - Wolfen 17 - Scrawny Blue Outfit (Club)', 'Flying Forest - Wolfen 18': 'Flying Forest - Wolfun Camp - Wolfen 18 - Scrawny Blue Outfit (Gun)', 'Flying Forest - Wolfen 19': 'Flying Forest - Wolfun Camp - Wolfen 19 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 20': 'Flying Forest - Wolfun Camp - Wolfen 20 - Scrawny Blue Outfit (Club)', 'Flying Forest - Wolfen 21': 'Flying Forest - Wolfun Camp - Wolfen 21 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 22': 'Flying Forest - Wolfun Camp - Wolfen 22 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 23': 'Flying Forest - Wolfun Camp - Wolfen 23 - Scrawny Blue Outfit (Fists)', 'Flying Forest - Wolfen 24': 'Flying Forest - Wolfun Factory - Wolfen 24 - Scrawny Blue Outfit (Gun)', 'Flying Forest - Wolfen 25': 'Flying Forest - Wolfun Factory - Wolfen 25', 'Flying Forest - Wolfen 26': 'Flying Forest - Wolfun Factory - Wolfen 26', 'Flying Forest - Wolfen 27': 'Flying Forest - Wolfun Factory - Wolfen 27', 'Flying Forest - Wolfen 28': 'Flying Forest - Wolfun Factory - Wolfen 28', 'Flying Forest - Wolfen 29': 'Flying Forest - Wolfun Factory - Wolfen 29', 'Flying Forest - Wolfen 30': 'Flying Forest - Wolfun Factory - Wolfen 30', 'Flying Forest - Wolfen 31': 'Flying Forest - Wolfun Factory - Wolfen 31', 'Flying Forest - Wolfen 32': 'Flying Forest - Wolfun Factory - Wolfen 32', 'Flying Forest - Wolfen 33': 'Flying Forest - Wolfun Factory - Wolfen 33', 'Flying Forest - Wolfen 34': "Flying Forest - Brazul's Crow Chase - Wolfen 34", 'Flying Forest - Wolfen 35': "Flying Forest - Brazul's Crow Chase - Wolfen 35", 'Flying Forest - Wolfen 36': "Flying Forest - Brazul's Crow Chase - Wolfen 36", 'Flying Forest - Wolfen 37': "Flying Forest - Brazul's Crow Chase - Wolfen 37", 'Hunters Domain - Wolfen 01': 'Hunters Domain - Entrance - Wolfen 01 - Scrawny Blue Outfit (Fists)', 'Hunters Domain - Wolfen 02': 'Hunters Domain - Entrance - Wolfen 02 - Scrawny Blue Outfit (Gun)', 'Hunters Domain - Wolfen 03': 'Hunters Domain - Entrance - Wolfen 03 - Scrawny Blue Outfit (Fists)', 'Hunters Domain - Wolfen 04': 'Hunters Domain - Entrance - Wolfen 04 - Scrawny Blue Outfit (Fists)', 'Hunters Domain - Wolfen 05': 'Hunters Domain - Entrance - Wolfen 05 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 06': 'Hunters Domain - Entrance - Wolfen 06 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 07': 'Hunters Domain - Entrance - Wolfen 07 - Scrawny Yellow Outfit (Fists)', 'Hunters Domain - Wolfen 08': 'Hunters Domain - Entrance - Wolfen 08 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 09': 'Hunters Domain - Wolfun Camp - Wolfen 09 - Scrawny Blue Outfit (Gun)', 'Hunters Domain - Wolfen 10': 'Hunters Domain - Wolfun Camp - Wolfen 10 - Scrawny Blue Outfit (Gun)', 'Hunters Domain - Wolfen 11': 'Hunters Domain - Wolfun Camp - Wolfen 11 - Gun Blue Outfit', 'Hunters Domain - Wolfen 12': 'Hunters Domain - Wolfun Camp - Wolfen 12 - Gun Blue Outfit', 'Hunters Domain - Wolfen 13': 'Hunters Domain - Wolfun Camp - Wolfen 13 - Club Blue Outfit', 'Hunters Domain - Wolfen 14': 'Hunters Domain - Wolfun Camp - Wolfen 14 - Fists Black Outfit', 'Hunters Domain - Wolfen 15': 'Hunters Domain - Wolfun Camp - Wolfen 15 - Fists Black Outfit', 'Hunters Domain - Wolfen 16': 'Hunters Domain - Wolfun Camp - Wolfen 16 - Grunt Blue Outfit (Fists)', 'Hunters Domain - Wolfen 17': 'Hunters Domain - Wolfun Camp - Wolfen 17 - Scrawny Blue Outfit (Sniper)', 'Hunters Domain - Wolfen 18': 'Hunters Domain - Wolfun Camp - Wolfen 18 - Scrawny Blue Outfit (Sniper)', 'Hunters Domain - Wolfen 19': 'Hunters Domain - Wolfun Camp - Wolfen 19 - Grunt Blue Outfit (Fists)', 'Hunters Domain - Wolfen 20': 'Hunters Domain - Wolfun Camp - Wolfen 20 - Grunt Blue Outfit (Fists)', 'Hunters Domain - Wolfen 21': 'Hunters Domain - Wolfun Camp - Wolfen 21 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 22': 'Hunters Domain - Wolfun Camp - Wolfen 22 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 23': 'Hunters Domain - Wolfun Camp - Wolfen 23 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 24': 'Hunters Domain - Wolfun Camp - Wolfen 24 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 25': 'Hunters Domain - Wolfun Camp - Wolfen 25 - Scrawny Blue Outfit (Club)', 'Hunters Domain - Wolfen 26': "Hunters Domain - Hunter's Dungeon - Wolfen 26 - Grunt Blue Outfit (Fists)", 'Hunters Domain - Wolfen 27': "Hunters Domain - Hunter's Dungeon - Wolfen 27 - Scrawny Blue Outfit (Gun)", 'Hunters Domain - Wolfen 28': "Hunters Domain - Hunter's Dungeon - Wolfen 28 - Scrawny Blue Outfit (Gun)", 'Hunters Domain - Wolfen 29': "Hunters Domain - Hunter's Dungeon - Wolfen 29 - Grunt Blue Outfit (Fists)", 'Hunters Domain - Wolfen 30': "Hunters Domain - Hunter's Dungeon - Wolfen 30 - Grunt Blue Outfit (Fists)", 'Hunters Domain - Wolfen 31': "Hunters Domain - Hunter's Dungeon - Wolfen 31 - Scrawny Blue Outfit (Sniper)", 'Hunters Domain - Wolfen 32': "Hunters Domain - Hunter's Dungeon - Wolfen 32 - Scrawny Blue Outfit (Sniper)", 'Hunters Domain - Wolfen 33': "Hunters Domain - Hunter's Dungeon - Wolfen 33 - Scrawny Blue Outfit (Fists)", 'Hunters Domain - Wolfen 34': "Hunters Domain - Hunter's Dungeon - Wolfen 34 - Grunt Blue Outfit (Fists)", 'Hunters Domain - Wolfen 35': "Hunters Domain - Hunter's Dungeon - Wolfen 35 - Scrawny Blue Outfit (Gun)", 'Hunters Domain - Wolfen 36': 'Hunters Domain - Hilltop Fort - Wolfen 36 - Grunt Blue Outfit (Fists)', 'Hunters Domain - Wolfen 37': 'Hunters Domain - Hilltop Fort - Wolfen 37 - Scrawny Blue Outfit (Fists)', 'Hunters Domain - Wolfen 38': 'Hunters Domain - Hilltop Fort - Wolfen 38 - Scrawny Yellow Outfit (Fists)', 'Hunters Domain - Wolfen 39': 'Hunters Domain - Hilltop Fort - Wolfen 39 - Scrawny Yellow Outfit (Fists)', 'Hunters Domain - Wolfen 40': 'Hunters Domain - Hilltop Fort - Wolfen 40 - Scrawny Yellow Outfit (Fists)', 'Hunters Domain - Wolfen 41': 'Hunters Domain - Hilltop Fort - Wolfen 41 - Scrawny Blue Outfit (Gun)', 'Hunters Domain - Wolfen 42': 'Hunters Domain - Hilltop Fort - Wolfen 42 - Scrawny Blue Outfit (Sniper)', 'Hunters Domain - Wolfen 43': 'Hunters Domain - Hilltop Fort - Wolfen 43 - Grunt Blue Outfit (Fists)', 'Hunters Domain - Wolfen 44': 'Hunters Domain - Hilltop Fort - Wolfen 44 - Scrawny Blue Outfit (Fists)', 'Hunters Domain - Wolfen 45': 'Hunters Domain - Hilltop Fort - Wolfen 45 - Scrawny Blue Outfit (Fists)', 'Hunters Domain - Wolfen 46': 'Hunters Domain - Hilltop Fort - Wolfen 46 - Scrawny Blue Outfit (Fists)', 'Wind Tower - Wolfen 01': 'Hunters Domain - Wind Tower - Wolfen 01 - Scrawny Blue Outfit (Rocket Gun)', 'Wind Tower - Wolfen 02': 'Hunters Domain - Wind Tower - Wolfen 02 - Scrawny Blue Outfit (Gun)', 'The Quarry - Wolfen 01': 'The Quarry - Entrance - Wolfen 01', 'The Quarry - Wolfen 02': 'The Quarry - Entrance - Wolfen 02', 'The Quarry - Wolfen 03': 'The Quarry - Entrance - Wolfen 03', 'The Quarry - Wolfen 04': 'The Quarry - Entrance - Wolfen 04', 'The Quarry - Wolfen 05': 'The Quarry - Entrance - Wolfen 05 - Scrawny Blue Outfit (Club)', 'The Quarry - Wolfen 06': 'The Quarry - Entrance - Wolfen 06 - Scrawny Blue Outfit (Gun)', 'The Quarry - Wolfen 07': 'The Quarry - Entrance - Wolfen 07 - Scrawny Blue Outfit (Gun)', 'The Quarry - Wolfen 08': 'The Quarry - Quarry - Wolfen 08 - Scrawny Blue Outfit (Gun)', 'The Quarry - Wolfen 09': 'The Quarry - Quarry - Wolfen 09 - Grunt Blue Outfit (Fists)', 'The Quarry - Wolfen 10': 'The Quarry - Quarry - Wolfen 10 - Scrawny Yellow Outfit (Fists)', 'The Quarry - Wolfen 11': 'The Quarry - Quarry - Wolfen 11 - Scrawny Yellow Outfit (Fists)', 'The Quarry - Wolfen 12': 'The Quarry - Quarry - Wolfen 12 - Scrawny Yellow Outfit (Fists)', 'The Quarry - Wolfen 13': 'The Quarry - Quarry - Wolfen 13 - Grunt Blue Outfit (Fists)', 'The Quarry - Wolfen 14': 'The Quarry - Quarry - Wolfen 14', 'The Quarry - Wolfen 15': 'The Quarry - Quarry - Wolfen 15', 'The Quarry - Wolfen 16': 'The Quarry - Quarry - Wolfen 16', 'The Quarry - Wolfen 17': 'The Quarry - Quarry - Wolfen 17 - Grunt Black Outfit (Fists)', 'The Quarry - Wolfen 18': 'The Quarry - Quarry - Wolfen 18', 'The Quarry - Wolfen 19': 'The Quarry - Quarry - Wolfen 19 - Grunt Black Outfit (Fists)', 'The Quarry - Wolfen 20': 'The Quarry - Arena - Wolfen 20', 'The Quarry - Wolfen 21': 'The Quarry - Arena - Wolfen 21', 'The Quarry - Wolfen 22': 'The Quarry - Arena - Wolfen 22', 'The Quarry - Wolfen 23': 'The Quarry - Arena - Wolfen 23', 'The Quarry - Wolfen 24': 'The Quarry - Arena - Wolfen 24', 'The Quarry - Wolfen 25': 'The Quarry - Arena - Wolfen 25', 'The Quarry - Wolfen 26': 'The Quarry - Arena - Wolfen 26', 'The Quarry - Wolfen 27': 'The Quarry - Arena - Wolfen 27', 'The Quarry - Wolfen 28': 'The Quarry - Arena - Wolfen 28', 'The Quarry - Wolfen 29': 'The Quarry - Arena - Wolfen 29', 'The Quarry - Wolfen 30': 'The Quarry - Arena - Wolfen 30', 'The Quarry - Wolfen 31': 'The Quarry - Arena - Wolfen 31', 'Amber Quarry - Wolfen 01': 'The Quarry - Amber Quarry - Wolfen 01 - Scrawny Blue Outfit (Fists)', 'Amber Quarry - Wolfen 02': 'The Quarry - Amber Quarry - Wolfen 02 - Scrawny Yellow Outfit (Fists)', 'Amber Quarry - Wolfen 03': 'The Quarry - Amber Quarry - Wolfen 03 - Grunt Black Outfit (Fists)', 'Amber Quarry - Wolfen 04': 'The Quarry - Amber Quarry - Wolfen 04 - Scrawny Blue Outfit (Fists)', 'Amber Quarry - Wolfen 05': 'The Quarry - Amber Quarry - Wolfen 05 - Scrawny Yellow Outfit (Fists)', 'Amber Quarry - Wolfen 06': 'The Quarry - Amber Quarry - Wolfen 06 - Grunt Black Outfit (Fists)', 'Amber Quarry - Wolfen 07': 'The Quarry - Amber Quarry - Wolfen 07 - Scrawny Blue Outfit (Fists)', 'Amber Quarry - Wolfen 08': 'The Quarry - Amber Quarry - Wolfen 08 - Grunt Blue Outfit (Fists)', 'Amber Quarry - Wolfen 09': 'The Quarry - Amber Quarry - Wolfen 09 - Scrawny Blue Outfit (Fists)', 'Amber Quarry - Wolfen 10': 'The Quarry - Amber Quarry - Wolfen 10 - Grunt Blue Outfit (Fists)', 'Amber Quarry - Wolfen 11': 'The Quarry - Amber Quarry - Wolfen 11 - Scrawny Blue Outfit (Sniper)', 'Amber Quarry - Wolfen 12': 'The Quarry - Amber Quarry - Wolfen 12 - Scrawny Blue Outfit (Sniper)', 'Amber Quarry - Wolfen 13': 'The Quarry - Amber Quarry - Wolfen 13 - Scrawny Blue Outfit (Sniper)', 'Amber Quarry - Wolfen 14': 'The Quarry - Amber Quarry - Wolfen 14 - Scrawny Blue Outfit (Sniper)', 'The Root - Wolfen 01': 'The Root - Wolfun Bridge - Wolfen 01 - Scrawny Blue Outfit (Rocket Gun)', 'The Root - Wolfen 02': 'The Root - Wolfun Camp 1 - Wolfen 02 - Scrawny Blue Outfit (Fists)', 'The Root - Wolfen 03': 'The Root - Wolfun Camp 1 - Wolfen 03 - Scrawny Blue Outfit (Gun)', 'The Root - Wolfen 04': 'The Root - Wolfun Camp 1 - Wolfen 04 - Scrawny Blue Outfit (Gun)', 'The Root - Wolfen 05': 'The Root - Wolfun Camp 1 - Wolfen 05 - Scrawny Blue Outfit (Gun)', 'The Root - Wolfen 06': 'The Root - Wolfun Camp 2 - Wolfen 06 - Scrawny Blue Outfit (Sniper)', 'The Root - Wolfen 07': 'The Root - Wolfun Camp 2 - Wolfen 07 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 01': 'The Air Post - Entrance - Wolfen 01 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 02': 'The Air Post - Entrance - Wolfen 02 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 03': 'The Air Post - Dark Island - Wolfen 03 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 04': 'The Air Post - Dark Island - Wolfen 04 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 05': 'The Air Post - Dark Island - Wolfen 05 - Scrawny Blue Outfit (Fists)', 'The Air Post - Wolfen 06': 'The Air Post - Dark Island - Wolfen 06 - Scrawny Blue Outfit (Club)', 'The Air Post - Wolfen 07': 'The Air Post - Dark Island - Wolfen 07 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 08': 'The Air Post - Dark Island - Wolfen 08 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 09': 'The Air Post - Dark Island - Wolfen 09 - Scrawny Blue Outfit (Club)', 'The Air Post - Wolfen 10': 'The Air Post - Dark Island - Wolfen 10 - Grunt Black Outfit (Fists)', 'The Air Post - Wolfen 11': 'The Air Post - Dark Island - Wolfen 11 - Grunt Yellow Outfit (Club)', 'The Air Post - Wolfen 12': 'The Air Post - Dark Island - Wolfen 12 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 13': 'The Air Post - Dark Island - Wolfen 13 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 14': 'The Air Post - Dark Island - Wolfen 14 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 15': 'The Air Post - Dark Island - Wolfen 15 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 16': 'The Air Post - Dark Island - Wolfen 16 - Grunt Brown Outfit (Club)', 'The Air Post - Wolfen 17': 'The Air Post - Dark Island - Wolfen 17 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 18': 'The Air Post - Dark Island - Wolfen 18 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 19': 'The Air Post - Dark Island - Wolfen 19 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 20': 'The Air Post - Dark Island - Wolfen 20 - Grunt Yellow Outfit (Fists)', 'The Air Post - Wolfen 21': 'The Air Post - Wolfun Guard Room - Wolfen 21 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 22': 'The Air Post - Wolfun Guard Room - Wolfen 22 - Grunt Yellow Outfit (Club)', 'The Air Post - Wolfen 23': 'The Air Post - Wolfun Guard Room - Wolfen 23 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 24': 'The Air Post - Wolfun Guard Room - Wolfen 24 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 25': 'The Air Post - Wolfun Guard Room - Wolfen 25 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 26': 'The Air Post - Wolfun Guard Room - Wolfen 26 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 27': 'The Air Post - Wolfun Guard Room - Wolfen 27 - Scrawny Yellow Outfit (Gun)', 'The Air Post - Wolfen 28': 'The Air Post - Energy Field Control Room - Wolfen 28 - Scrawny Blue Outfit (Fists)', 'The Air Post - Wolfen 29': 'The Air Post - Energy Field Control Room - Wolfen 29 - Grunt Black Outfit (Fists)', 'The Air Post - Wolfen 30': 'The Air Post - Energy Field Control Room - Wolfen 30 - Scrawny Blue Outfit (Rocket Gun)', 'The Air Post - Wolfen 31': 'The Air Post - Energy Field Control Room - Wolfen 31 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 32': 'The Air Post - Energy Field Control Room - Wolfen 32 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 33': 'The Air Post - Energy Field Control Room - Wolfen 33 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 34': 'The Air Post - Energy Field Control Room - Wolfen 34 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 35': 'The Air Post - Air Post Blowers - Wolfen 35 - Grunt Blue Outfit (Fists)', 'The Air Post - Wolfen 36': 'The Air Post - Air Post Blowers - Wolfen 36 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 37': 'The Air Post - Air Post Blowers - Wolfen 37 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 38': 'The Air Post - Air Post Blowers - Wolfen 38 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 39': 'The Air Post - Air Post Blowers - Wolfen 39 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 40': 'The Air Post - Air Post Blowers - Wolfen 40 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 41': 'The Air Post - Air Post Blowers - Wolfen 41 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 42': 'The Air Post - Air Post Blowers - Wolfen 42 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 43': 'The Air Post - Air Post Blowers - Wolfen 43 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 44': 'The Air Post - Air Post Blowers - Wolfen 44 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 45': 'The Air Post - Air Post Blowers - Wolfen 45 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 46': 'The Air Post - Air Post Blowers - Wolfen 46 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 47': 'The Air Post - Air Post Blowers - Wolfen 47 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 48': 'The Air Post - Air Post Blowers - Wolfen 48 - Scrawny Blue Outfit (Gun)', 'The Air Post - Wolfen 49': 'The Air Post - Wolfun Ventilation Zone - Wolfen 49 - Grunt Blue Outfit (Club)', 'The Air Post - Wolfen 50': 'The Air Post - Wolfun Ventilation Zone - Wolfen 50 - Grunt Yellow Outfit (Club)', 'The Air Post - Wolfen 51': 'The Air Post - Wolfun Ventilation Zone - Wolfen 51 - Grunt Yellow Outfit (Fists)', 'The Air Post - Wolfen 52': 'The Air Post - Wolfun Ventilation Zone - Wolfen 52 - Scrawny Blue Outfit (Rocket Gun)', 'The Air Post - Wolfen 53': 'The Air Post - Wolfun Ventilation Zone - Wolfen 53 - Scrawny Blue Outfit (Rocket Gun)', 'The Air Post - Wolfen 54': 'The Air Post - Forgotten Island Cannon Room - Wolfen 54 - Grunt Yellow Outfit (Fists)', 'The Air Post - Wolfen 55': 'The Air Post - Forgotten Island Cannon Room - Wolfen 55 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 56': 'The Air Post - Forgotten Island Cannon Room - Wolfen 56 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 57': 'The Air Post - Forgotten Island Cannon Room - Wolfen 57 - Scrawny Blue Outfit (Sniper)', 'The Air Post - Wolfen 58': 'The Air Post - Forgotten Island Cannon Room - Wolfen 58 - Scrawny Blue Outfit (Rocket Gun)', 'The Air Post - Wolfen 59': 'The Air Post - Forgotten Island Cannon Room - Wolfen 59 - Scrawny Blue Outfit (Club)', 'The Air Post - Wolfen 60': 'The Air Post - Forgotten Island Cannon Room - Wolfen 60 - Scrawny Blue Outfit (Club)', 'The Air Post - Wolfen 61': 'The Air Post - Forgotten Island Cannon Room - Wolfen 61 - Grunt Black Outfit (Fists)', 'Forgotten Island - Wolfen 01': 'Forgotten Island - Entrance - Wolfen 01', 'Forgotten Island - Wolfen 02': 'Forgotten Island - Entrance - Wolfen 02', 'Forgotten Island - Wolfen 03': 'Forgotten Island - Entrance - Wolfen 03', 'Forgotten Island - Wolfen 04': "Forgotten Island - Hell's Road - Wolfen 04 - Scrawny Yellow Outfit (Fists)", 'Forgotten Island - Wolfen 05': 'Forgotten Island - Laboratory Entrance - Wolfen 05 - Grunt Yellow Outfit (Club)', 'Forgotten Island - Wolfen 06': 'Forgotten Island - Laboratory Entrance - Wolfen 06 - Grunt Blue Outfit (Fists)', 'Forgotten Island - Wolfen 07': 'Forgotten Island - Laboratory Entrance - Wolfen 07 - Scrawny Yellow Outfit (Rocket Gun)', 'Forgotten Island - Wolfen 08': 'Forgotten Island - Laboratory Entrance - Wolfen 08 - Kronos Black Outfit (Fists)', 'Wolfen City - Wolfen 01': 'Wolfen City - Entrance - Wolfen 01 - Scrawny Blue Outfit (Gun)', 'Wolfen City - Wolfen 02': 'Wolfen City - Entrance - Wolfen 02 - Grunt Yellow Outfit (Fists)', 'Wolfen City - Wolfen 03': 'Wolfen City - Entrance - Wolfen 03 - Scrawny Blue Outfit (Fists)', 'Wolfen City - Wolfen 04': 'Wolfen City - Entrance - Wolfen 04 - Grunt Yellow Outfit (Fists)', 'Wolfen City - Wolfen 05': 'Wolfen City - Entrance - Wolfen 05 - Scrawny Blue Outfit (Fists)', 'Wolfen City - Wolfen 06': 'Wolfen City - Wolfen 06 - Scrawny Blue Outfit (Club)', 'Wolfen City - Wolfen 07': 'Wolfen City - Wolfen 07 - Scrawny Blue Outfit (Club)', 'Wolfen City - Wolfen 08': 'Wolfen City - Wolfen 08 - Kronos Black Outfit (Fists)', 'Wolfen City - Wolfen 09': 'Wolfen City - Wolfen 09 - Grunt Blue Outfit (Club)', 'Wolfen City - Wolfen 10': 'Wolfen City - Wolfen 10 - Kronos Black Outfit (Fists)', 'Wolfen City - Wolfen 11': 'Wolfen City - Wolfen 11 - Scrawny Yellow Outfit (Gun)', 'Wolfen City - Wolfen 12': 'Wolfen City - Wolfen 12 - Grunt Blue Outfit (Fists)', 'Wolfen City - Wolfen 13': 'Wolfen City - Wolfen 13 - Scrawny Blue Outfit (Sniper)', 'Wolfen City - Wolfen 14': 'Wolfen City - Wolfen 14 - Scrawny Blue Outfit (Sniper)', 'Wolfen City - Wolfen 15': 'Wolfen City - Wolfen 15 - Scrawny Yellow Outfit (Gun)', 'Wolfen City - Wolfen 16': 'Wolfen City - Wolfen 16 - Kronos Black Outfit (Fists)', 'Wolfen City - Wolfen 17': 'Wolfen City - Wolfen 17 - Grunt Yellow Outfit (Fists)', 'Wolfen City - Wolfen 18': 'Wolfen City - Wolfen 18 - Grunt Blue Outfit (Club)', 'Wolfen City - Wolfen 19': 'Wolfen City - Wolfen 19 - Scrawny Blue Outfit (Gun)', 'Wolfen City - Wolfen 20': 'Wolfen City - Wolfen 20 - Grunt Blue Outfit (Club)', 'Wolfen City - Wolfen 21': 'Wolfen City - Wolfen 21 - Kronos Black Outfit (Fists)', 'Wolfen City - Wolfen 22': 'Wolfen City - Wolfen 22 - Scrawny Yellow Outfit (Gun)', 'Wolfen City - Wolfen 23': 'Wolfen City - Wolfen 23 - Scrawny Yellow Outfit (Gun)', 'Wolfen City - Wolfen 24': 'Wolfen City - Wolfen 24 - Scrawny Blue Outfit (Gun)', 'Wolfen City - Wolfen 25': 'Wolfen City - Wolfen 25 - Scrawny Blue Outfit (Gun)', 'Wolfen City - Wolfen 26': 'Wolfen City - Wolfen 26 - Scrawny Blue Outfit (Gun)', 'Wolfen City - Wolfen 27': 'Wolfen City - Wolfen 27 - Grunt Blue Outfit (Fists)', 'Wolfen City - Wolfen 28': 'Wolfen City - Wolfen 28 - Grunt Blue Outfit (Fists)', 'Wolfen City - Wolfen 29': 'Wolfen City - Wolfen 29 - Grunt Blue Outfit (Fists)', 'Wolfen City - Wolfen 30': 'Wolfen City - Wolfen 30', 'Wolfen City - Wolfen 31': 'Wolfen City - Wolfen 31', 'Wolfen City - Wolfen 32': 'Wolfen City - Wolfen 32 - Scrawny Blue Outfit (Sniper)', 'Wolfen City - Wolfen 33': 'Wolfen City - Wolfen 33 - Kronos Black Outfit (Fists)', 'Wolfen City - Wolfen 34': 'Wolfen City - Wolfen 34 - Scrawny Blue Outfit (Sniper)', 'Wolfen City - Wolfen 35': 'Wolfen City - Wolfen 35 - Scrawny Blue Outfit (Sniper)', 'Wolfen City - Wolfen 36': 'Wolfen City - Wolfen 36 - Scrawny Blue Outfit (Sniper)', 'Wolfen City - Wolfen 37': 'Wolfen City - Wolfun Reserve - Wolfen 37 - Scrawny Blue Outfit (Fists)', 'Wolfen City - Wolfen 38': 'Wolfen City - Wolfun Reserve - Wolfen 38', 'Wolfen City - Wolfen 39': 'Wolfen City - Wolfun Reserve - Wolfen 39 - Scrawny Blue Outfit (Fists)', 'Wolfen City - Wolfen 40': 'Wolfen City - Wolfun Reserve - Wolfen 40 - Scrawny Blue Outfit (Fists)', 'The Fortress - Wolfen 01': 'The Fortress - Fortress Arena - Wolfen 01', 'The Fortress - Wolfen 02': 'The Fortress - Fortress Arena - Wolfen 02', 'The Fortress - Wolfen 03': 'The Fortress - Fortress Arena - Wolfen 03', 'The Fortress - Wolfen 04': 'The Fortress - Fortress Arena - Wolfen 04 - UNMAPPED', 'The Fortress - Wolfen 05': 'The Fortress - Fortress Arena - Wolfen 05', 'The Fortress - Wolfen 06': 'The Fortress - Fortress Arena - Wolfen 06', 'The Fortress - Wolfen 07': 'The Fortress - Fortress Arena - Wolfen 07', 'The Fortress - Wolfen 08': 'The Fortress - Fortress Arena - Wolfen 08', 'The Fortress - Wolfen 09': 'The Fortress - Fortress Arena - Wolfen 09', 'The Fortress - Wolfen 10': 'The Fortress - Fortress Arena - Wolfen 10', 'The Fortress - Wolfen 11': 'The Fortress - Fortress Arena - Wolfen 11', 'The Fortress - Wolfen 12': 'The Fortress - Fortress Arena - Wolfen 12', 'The Fortress - Wolfen 13': 'The Fortress - Fortress Arena - Wolfen 13'}
SUBZONE_PLAYTEST_RANGES = {'Nativs City': [(1, 1, 'Nativs City', 'single')], 'Flying Forest': [(1, 13, 'Entrance', 'confirmed'), (14, 23, 'Wolfun Camp', 'provisional'), (24, 33, 'Wolfun Factory', 'provisional'), (34, 37, "Brazul's Crow Chase", 'provisional')], 'Hunters Domain': [(1, 8, 'Entrance', 'provisional'), (9, 25, 'Wolfun Camp', 'provisional'), (26, 35, "Hunter's Dungeon", 'provisional'), (36, 46, 'Hilltop Fort', 'provisional')], 'Wind Tower': [(1, 2, 'Wind Tower', 'confirmed')], 'The Quarry': [(1, 7, 'Entrance', 'provisional'), (8, 19, 'Quarry', 'provisional'), (20, 31, 'Arena', 'provisional')], 'Amber Quarry': [(1, 14, 'Amber Quarry', 'confirmed')], 'The Root': [(1, 1, 'Wolfun Bridge', 'strong'), (2, 5, 'Wolfun Camp 1', 'provisional'), (6, 7, 'Wolfun Camp 2', 'provisional')], 'The Air Post': [(1, 2, 'Entrance', 'confirmed'), (3, 20, 'Dark Island', 'provisional'), (21, 27, 'Wolfun Guard Room', 'provisional'), (28, 34, 'Energy Field Control Room', 'provisional'), (35, 48, 'Air Post Blowers', 'provisional'), (49, 53, 'Wolfun Ventilation Zone', 'provisional'), (54, 61, 'Forgotten Island Cannon Room', 'provisional')], 'Forgotten Island': [(1, 3, 'Entrance', 'confirmed'), (4, 4, "Hell's Road", 'confirmed'), (5, 8, 'Laboratory Entrance', 'confirmed')], 'Wolfen City': [(1, 5, 'Entrance', 'provisional'), (6, 36, 'Wolfen City', 'provisional'), (37, 40, 'Wolfun Reserve', 'strong')], 'The Fortress': [(1, 13, 'Fortress Arena', 'confirmed')]}

# Preserve old IDs while replacing only the display names of Wolfen locations.
_OLD_LOCATION_NAME_TO_ID = dict(LOCATION_NAME_TO_ID)
LOCATION_NAME_TO_ID = {WOLFEN_DISPLAY_NAME_OVERRIDES.get(_name, _name): _id for _name, _id in _OLD_LOCATION_NAME_TO_ID.items()}

# Runtime key -> Location display name.
WOLFEN_ZONE_KEY_TO_LOCATION = {
    _zone: {_key: WOLFEN_DISPLAY_NAME_OVERRIDES.get(_name, _name) for _key, _name in _mapping.items()}
    for _zone, _mapping in WOLFEN_ZONE_KEY_TO_LOCATION.items()
}
WOLFEN_LOCATIONS_BY_ZONE = {
    _zone: tuple(WOLFEN_DISPLAY_NAME_OVERRIDES.get(_name, _name) for _name in _names)
    for _zone, _names in WOLFEN_LOCATIONS_BY_ZONE.items()
}
WOLFEN_KEY_TO_ZONES = {}
for _zone, _mapping in WOLFEN_ZONE_KEY_TO_LOCATION.items():
    for _key in _mapping:
        WOLFEN_KEY_TO_ZONES.setdefault(_key, []).append(_zone)
WOLFEN_KEY_TO_LOCATION = {
    _key: WOLFEN_ZONE_KEY_TO_LOCATION[_zones[0]][_key]
    for _key, _zones in WOLFEN_KEY_TO_ZONES.items()
}

# Region contents and fixed progression placements must follow the renamed locations.
LOCATION_NAMES_BY_ZONE = {
    _zone: tuple(WOLFEN_DISPLAY_NAME_OVERRIDES.get(_name, _name) for _name in _names)
    for _zone, _names in LOCATION_NAMES_BY_ZONE.items()
}
STARTER_LOCATION_NAME = WOLFEN_DISPLAY_NAME_OVERRIDES.get(STARTER_LOCATION_NAME, STARTER_LOCATION_NAME)
BRACELET_ZONE_LOCATIONS = tuple(WOLFEN_DISPLAY_NAME_OVERRIDES.get(_name, _name) for _name in BRACELET_ZONE_LOCATIONS)

# Overlay descriptions are still keyed by the Location display name.
WOLFEN_LOCATION_DESCRIPTIONS = {
    WOLFEN_DISPLAY_NAME_OVERRIDES.get(_name, _name): _description
    for _name, _description in WOLFEN_LOCATION_DESCRIPTIONS.items()
}

# ============================================================================
# 0.7.7 FORTRESS WOLFEN 04 COMPLETION PATCH (2026-10-04)
# Completes the zone-safe 260/260 Wolfen mapping without changing Location IDs.
# Fortress Wolfen 04 uses persistent key 0x046A. The same numeric key is also
# used by The Quarry Wolfen 02, so the mapping MUST remain zone-scoped.
# ============================================================================
PROTOTYPE_VERSION = "0.7.7-fortress260-shop-thresholds-subzones"
AP_BUILD_VERSION = PROTOTYPE_VERSION

_FORTRESS04_OLD = "The Fortress - Fortress Arena - Wolfen 04 - UNMAPPED"
_FORTRESS04_NEW = "The Fortress - Fortress Arena - Wolfen 04 - Scrawny"
_FORTRESS04_KEY = 0x046A

# Keep the existing AP Location ID while replacing only the display name.
if _FORTRESS04_OLD in LOCATION_NAME_TO_ID:
    _fortress04_id = LOCATION_NAME_TO_ID.pop(_FORTRESS04_OLD)
    LOCATION_NAME_TO_ID[_FORTRESS04_NEW] = _fortress04_id

# Runtime detection is zone-scoped because 0x046A also exists in The Quarry.
WOLFEN_ZONE_KEY_TO_LOCATION = {
    _zone: dict(_mapping) for _zone, _mapping in WOLFEN_ZONE_KEY_TO_LOCATION.items()
}
WOLFEN_ZONE_KEY_TO_LOCATION["The Fortress"][_FORTRESS04_KEY] = _FORTRESS04_NEW

# Keep all per-zone location collections aligned with the renamed Location.
def _replace_fortress04_name(_names):
    return tuple(_FORTRESS04_NEW if _name == _FORTRESS04_OLD else _name for _name in _names)

WOLFEN_LOCATIONS_BY_ZONE = {
    _zone: _replace_fortress04_name(_names) if _zone == "The Fortress" else tuple(_names)
    for _zone, _names in WOLFEN_LOCATIONS_BY_ZONE.items()
}
LOCATION_NAMES_BY_ZONE = {
    _zone: _replace_fortress04_name(_names) if _zone == "The Fortress" else tuple(_names)
    for _zone, _names in LOCATION_NAMES_BY_ZONE.items()
}

# Rebuild collision-aware reverse lookup. For key 0x046A this intentionally
# yields both The Quarry and The Fortress; current-zone mapping picks the right one.
WOLFEN_KEY_TO_ZONES = {}
for _zone, _mapping in WOLFEN_ZONE_KEY_TO_LOCATION.items():
    for _key in _mapping:
        WOLFEN_KEY_TO_ZONES.setdefault(_key, []).append(_zone)
WOLFEN_KEY_TO_LOCATION = {
    _key: WOLFEN_ZONE_KEY_TO_LOCATION[_zones[0]][_key]
    for _key, _zones in WOLFEN_KEY_TO_ZONES.items()
}

# User-facing metadata: type is confirmed as Scrawny; weapon/outfit remain unlabelled.
WOLFEN_DISPLAY_NAME_OVERRIDES = dict(WOLFEN_DISPLAY_NAME_OVERRIDES)
WOLFEN_DISPLAY_NAME_OVERRIDES["The Fortress - Wolfen 04"] = _FORTRESS04_NEW
WOLFEN_LOCATION_DESCRIPTIONS = dict(WOLFEN_LOCATION_DESCRIPTIONS)
WOLFEN_LOCATION_DESCRIPTIONS.pop(_FORTRESS04_OLD, None)
WOLFEN_LOCATION_DESCRIPTIONS[_FORTRESS04_NEW] = "Scrawny"


# ============================================================================
# 0.7.8 SAFE LOGIC / FAST TRAVEL / VALIDATION PATCH (2026-10-05)
# Based on the full live validation run and BWITCH.INI vanilla shop thresholds.
# ============================================================================
PROTOTYPE_VERSION = "0.7.8-safe-logic-fasttravel-shopfix"
AP_BUILD_VERSION = PROTOTYPE_VERSION

# Live blocker measurements from the validation run.
# At the listed global Wolfen count, the next Wolfen/progression route is blocked.
FF_BOARD_LOCK_START = 22       # 22 total reachable before Magic Board wall => FF22+
FF_CLIMB_LOCK_START = 29       # 29 total reachable before Gloves wall => FF29+
HD_ADVANCED_LOCK_START = 26    # 45 + HD01..25 = 70 before Silver Boomy/Bouncers wall
QUARRY_SPEED_LOCK_START = 20   # Arena/late Quarry route requires Speed Board

# Exact vanilla Nativ/shop gates from BWITCH.INI. The tutorial exorcism means
# the first AP shop is effectively available at global Wolfen count 1.
SHOP_UNLOCK_THRESHOLDS = (1, 10, 20, 30, 50, 75, 110, 200)
SHOP_UNLOCK_GROUPS = {
    1: (
        "Nativs City - Shop - Basic Boomy",
    ),
    10: (
        "Nativs City - Shop - Yellow Bracelet",
        "Nativs City - Shop - Telescope",
        "Nativs City - Shop - Magic Board",
    ),
    20: (
        "Nativs City - Shop - Green Bracelet",
        "Nativs City - Shop - Climbing Gloves",
    ),
    30: (
        "Nativs City - Shop - Extra Energy Bar 1",
        "Nativs City - Shop - Blue Bracelet",
        "Nativs City - Shop - Jamgut Birdcall",
    ),
    50: (
        "Nativs City - Shop - Brown Bracelet",
        "Nativs City - Shop - Silver Boomy",
        "Nativs City - Shop - Magic Bouncers",
    ),
    75: (
        "Nativs City - Shop - Black Bracelet",
        "Nativs City - Shop - Speed Board",
        "Nativs City - Shop - Golden Boomy",
    ),
    110: (
        "Nativs City - Shop - Silver Bracelet",
    ),
    200: (
        "Nativs City - Shop - Gold Bracelet",
        "Nativs City - Shop - Extra Energy Bar 2",
    ),
}

# Flying Forest sub-zone correction from the validation run:
# Camp continues through 25; Factory starts at 26.
def _rename_location_everywhere(_old: str, _new: str, _zone: str) -> None:
    global LOCATION_NAME_TO_ID, WOLFEN_ZONE_KEY_TO_LOCATION, WOLFEN_LOCATIONS_BY_ZONE
    global LOCATION_NAMES_BY_ZONE, WOLFEN_LOCATION_DESCRIPTIONS, WOLFEN_DISPLAY_NAME_OVERRIDES
    if _old == _new:
        return
    if _old in LOCATION_NAME_TO_ID:
        _id = LOCATION_NAME_TO_ID.pop(_old)
        LOCATION_NAME_TO_ID[_new] = _id
    if _zone in WOLFEN_ZONE_KEY_TO_LOCATION:
        WOLFEN_ZONE_KEY_TO_LOCATION[_zone] = {
            _key: (_new if _name == _old else _name)
            for _key, _name in WOLFEN_ZONE_KEY_TO_LOCATION[_zone].items()
        }
    if _zone in WOLFEN_LOCATIONS_BY_ZONE:
        WOLFEN_LOCATIONS_BY_ZONE[_zone] = tuple(
            _new if _name == _old else _name for _name in WOLFEN_LOCATIONS_BY_ZONE[_zone]
        )
    if _zone in LOCATION_NAMES_BY_ZONE:
        LOCATION_NAMES_BY_ZONE[_zone] = tuple(
            _new if _name == _old else _name for _name in LOCATION_NAMES_BY_ZONE[_zone]
        )
    if _old in WOLFEN_LOCATION_DESCRIPTIONS:
        WOLFEN_LOCATION_DESCRIPTIONS[_new] = WOLFEN_LOCATION_DESCRIPTIONS.pop(_old)
    WOLFEN_DISPLAY_NAME_OVERRIDES = {
        _base: (_new if _value == _old else _value)
        for _base, _value in WOLFEN_DISPLAY_NAME_OVERRIDES.items()
    }

_rename_location_everywhere(
    "Flying Forest - Wolfun Factory - Wolfen 24 - Scrawny Blue Outfit (Gun)",
    "Flying Forest - Wolfun Camp - Wolfen 24 - Scrawny Blue Outfit (Gun)",
    "Flying Forest",
)
_rename_location_everywhere(
    "Flying Forest - Wolfun Factory - Wolfen 25",
    "Flying Forest - Wolfun Camp - Wolfen 25",
    "Flying Forest",
)

SUBZONE_PLAYTEST_RANGES = dict(SUBZONE_PLAYTEST_RANGES)
SUBZONE_PLAYTEST_RANGES["Flying Forest"] = [
    (1, 13, "Entrance", "confirmed"),
    (14, 25, "Wolfun Camp", "confirmed"),
    (26, 33, "Wolfun Factory", "strong"),
    (34, 37, "Brazul's Crow Chase", "strong"),
]
# Current descriptive split requested for the Quarry. Exact Wolfen boundaries
# outside the validated speed-board wall remain a playtest aid, not a runtime key change.
SUBZONE_PLAYTEST_RANGES["The Quarry"] = [
    (1, 7, "Wolfun Camp", "provisional"),
    (8, 10, "Wolfun Convoy Chase", "provisional"),
    (11, 19, "Quarry", "provisional"),
    (20, 31, "Arena", "strong"),
]

# Correct/complete Fast Travel identity mapping from the live run and the later
# classification audit. Existing Location IDs are preserved where the same FT
# number already existed; six newly exposed FT checks use new IDs.
FAST_TRAVEL_ZONE_KEY_TO_LOCATION = {
    _zone: dict(_mapping) for _zone, _mapping in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items()
}
FAST_TRAVEL_ZONE_KEY_TO_LOCATION["Flying Forest"] = {
    0x0DB7: "Flying Forest - Fast Travel 01",
    0x0E48: "Flying Forest - Fast Travel 02",
    0x0ED1: "Flying Forest - Fast Travel 03",
    0x0FB0: "Flying Forest - Fast Travel 04",
}
FAST_TRAVEL_ZONE_KEY_TO_LOCATION["Hunters Domain"] = {
    0x15EF: "Hunters Domain - Fast Travel 01",
    0x1197: "Hunters Domain - Fast Travel 02",
    0x1307: "Hunters Domain - Fast Travel 03",
    0x130D: "Hunters Domain - Fast Travel 04",
    0x15C5: "Hunters Domain - Fast Travel 05",
    0x123D: "Hunters Domain - Fast Travel 06",
}

_NEW_FT_LOCATION_IDS = {
    "Flying Forest - Fast Travel 03": 51474320,
    "Flying Forest - Fast Travel 04": 51474321,
    "Hunters Domain - Fast Travel 01": 51474322,
    "Hunters Domain - Fast Travel 04": 51474323,
    "Hunters Domain - Fast Travel 05": 51474324,
    "Hunters Domain - Fast Travel 06": 51474325,
}
LOCATION_NAME_TO_ID = dict(LOCATION_NAME_TO_ID)
LOCATION_NAME_TO_ID.update(_NEW_FT_LOCATION_IDS)

# Rebuild FT reverse metadata and ensure all new FT Locations belong to regions.
FAST_TRAVEL_LOCATION_ZONES = {
    _name: _zone
    for _zone, _mapping in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items()
    for _name in _mapping.values()
}
FAST_TRAVEL_KEY_TO_ZONES = {}
for _zone, _mapping in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items():
    for _key in _mapping:
        FAST_TRAVEL_KEY_TO_ZONES.setdefault(_key, []).append(_zone)

for _zone in ("Flying Forest", "Hunters Domain"):
    _existing = list(LOCATION_NAMES_BY_ZONE[_zone])
    for _name in FAST_TRAVEL_ZONE_KEY_TO_LOCATION[_zone].values():
        if _name not in _existing:
            _existing.append(_name)
    LOCATION_NAMES_BY_ZONE[_zone] = tuple(_existing)

# Rebuild collision-aware Wolfen reverse metadata after display-name corrections.
WOLFEN_KEY_TO_ZONES = {}
for _zone, _mapping in WOLFEN_ZONE_KEY_TO_LOCATION.items():
    for _key in _mapping:
        WOLFEN_KEY_TO_ZONES.setdefault(_key, []).append(_zone)
WOLFEN_KEY_TO_LOCATION = {
    _key: WOLFEN_ZONE_KEY_TO_LOCATION[_zones[0]][_key]
    for _key, _zones in WOLFEN_KEY_TO_ZONES.items()
}

# 0.7.8 RUNTIME HOTFIX: duplicate shop purchases can charge Nooties without changing stock/reward.
ADDR_GLOBAL_WOLFEN_COUNT = 0x004253D4
SHOP_LIVE_REWARD_RULES = {'Nativs City - Shop - Basic Boomy': {'address': 4346908, 'mode': 'level_gain_to', 'threshold': 1}, 'Nativs City - Shop - Yellow Bracelet': {'address': 4346916, 'mode': 'bit_gain', 'mask': 2}, 'Nativs City - Shop - Telescope': {'address': 4346948, 'mode': 'bool_gain'}, 'Nativs City - Shop - Magic Board': {'address': 4346964, 'mode': 'level_gain_to', 'threshold': 1}, 'Nativs City - Shop - Green Bracelet': {'address': 4346916, 'mode': 'bit_gain', 'mask': 4}, 'Nativs City - Shop - Climbing Gloves': {'address': 4346900, 'mode': 'bool_gain'}, 'Nativs City - Shop - Extra Energy Bar 1': {'address': 4346996, 'mode': 'life_gain', 'threshold': 100}, 'Nativs City - Shop - Blue Bracelet': {'address': 4346916, 'mode': 'bit_gain', 'mask': 8}, 'Nativs City - Shop - Jamgut Birdcall': {'address': 4346940, 'mode': 'bool_gain'}, 'Nativs City - Shop - Speed Board': {'address': 4346964, 'mode': 'level_gain_to', 'threshold': 2}, 'Nativs City - Shop - Golden Boomy': {'address': 4346908, 'mode': 'level_gain_to', 'threshold': 3}, 'Nativs City - Shop - Silver Bracelet': {'address': 4346916, 'mode': 'bit_gain', 'mask': 64}, 'Nativs City - Shop - Silver Boomy': {'address': 4346908, 'mode': 'level_gain_to', 'threshold': 2}, 'Nativs City - Shop - Brown Bracelet': {'address': 4346916, 'mode': 'bit_gain', 'mask': 16}, 'Nativs City - Shop - Magic Bouncers': {'address': 4346892, 'mode': 'bool_gain'}, 'Nativs City - Shop - Extra Energy Bar 2': {'address': 4346996, 'mode': 'life_gain', 'threshold': 150}, 'Nativs City - Shop - Black Bracelet': {'address': 4346916, 'mode': 'bit_gain', 'mask': 32}, 'Nativs City - Shop - Gold Bracelet': {'address': 4346916, 'mode': 'bit_gain', 'mask': 128}}


# ============================================================================
# 0.7.9 HARD PROGRESSION DEADLINES (2026-10-05)
# Live playtest corrections after the first 0.7.8 safe-logic run.
# - Jamgut must be obtainable in Flying Forest / The Root, never The Air Post+.
# - Speed Board (2nd Progressive Board) must be obtainable by Quarry Wolfun
#   Camp / Wolfun Convoy Chase. The Quarry proper begins after Wolfen 10.
# ============================================================================
PROTOTYPE_VERSION = "0.8.2-economy-draft"
AP_BUILD_VERSION = PROTOTYPE_VERSION
QUARRY_SPEED_LOCK_START = 11


# ============================================================================
# 0.8.3 RUN-SAFE ECONOMY 10 (2026-10-06)
# - Blue Egg remains known to the runtime/client for backwards compatibility,
#   but is no longer generated in new AP item pools. It is not required by logic.
# - Economy percentages are normalized to 10% steps by options.py.
# ============================================================================
ITEM_PROGRESSION_COUNTS = dict(ITEM_PROGRESSION_COUNTS)
ITEM_PROGRESSION_COUNTS.pop("Blue Egg", None)
PROTOTYPE_VERSION = "0.8.3-run-safe-economy10"
AP_BUILD_VERSION = PROTOTYPE_VERSION


# ============================================================================
# 0.8.4 FAST TRAVEL OPTIONS BETA (2026-10-07)
# - 21/21 allowed Fast Travel destinations retained; 10 unsafe/dead-end routes
#   are removed from new generated seeds.
# - One starting destination maximum per destination zone for the first beta.
# - Nativs City source-controller, C540 wind-controller, destination Master and
#   access-lock metadata are exported to the external Launcher.
# ============================================================================

# Physical Fast Travel locations retained in the AP pool after the destination
# audit. Names are the physical button numbers used by the final 21-route table.
_FAST_TRAVEL_BANNED_LOCATIONS = {
    "Flying Forest - Fast Travel 04",
    "Hunters Domain - Fast Travel 03",
    "Hunters Domain - Fast Travel 06",
    "Amber Quarry - Fast Travel 01",
    "The Root - Fast Travel 04",
    "Forgotten Island - Fast Travel 05",
    "Wolfen City - Fast Travel 01",
    "Wolfen City - Fast Travel 03",
    "Wolfen City - Fast Travel 04",
    "The Fortress - Fast Travel 01",
}

LOCATION_NAME_TO_ID = {
    _name: _id for _name, _id in LOCATION_NAME_TO_ID.items()
    if _name not in _FAST_TRAVEL_BANNED_LOCATIONS
}
for _zone in ZONE_ORDER:
    LOCATION_NAMES_BY_ZONE[_zone] = tuple(
        _name for _name in LOCATION_NAMES_BY_ZONE[_zone]
        if _name not in _FAST_TRAVEL_BANNED_LOCATIONS
    )

# Correct physical destination identities for the 21 allowed checks.
FAST_TRAVEL_ZONE_KEY_TO_LOCATION = {
    "Hunters Domain": {
        0x15EF: "Hunters Domain - Fast Travel 01",
        0x1197: "Hunters Domain - Fast Travel 02",
        0x1307: "Hunters Domain - Fast Travel 04",
        0x130D: "Hunters Domain - Fast Travel 05",
    },
    "The Root": {
        0x0A72: "The Root - Fast Travel 01",
        0x0ACE: "The Root - Fast Travel 02",
        0x0B54: "The Root - Fast Travel 03",
    },
    "Flying Forest": {
        0x0DB7: "Flying Forest - Fast Travel 01",
        0x0E48: "Flying Forest - Fast Travel 02",
        0x0ED1: "Flying Forest - Fast Travel 03",
    },
    "The Quarry": {
        0x2842: "The Quarry - Fast Travel 01",
        0x0AEA: "The Quarry - Fast Travel 02",
        0x0BF8: "The Quarry - Fast Travel 03",
    },
    "The Air Post": {
        0x0D8D: "The Air Post - Fast Travel 01",
        0x0DA5: "The Air Post - Fast Travel 02",
        0x0E18: "The Air Post - Fast Travel 03",
        0x0FF0: "The Air Post - Fast Travel 04",
    },
    "Forgotten Island": {
        0x073D: "Forgotten Island - Fast Travel 01",
        0x1115: "Forgotten Island - Fast Travel 02",
        0x063A: "Forgotten Island - Fast Travel 03",
        0x0620: "Forgotten Island - Fast Travel 04",
    },
}

FAST_TRAVEL_LOCATION_ZONES = {
    _name: _zone
    for _zone, _mapping in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items()
    for _name in _mapping.values()
}
FAST_TRAVEL_KEY_TO_ZONES = {}
for _zone, _mapping in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items():
    for _key in _mapping:
        FAST_TRAVEL_KEY_TO_ZONES.setdefault(_key, []).append(_zone)

# Nativs City source controllers. The first six are eligible for randomized
# starting destinations; Wolfen City/Fortress remain explicitly blocked.
NATIV_FAST_TRAVEL_SOURCE_KEYS = (
    0x0225, 0x022F, 0x0239, 0x0244, 0x024E, 0x0258, 0x0262, 0x026C,
)
NATIV_WIND_CONTROLLER_KEYS = {
    0x0225: 0x0226,
    0x022F: 0x0230,
    0x0239: 0x023A,
    0x0244: 0x0245,
    0x024E: 0x024F,
    0x0258: 0x0259,
    0x0262: 0x0263,
    0x026C: 0x026D,
}

# Includes banned peer endpoints so the Launcher can force every non-selected
# endpoint OFF in a loaded destination zone.
FAST_TRAVEL_DESTINATION_GROUPS = {
    0x0225: (0x15EF, 0x1197, 0x123D, 0x1307, 0x130D, 0x15C5),
    0x022F: (0x0A72, 0x0ACE, 0x0B54, 0x0C26),
    0x0239: (0x0DB7, 0x0E48, 0x0ED1, 0x0FB0),
    0x0244: (0x2842, 0x0AEA, 0x0BF8, 0x0088),
    0x024E: (0x0D8D, 0x0DA5, 0x0E18, 0x0FF0),
    0x0258: (0x073D, 0x1115, 0x063A, 0x0620, 0x0594),
}

# 21 validated source->destination routes. One route is chosen from each sampled
# zone; therefore starting_fast_travels is intentionally 1..6 in this beta.
FAST_TRAVEL_ALLOWED_ROUTES = {
    "Hunters Domain": (
        {"id": "hunters_01", "label": "Hunters Domain Fast Travel 01", "zone": "Hunters Domain", "source_key": 0x0225, "source_index": 0, "target_key": 0x15EF, "master_key": 0x15EE, "location_name": "Hunters Domain - Fast Travel 01"},
        {"id": "hunters_02", "label": "Hunters Domain Fast Travel 02", "zone": "Hunters Domain", "source_key": 0x0225, "source_index": 1, "target_key": 0x1197, "master_key": 0x1196, "location_name": "Hunters Domain - Fast Travel 02"},
        {"id": "hunters_04", "label": "Hunters Domain Fast Travel 04", "zone": "Hunters Domain", "source_key": 0x0225, "source_index": 3, "target_key": 0x1307, "master_key": 0x1306, "location_name": "Hunters Domain - Fast Travel 04"},
        {"id": "hunters_05", "label": "Hunters Domain Fast Travel 05", "zone": "Hunters Domain", "source_key": 0x0225, "source_index": 4, "target_key": 0x130D, "master_key": 0x130C, "location_name": "Hunters Domain - Fast Travel 05"},
    ),
    "The Root": (
        {"id": "root_01", "label": "The Root Fast Travel 01", "zone": "The Root", "source_key": 0x022F, "source_index": 0, "target_key": 0x0A72, "master_key": 0x0A71, "location_name": "The Root - Fast Travel 01"},
        {"id": "root_02", "label": "The Root Fast Travel 02", "zone": "The Root", "source_key": 0x022F, "source_index": 1, "target_key": 0x0ACE, "master_key": 0x0ADA, "location_name": "The Root - Fast Travel 02"},
        {"id": "root_03", "label": "The Root Fast Travel 03", "zone": "The Root", "source_key": 0x022F, "source_index": 2, "target_key": 0x0B54, "master_key": 0x0B53, "location_name": "The Root - Fast Travel 03"},
    ),
    "Flying Forest": (
        {"id": "flying_01", "label": "Flying Forest Fast Travel 01", "zone": "Flying Forest", "source_key": 0x0239, "source_index": 0, "target_key": 0x0DB7, "master_key": 0x0DB6, "location_name": "Flying Forest - Fast Travel 01"},
        {"id": "flying_02", "label": "Flying Forest Fast Travel 02", "zone": "Flying Forest", "source_key": 0x0239, "source_index": 1, "target_key": 0x0E48, "master_key": 0x0E47, "location_name": "Flying Forest - Fast Travel 02"},
        {"id": "flying_03", "label": "Flying Forest Fast Travel 03", "zone": "Flying Forest", "source_key": 0x0239, "source_index": 2, "target_key": 0x0ED1, "master_key": 0x0ED0, "location_name": "Flying Forest - Fast Travel 03"},
    ),
    "The Quarry": (
        {"id": "quarry_01", "label": "The Quarry Fast Travel 01", "zone": "The Quarry", "source_key": 0x0244, "source_index": 0, "target_key": 0x2842, "master_key": 0x2841, "location_name": "The Quarry - Fast Travel 01"},
        {"id": "quarry_02", "label": "The Quarry Fast Travel 02", "zone": "The Quarry", "source_key": 0x0244, "source_index": 1, "target_key": 0x0AEA, "master_key": 0x0AE9, "location_name": "The Quarry - Fast Travel 02"},
        {"id": "quarry_03", "label": "The Quarry Fast Travel 03", "zone": "The Quarry", "source_key": 0x0244, "source_index": 2, "target_key": 0x0BF8, "master_key": 0x0BF7, "location_name": "The Quarry - Fast Travel 03"},
    ),
    "The Air Post": (
        {"id": "airpost_01", "label": "The Air Post Fast Travel 01", "zone": "The Air Post", "source_key": 0x024E, "source_index": 0, "target_key": 0x0D8D, "master_key": 0x0D8C, "location_name": "The Air Post - Fast Travel 01"},
        {"id": "airpost_02", "label": "The Air Post Fast Travel 02", "zone": "The Air Post", "source_key": 0x024E, "source_index": 1, "target_key": 0x0DA5, "master_key": 0x0DA4, "location_name": "The Air Post - Fast Travel 02"},
        {"id": "airpost_03", "label": "The Air Post Fast Travel 03", "zone": "The Air Post", "source_key": 0x024E, "source_index": 2, "target_key": 0x0E18, "master_key": 0x0E17, "location_name": "The Air Post - Fast Travel 03"},
        {"id": "airpost_04", "label": "The Air Post Fast Travel 04", "zone": "The Air Post", "source_key": 0x024E, "source_index": 3, "target_key": 0x0FF0, "master_key": 0x0FEF, "location_name": "The Air Post - Fast Travel 04"},
    ),
    "Forgotten Island": (
        {"id": "forgotten_01", "label": "Forgotten Island Fast Travel 01", "zone": "Forgotten Island", "source_key": 0x0258, "source_index": 0, "target_key": 0x073D, "master_key": 0x073C, "location_name": "Forgotten Island - Fast Travel 01"},
        {"id": "forgotten_02", "label": "Forgotten Island Fast Travel 02", "zone": "Forgotten Island", "source_key": 0x0258, "source_index": 1, "target_key": 0x1115, "master_key": 0x1114, "location_name": "Forgotten Island - Fast Travel 02"},
        {"id": "forgotten_03", "label": "Forgotten Island Fast Travel 03", "zone": "Forgotten Island", "source_key": 0x0258, "source_index": 2, "target_key": 0x063A, "master_key": 0x0639, "location_name": "Forgotten Island - Fast Travel 03"},
        {"id": "forgotten_04", "label": "Forgotten Island Fast Travel 04", "zone": "Forgotten Island", "source_key": 0x0258, "source_index": 3, "target_key": 0x0620, "master_key": 0x061F, "location_name": "Forgotten Island - Fast Travel 04"},
    ),
}

# Runtime offsets and validated access blockers used by the matching Launcher.
ACTOR_FLAGS_OFFSET = 0x08
ACTOR_STATE_OFFSET = 0x104
ACTOR_PREV_STATE_OFFSET = 0x108
ACTOR_POS_X_OFFSET = 0x30
ACTOR_POS_Y_OFFSET = 0x34
ACTOR_POS_Z_OFFSET = 0x38
ADDR_KYA_ACTOR_GLOBAL = 0x00448E10
ADDR_CURRENT_MANA = 0x004525D8
FAST_TRAVEL_INDEX_OFFSET = 0x294
FAST_TRAVEL_INDEX_COPY_OFFSET = 0x298
FAST_TRAVEL_MASK_OFFSET = 0x29C
FAST_TRAVEL_ACTIVE_OFFSET = 0x2A0
FAST_TRAVEL_AVAILABLE_OFFSET = 0x2A4
FAST_TRAVEL_ROUTE_TABLE_OFFSET = 0x2BC
FAST_TRAVEL_ROUTE_READY_FLAG = 0x40000000
FAST_TRAVEL_DESTINATION_SINGLE_MASK = 0xFFFFFFFE
MASTER_EVENT_VTABLE = 0x0043C3F0
WIND_CONTROLLER_VTABLE = 0x0043C540
ACCESS_HANDLER_VTABLE = 0x0043BDA0
ACCESS_LOCK_DISABLE_BIT = 0x02000000
FLYING_FOREST_ELEVATOR_KEY = 0x0299
THE_ROOT_TARGET_KEY = 0x0A86
WIND_FLAG_CLEAR = 0x21
WIND_FLAG_SET_STAGE1 = 0x4100
WIND_FLAG_SET_STAGE2 = 0x0004
FAST_TRAVEL_MIN_RETURN_MANA = 3
FAST_TRAVEL_SOURCE_ARM_RADIUS = 10.0
FAST_TRAVEL_SOURCE_ARM_WINDOW = 6.0

PROTOTYPE_VERSION = "0.8.4-fasttravel-options"
AP_BUILD_VERSION = PROTOTYPE_VERSION

# v0.8.6: The game gives Basic Boomy after the introductory Wolfen.
# Progressive Boomy is now Silver/Golden (2 AP items, not 3).
ITEM_PROGRESSION_COUNTS = dict(ITEM_PROGRESSION_COUNTS)
ITEM_PROGRESSION_COUNTS[ITEM_PROGRESSIVE_BOOMY] = 2
PROTOTYPE_VERSION = "0.8.8-mapping-restored-086"

# 0.8.7 FT01 terrain logic patch — two NEW AP progression gate items.
# PAL SLES-51473: 0x048E / 0x02EA are persistent actor keys, not heap pointers.
ITEM_WOLFEN_CITY_ACCESS = "Wolfen City Access"
ITEM_FORTRESS_ACCESS = "The Fortress Access"
ITEM_NAME_TO_ID = dict(ITEM_NAME_TO_ID)
ITEM_NAME_TO_ID[ITEM_WOLFEN_CITY_ACCESS] = ITEM_ID_BASE + 45
ITEM_NAME_TO_ID[ITEM_FORTRESS_ACCESS] = ITEM_ID_BASE + 46
ITEM_PROGRESSION_COUNTS = dict(ITEM_PROGRESSION_COUNTS)
ITEM_PROGRESSION_COUNTS[ITEM_WOLFEN_CITY_ACCESS] = 1
ITEM_PROGRESSION_COUNTS[ITEM_FORTRESS_ACCESS] = 1
WOLFEN_CITY_ELEVATOR_KEY = 0x048E
FORTRESS_ELEVATOR_KEY = 0x02EA
PROTOTYPE_VERSION = "0.8.7-ft01-terrain-gates"
AP_BUILD_VERSION = PROTOTYPE_VERSION


# ============================================================================
# 0.8.8 — player-validated Flying Forest labels + FT04 + Rune-only magic cap.
# All existing location IDs are preserved. Added FF FT04 at ID 51474321.
# The 3 confusing Progressive Magic Gauge rewards are removed from NEW seeds;
# the launcher still understands old 0.8.7 item deliveries.
# ============================================================================
_FF_088_LABELS = {
    'Flying Forest - Wolfun Camp - Wolfen 21 - Scrawny Blue Outfit (Fists)': "Flying Forest - Brazul's Crow Chase - Wolfen 21 - Scrawny Blue Outfit (Fists)",
    'Flying Forest - Wolfun Camp - Wolfen 22 - Scrawny Blue Outfit (Fists)': "Flying Forest - Brazul's Crow Chase - Wolfen 22 - Scrawny Blue Outfit (Fists)",
    'Flying Forest - Wolfun Camp - Wolfen 23 - Scrawny Blue Outfit (Fists)': "Flying Forest - Brazul's Crow Chase - Wolfen 23 - Scrawny Blue Outfit (Fists)",
    "Flying Forest - Brazul's Crow Chase - Wolfen 35": 'Flying Forest - Wolfun Factory - Wolfen 35',
    "Flying Forest - Brazul's Crow Chase - Wolfen 36": 'Flying Forest - Wolfun Factory - Wolfen 36',
    "Flying Forest - Brazul's Crow Chase - Wolfen 37": 'Flying Forest - Wolfun Factory - Wolfen 37',
}
LOCATION_NAME_TO_ID = {_FF_088_LABELS.get(k,k):v for k,v in LOCATION_NAME_TO_ID.items()}
LOCATION_NAME_TO_ZONE = {_FF_088_LABELS.get(k,k):v for k,v in LOCATION_NAME_TO_ZONE.items()}
WOLFEN_ZONE_KEY_TO_LOCATION = {z:{k:_FF_088_LABELS.get(n,n) for k,n in m.items()} for z,m in WOLFEN_ZONE_KEY_TO_LOCATION.items()}
WOLFEN_LOCATIONS_BY_ZONE = {z:tuple(_FF_088_LABELS.get(n,n) for n in names) for z,names in WOLFEN_LOCATIONS_BY_ZONE.items()}
WOLFEN_KEY_TO_LOCATION = {k:_FF_088_LABELS.get(n,n) for k,n in WOLFEN_KEY_TO_LOCATION.items()}
WOLFEN_LOCATION_DESCRIPTIONS = {_FF_088_LABELS.get(k,k):v for k,v in WOLFEN_LOCATION_DESCRIPTIONS.items()}
LOCATION_NAMES_BY_ZONE = {z:tuple(_FF_088_LABELS.get(n,n) for n in names) for z,names in LOCATION_NAMES_BY_ZONE.items()}
BRACELET_ZONE_LOCATIONS = tuple(_FF_088_LABELS.get(n,n) for n in BRACELET_ZONE_LOCATIONS)
STARTER_LOCATION_NAME = _FF_088_LABELS.get(STARTER_LOCATION_NAME, STARTER_LOCATION_NAME)
SUBZONE_PLAYTEST_RANGES = dict(SUBZONE_PLAYTEST_RANGES)
SUBZONE_PLAYTEST_RANGES['Flying Forest'] = [
    (1,13,'Entrance','confirmed'),(14,20,'Wolfun Camp','confirmed'),
    (21,23,"Brazul's Crow Chase",'player-confirmed'),
    (24,25,'Wolfun Camp','confirmed'),(26,33,'Wolfun Factory','strong'),
    (34,34,"Brazul's Crow Chase",'strong'),
    (35,37,'Wolfun Factory','player-confirmed'),
]
# FF FT04 is a LOCAL discovery check, never an early-game starting route.
LOCATION_NAME_TO_ID = dict(LOCATION_NAME_TO_ID)
LOCATION_NAME_TO_ID['Flying Forest - Fast Travel 04'] = 51474321
LOCATION_NAME_TO_ZONE = dict(LOCATION_NAME_TO_ZONE)
LOCATION_NAME_TO_ZONE['Flying Forest - Fast Travel 04'] = 'Flying Forest'
FAST_TRAVEL_ZONE_KEY_TO_LOCATION = {z:dict(m) for z,m in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items()}
FAST_TRAVEL_ZONE_KEY_TO_LOCATION['Flying Forest'][0x0FB0] = 'Flying Forest - Fast Travel 04'
FAST_TRAVEL_LOCATION_ZONES = {n:z for z,m in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items() for n in m.values()}
FAST_TRAVEL_KEY_TO_ZONES = {}
for _zone, _map in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items():
    for _key in _map:
        FAST_TRAVEL_KEY_TO_ZONES.setdefault(_key,[]).append(_zone)
LOCATION_NAMES_BY_ZONE['Flying Forest'] = tuple(list(LOCATION_NAMES_BY_ZONE['Flying Forest']) + ['Flying Forest - Fast Travel 04'])
# Six rune AP items alone yield 350 mana and open Wolfen City.
ITEM_REWARD_COUNTS = dict(ITEM_REWARD_COUNTS)
ITEM_REWARD_COUNTS.pop(ITEM_PROGRESSIVE_MAGIC_GAUGE, None)
ITEM_USEFUL = frozenset(n for n in ITEM_USEFUL if n != ITEM_PROGRESSIVE_MAGIC_GAUGE)
PROTOTYPE_VERSION = '0.8.8-rune-ft04-subzones'
AP_BUILD_VERSION = PROTOTYPE_VERSION

# 0.8.9: data/ID-compatible with 0.8.8, placement rules revised.
PROTOTYPE_VERSION = "0.8.9-dynamic-map-logic"
AP_BUILD_VERSION = PROTOTYPE_VERSION

# 0.8.10: no user-selectable lock_root / lock_flying_forest; mode-derived.
PROTOTYPE_VERSION = "0.8.10-auto-ft-access"
AP_BUILD_VERSION = PROTOTYPE_VERSION

# 0.8.11: terrain-corrected Quarry progression gating (Wolfen 02-10 require Gloves).
PROTOTYPE_VERSION = "0.8.11-quarry-wolfen01-only"
AP_BUILD_VERSION = PROTOTYPE_VERSION


# ============================================================================
# 0.8.12 - AMBER QUARRY LOCAL FAST TRAVEL CHECK (2026-11-03)
# Re-enable the historical LOCATION ID (51474299) for a physical 0->1 pad
# activation observed in the user's read-only PINE Memory Probe V1.
# This is a LOCATION CHECK only. 0x0088 is NOT a validated Nativs City route,
# so it MUST NOT appear in FAST_TRAVEL_ALLOWED_ROUTES or starting FT choices.
# Keep all existing location/item IDs stable.
# ============================================================================
_AMBER_FT_LOCATION = 'Amber Quarry - Fast Travel 01'
_AMBER_FT_KEY = 0x0088
_AMBER_FT_LOCATION_ID = 51474299  # historic 0.7.3 ID, unused in 0.8.11
assert _AMBER_FT_LOCATION_ID not in LOCATION_NAME_TO_ID.values()
LOCATION_NAME_TO_ID = dict(LOCATION_NAME_TO_ID)
LOCATION_NAME_TO_ID[_AMBER_FT_LOCATION] = _AMBER_FT_LOCATION_ID
LOCATION_NAME_TO_ZONE = dict(LOCATION_NAME_TO_ZONE)
LOCATION_NAME_TO_ZONE[_AMBER_FT_LOCATION] = 'Amber Quarry'
LOCATION_NAMES_BY_ZONE = {z:tuple(v) for z,v in LOCATION_NAMES_BY_ZONE.items()}
assert _AMBER_FT_LOCATION not in LOCATION_NAMES_BY_ZONE['Amber Quarry']
LOCATION_NAMES_BY_ZONE['Amber Quarry'] += (_AMBER_FT_LOCATION,)
FAST_TRAVEL_ZONE_KEY_TO_LOCATION = {z:dict(v) for z,v in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items()}
FAST_TRAVEL_ZONE_KEY_TO_LOCATION['Amber Quarry'] = {_AMBER_FT_KEY: _AMBER_FT_LOCATION}
FAST_TRAVEL_LOCATION_ZONES = {
    name: zone for zone, mapping in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items()
    for name in mapping.values()
}
FAST_TRAVEL_KEY_TO_ZONES = {}
for zone, mapping in FAST_TRAVEL_ZONE_KEY_TO_LOCATION.items():
    for key in mapping:
        FAST_TRAVEL_KEY_TO_ZONES.setdefault(key, []).append(zone)
assert all(int(r.get('target_key', -1)) != _AMBER_FT_KEY
           for routes in FAST_TRAVEL_ALLOWED_ROUTES.values() for r in routes)
PROTOTYPE_VERSION = '0.8.12-amber-local-check'
AP_BUILD_VERSION = PROTOTYPE_VERSION


# 0.8.13 - Lava Worm guarded beta location.
# Memory Probe: ScenarioVar[4] 0->1 followed by same-scene actor state
# 0x03->0x11. Launcher requires both live edges; never use ScenarioVar alone.
_LAVA_WORM_LOCATION = 'Flying Forest - Lava Worm Defeated'
assert _LAVA_WORM_LOCATION not in LOCATION_NAME_TO_ID
_LAVA_WORM_LOCATION_ID = max(LOCATION_NAME_TO_ID.values()) + 1
LOCATION_NAME_TO_ID = dict(LOCATION_NAME_TO_ID)
LOCATION_NAME_TO_ID[_LAVA_WORM_LOCATION] = _LAVA_WORM_LOCATION_ID
LOCATION_NAME_TO_ZONE = dict(LOCATION_NAME_TO_ZONE)
LOCATION_NAME_TO_ZONE[_LAVA_WORM_LOCATION] = 'Flying Forest'
LOCATION_NAMES_BY_ZONE = {z: tuple(v) for z,v in LOCATION_NAMES_BY_ZONE.items()}
LOCATION_NAMES_BY_ZONE['Flying Forest'] += (_LAVA_WORM_LOCATION,)
PROTOTYPE_VERSION = '0.8.13-lava-witness-map-zoom'
AP_BUILD_VERSION = PROTOTYPE_VERSION

# 0.8.14: FT safety. No item/location IDs added or renamed; new seed required
# solely to enforce no advancement items on unresolved FT checks.
PROTOTYPE_VERSION = '0.8.14-ft-safe-shop-audit'
AP_BUILD_VERSION = PROTOTYPE_VERSION


# ==========================================================================
# 0.8.14.1 BETA LOGIC HOTFIX (2026-11-04)
# ZERO Archipelago reward/check locations in Wolfen City. The City remains a
# physical Region and its Wolfen keys stay known for scene/zone identification.
# Launcher data/core.json + wolfen.json + zones.json must be updated to the
# matching tables to avoid stale check submissions. No EXE recompile needed.
# Keep the existing slot_data prototype_version for launcher 0.9.63 hardcoded
# compatibility checks (Amber/Lava). The hotfix marker below identifies the
# new logic revision. Existing rooms are not retroactively modified.
# ==========================================================================
_WOLFEN_CITY_DISABLED_NAMES = frozenset(LOCATION_NAMES_BY_ZONE['Wolfen City'])
assert len(_WOLFEN_CITY_DISABLED_NAMES) == 41, len(_WOLFEN_CITY_DISABLED_NAMES)
assert len(WOLFEN_LOCATIONS_BY_ZONE['Wolfen City']) == 40
LOCATION_NAME_TO_ID = {name: ident for name, ident in LOCATION_NAME_TO_ID.items()
                       if name not in _WOLFEN_CITY_DISABLED_NAMES}
LOCATION_NAME_TO_ZONE = {name: zone for name, zone in LOCATION_NAME_TO_ZONE.items()
                         if name not in _WOLFEN_CITY_DISABLED_NAMES}
LOCATION_NAMES_BY_ZONE = dict(LOCATION_NAMES_BY_ZONE)
LOCATION_NAMES_BY_ZONE['Wolfen City'] = ()
WOLFEN_LOCATIONS_BY_ZONE = dict(WOLFEN_LOCATIONS_BY_ZONE)
WOLFEN_LOCATIONS_BY_ZONE['Wolfen City'] = ()
WOLFEN_ZONE_KEY_TO_LOCATION = dict(WOLFEN_ZONE_KEY_TO_LOCATION)
WOLFEN_ZONE_KEY_TO_LOCATION['Wolfen City'] = {}
# Preserve WOLFEN_KEY_TO_ZONES and WOLFEN_KEY_TO_LOCATION for scene recognition.
SPECIAL_LOCATION_CONDITIONS = {name: cond for name, cond in SPECIAL_LOCATION_CONDITIONS.items()
                               if name not in _WOLFEN_CITY_DISABLED_NAMES}
SPECIAL_LOCATION_ZONES = {name: zone for name, zone in SPECIAL_LOCATION_ZONES.items()
                          if name not in _WOLFEN_CITY_DISABLED_NAMES}
BRACELET_ZONE_LOCATIONS = tuple(
    ('Hunters Domain - Wind Tower - Wolfen 01 - Scrawny Blue Outfit (Rocket Gun)' if name.startswith('Wolfen City - ') else name)
    for name in BRACELET_ZONE_LOCATIONS
)
assert len(BRACELET_ZONE_LOCATIONS) == 7 and len(set(BRACELET_ZONE_LOCATIONS)) == 7
assert all(name in LOCATION_NAME_TO_ID for name in BRACELET_ZONE_LOCATIONS)
assert not any(name.startswith('Wolfen City - ') for name in LOCATION_NAME_TO_ID)
KYA_LOGIC_HOTFIX = '2026-11-04-wolfen-city-no-locations-ap-root-entrance'
