import math, sys, random
from pprint import pprint
from enum import Enum

RANDOM_WORDS = ["altar", "corpse", "monster", "fire", "lightning", "water", "lava", "garbage", "venom", "gas", "ice", "power", "scrolls", "potions", "weapons", "statuses", "friendship", "persuasion", "tree", "stone", "void", "sand", "wind", "directions", "wild magic", "dragons", "kobolds", "alcohol", "food", "dreams", "time", "space", "portals", "spell slots", "rope", "sunlight", "moonlight"]

class Dice(Enum):
	d4 = "d4"
	d6 = "d6"
	d8 = "d8"
	d10 = "d10"
	d12 = "d12"
	d20 = "d20"

class DamageType(Enum):
	FIRE = "fire"
	LIGHTNING = "lightning"
	COLD = "cold"
	FORCE = "force"
	PSYCHIC = "psychic"
	THUNDER = "thunder"
	PIERCING = "piercing"
	SLASHING = "slashing"
	BLUDGEONING = "bludgeoning"
	RADIANT = "radiant"
	NECROTIC = "necrotic"
	POISON = "poison"
	ACID = "acid"

class Status(Enum):
	GRAPPLED = "grappled"
	PRONE = "prone"
	POISONED = "poisoned"
	EXHAUSTED = "exhausted"
	DEAFENED = "deafened"
	BLINDED = "blinded"
	CHARMED = "charmed"
	FRIGHTENED = "frightened"
	PARALYZED = "paralyzed"
	PETRIFIED = "petrified"
	RESTRAINED = "restrained"

class Schools(Enum):
	EVOCATION = "evocation"
	ILLUSION = "illusion"
	NECROMANCY = "necromancy"
	CONJURATION = "conjuration"
	DIVINATION = "divination"
	TRANSMUTATION = "transmuation"
	ABJURATION = "abjuration"
	ENCHANTMENT = "enchantment"

RANGE = [5, 10, 20, 30, 45, 60, 80, 100, 120]
AREA = ["cone", "line", "sphere", "cube"]
STAT = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]	

AVG_PARTY_LEVEL = 0 # affects dice type and min/max # of special actions, actions, BAs, reactions, statuses, hp, ability recharge
ENCOUNTER_DIFFICULTY = 0 # affects # of dice, probability of statuses, skill mod

class Enemy:
	MIN = 0
	MAX = 0
	PROBABILITY = 0.0
	
	name = ""
	hp = 0
	DC = 0
	spellcaster = False
	maxslotlevel = 0
	numberofspells = 0
	statmods = {} #empty dictionary to be generated using STAT[]
	goodstats = []
	badstats = []
	profbonus = 0
	move = 30
	resistances = []
	vuls = []
	immunities = []
	# turn based
	multiattack = 0
	actions = {}
	bonusactions = {}
	reactions = {}

	specialactions = {} # air/legendary
	abilityrecharge = 0

	def __init__(self, ENCOUNTER_DIFFICULTY, AVG_PARTY_LEVEL, STAT, RANGE, AREA):
		# init variables here
		if ENCOUNTER_DIFFICULTY == 1:
			self.MIN = 2
			self.MAX = 4
			self.PROBABILITY = 0.05
			self.multiattack = 1
		elif ENCOUNTER_DIFFICULTY == 2:
			self.MIN = 4
			self.MAX = 7
			self.PROBABILITY = 0.1
			roll_oof = random.random()
			if roll_oof <= self.PROBABILITY/3:
				self.resistances.append("All")
			self.multiattack = 2
		elif ENCOUNTER_DIFFICULTY == 3:
			self.MIN = 7
			self.MAX = 9
			self.PROBABILITY = 0.2
			self.multiattack = 3
		elif ENCOUNTER_DIFFICULTY == 4: # fucking lol
			self.MIN = random.randint(1, 8)
			self.MAX = random.randint(self.MIN, 10)
			self.PROBABILITY = random.random()
			self.multiattack = random.randint(1, self.MAX)
		else:
			print("Incorrect input, obey the instructions...")
			sys.exit()
		self.generate_info(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY)
		self.generate_stats(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, STAT)
		self.generate_actions(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, RANGE, AREA)
		return

	def generate_actions(self, AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, RANGE, AREA):
		# generate actions, special actions, BAs, reactions and recharge timers
		if 'WIS' in self.goodstats or 'CHA' in self.goodstats or 'INT' in self.goodstats:
			# spellcastchance = random.random()
			# if spellcastchance <= 0.5:
			self.spellcaster = True
			self.maxslotlevel = ENCOUNTER_DIFFICULTY + random.randint(math.floor(AVG_PARTY_LEVEL/3), math.floor(AVG_PARTY_LEVEL/2))
			self.numberofspells = random.randint(self.MIN, self.MAX) + ENCOUNTER_DIFFICULTY
			self.actions[random.choice(list(Schools)).value + ' magic spellcasting'] = "Can cast " + str(self.numberofspells) + " spells of school at max slot level " + str(self.maxslotlevel)
		#if ('STR' or 'DEX') in self.goodstats:
		diceresults = self.dice_picker(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY)
		self.actions['Attack Action'] = 'This creature has ' + str(self.multiattack) + ' multiattacks. To hit: Whatever attack stat you choose + ' + str(self.profbonus) + '. Each attack does ' + diceresults[0] + diceresults[1] + ' + ability modifier (that is used to attack) damage.' 
		
		#TODO: GENERATE ACTION ORIENTED ABILITIES NEXT
		print(self.actions)

		return

	def generate_stats(self, AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, STAT):
		# generate profbonus and statmods
		self.profbonus = random.randint(self.MIN, self.MAX) + ENCOUNTER_DIFFICULTY
		statlist = STAT
		random.shuffle(statlist)
		self.goodstats = [statlist[0], statlist[1], statlist[2]] # lol i used to be a good programmer some time ago
		self.badstats = [statlist[3], statlist[4], statlist[5]] # note for self use split operator

		for stat in self.goodstats:
			mod = random.randint(self.MIN, self.MAX)
			self.statmods[stat] = mod
		for stat in self.badstats:
			mod = random.randint(self.MIN, self.MAX) - random.randint(self.MIN, self.MAX)
			self.statmods[stat] = mod
		print(self.statmods)
		return

	def generate_info(self, AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY):
		self.hp = random.randint(self.MIN, self.MAX) * AVG_PARTY_LEVEL * ENCOUNTER_DIFFICULTY
		self.DC = 8 + math.ceil((AVG_PARTY_LEVEL/2)) + ENCOUNTER_DIFFICULTY
		# need to change above formulae, they break down at higher levels
		self.move = random.choice([self.move + 5*ENCOUNTER_DIFFICULTY, self.move - 5*ENCOUNTER_DIFFICULTY, self.move])

		for data in DamageType:
			roll_res = random.random()
			roll_vul = random.random()
			if roll_res <= self.PROBABILITY:
				if "All" not in self.resistances:
					self.resistances.append(data.value)
			if roll_vul <= (self.PROBABILITY/ENCOUNTER_DIFFICULTY):
				self.vuls.append(data.value)

		roll_imm = random.random()
		if roll_imm <= self.PROBABILITY:
			if roll_imm <= self.PROBABILITY/2:
				self.immunities.append(random.choice(list(DamageType)).value)
			self.immunities.append(random.choice(list(DamageType)).value)

		print(self.resistances)
		print(self.vuls)
		print(self.immunities)
		return

	def dice_picker(self, AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY): # returns two strings
	# return no. of dice and dice type based on encounter difficulty and scaled for avg party level
	# encounter difficulty is tied to number of dice, and dice type to avg party level
		numberofdice = random.randint(math.ceil(ENCOUNTER_DIFFICULTY/2), ENCOUNTER_DIFFICULTY)
		if 'STR' in self.goodstats:
			dicetype = random.choice([Dice.d8.value, Dice.d10.value, Dice.d12.value])
		elif 'DEX' in self.goodstats:
			dicetype = random.choice([Dice.d6.value, Dice.d8.value])
		else:
			dicetype = random.choice([Dice.d4.value, Dice.d6.value])
			numberofdice = 1
		
		# numberofdice = random.randint(1, ENCOUNTER_DIFFICULTY-1)

		return str(numberofdice), dicetype


def main(): 
	# fetch user prefs for enemies here and accordingly make enemies
	print("hello!")
	ENCOUNTER_DIFFICULTY = int(input("How difficult is this creature? 1 = Easy, 2 = Medium, 3 = Hard, 4 = ???: "))
	AVG_PARTY_LEVEL = int(input("Enter the avg party level, rounded up to the nearest integer: "))
	enemy = Enemy(ENCOUNTER_DIFFICULTY, AVG_PARTY_LEVEL, STAT, RANGE, AREA)
	print(enemy.__dict__)

if __name__ == '__main__':
	main()