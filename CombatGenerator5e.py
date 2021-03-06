import math, sys, random
from pprint import pprint
from enum import Enum

RANDOM_WORDS = ["altar", "corpse", "monster", "fire", "lightning", "water", "lava", "garbage", "venom", "gas", "ice", "power", "scrolls", "potions", "weapons", "statuses", "friendship", "persuasion", "tree", "stone", "void", "sand", "wind", "directions", "wild magic", "dragons", "kobolds", "alcohol", "food", "dreams", "time", "space", "portals", "spell slots", "rope", "sunlight", "moonlight", "animal", "veil", "horror", "random"]
SPECIAL = ["Teleport", "Spawn Adds", "Change the battlefield to advantage", "Use Damage dealing ability", "Drain resource", "Sacrifice Resource", "Gain Theme Relevant Buff", "Apply Theme Relevant Debuff", "Take a stance/charge", "Empower next action", "Manipulate item(s)", ""]
DESPRERATION = ["Apply Party Wide Debuff", "Do Party Wide Damage", "Use battlefield to run away", "cast most powerful spell available if spellcaster, else multiattack", "Use another special action but more dangerous", "Self-destruct", "Spawn Lots of Adds", "Empower next action"]
REACTIONS = ["Parry/Riposte", "Reflect some damage", "Cast a low level spell", "Sacrifice Resource", "Gain Resource"]
# effectively every time a special action is generated, it'll chain once by randomly picking another entry in the list
# that way each entry is at least vaguely cohesive with another action, narratively
# adding more verb-adjective pairs as we go along
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
	AC = 0
	spellcaster = False
	maxslotlevel = 0
	numberofspells = 0
	statmods = {} # empty dictionary to be generated using STAT[]
	goodstats = []
	badstats = []
	profbonus = 0 # note to self: might need to fix this calculation, too stronk atm?
	move = 30
	resistances = []
	vuls = []
	immunities = []
	# turn based
	multiattack = 0
	actions = {}
	reactions = {}
	desperationactions = {} # how does the creature respond to player wincons? low health?
	specialactions = {} # lair/legendary/bonus actions
	abilityrecharge = 0

	def __init__(self, ENCOUNTER_DIFFICULTY, AVG_PARTY_LEVEL, STAT, RANGE, AREA, SPECIAL, REACTIONS):
		# init variables here
		# change these values to balance encounters based on your party's composition
		# self.PROB dictates probabilities to beat in order to generate special actions, resistances, imms etc.
		# reduce to make encounter easier
		# MIN, MAX -> static int range for calculations, lower both to make generated encounters easier, vice versa
		if ENCOUNTER_DIFFICULTY == 1:
			self.MIN = 2
			self.MAX = 4
			self.PROBABILITY = 0.05
			self.multiattack = 1
		elif ENCOUNTER_DIFFICULTY == 2:
			self.MIN = 5
			self.MAX = 7
			self.PROBABILITY = 0.1
			roll_oof = random.random()
			if roll_oof <= self.PROBABILITY/(3-ENCOUNTER_DIFFICULTY):
				self.resistances.append("All")
			self.multiattack = 2
		elif ENCOUNTER_DIFFICULTY == 3:
			self.MIN = 7
			self.MAX = 9
			self.PROBABILITY = 0.2
			self.multiattack = 3
			roll_oof = random.random()
			if roll_oof <= self.PROBABILITY:
				self.resistances.append("All")
		elif ENCOUNTER_DIFFICULTY == 4: # fucking lol
			self.MIN = random.randint(1, 8)
			self.MAX = random.randint(self.MIN, 10)
			self.PROBABILITY = random.random()
			self.multiattack = random.randint(1, self.MAX)
			roll_oof = random.random()
			if roll_oof <= self.PROBABILITY/(3-ENCOUNTER_DIFFICULTY):
				self.resistances.append("All")
		else:
			print("Incorrect input, obey the instructions...")
			sys.exit()
		self.generate_info(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY)
		self.generate_stats(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, STAT)
		self.generate_actions(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, RANGE, AREA, SPECIAL, REACTIONS)

		return

	def generate_actions(self, AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, RANGE, AREA, SPECIAL, REACTIONS):
		# generate actions, special actions, BAs, reactions and recharge timers
		if 'WIS' in self.goodstats or 'CHA' in self.goodstats or 'INT' in self.goodstats:
			# spellcastchance = random.random()
			# if spellcastchance <= 0.5: What if spellcasting was a chance?
			self.spellcaster = True
			self.maxslotlevel = ENCOUNTER_DIFFICULTY + random.randint(math.floor(AVG_PARTY_LEVEL/3), math.floor(AVG_PARTY_LEVEL/2))
			self.numberofspells = random.randint(self.MIN, self.MAX) + ENCOUNTER_DIFFICULTY
			self.actions[random.choice(list(Schools)).value + ' magic spellcasting'] = "Can cast " + str(self.numberofspells) + " spells of school at max slot level " + str(self.maxslotlevel)
	
		diceresults = self.dice_picker(AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY)
		self.actions['Attack Action'] = 'This creature has ' + str(self.multiattack) + ' multiattacks. To hit: Whatever attack stat you choose + ' + str(self.profbonus) + '. Each attack does ' + diceresults[0] + diceresults[1] + ' + ability modifier (that is used to attack) damage.' 
		
		# GENERATE ACTION ORIENTED ABILITIES NEXT
		reactionchance = random.random() # chance to have a reaction
		if reactionchance <= self.PROBABILITY:
			self.actions['Reaction'] = 'This creature can ' + random.choice(REACTIONS) + ' once per round'

		# grant at least two special actions
		i = 1
		tempspeciallist = SPECIAL
		randomspecial = random.choice(tempspeciallist)
		self.abilityrecharge = random.randint(0, 3)
		self.specialactions['Special Action ' + str(i)] = 'This creature may ' + str(randomspecial) + ' on an ability cooldown of ' + str(self.abilityrecharge) + ' rounds'
		i += 1
		tempspeciallist.remove(randomspecial)
		randomspecial = random.choice(tempspeciallist)
		self.abilityrecharge = random.randint(1, 3)
		self.specialactions['Special Action ' + str(i)] = 'This creature may ' + str(randomspecial) + ' on an ability cooldown of ' + str(self.abilityrecharge) + ' rounds'
		i += 1
		tempspeciallist.remove(randomspecial)

		# Pick a desperation action, reaction to player's tactics
		j = 1
		tempdesplist = DESPRERATION
		randomdesp = random.choice(tempdesplist)
		self.desperationactions['Desperation Action ' + str(j)] = 'This creature may ' + str(randomdesp) + ' once per combat'

		# how many special actions can a lad have :?
		while(True):
			morespecialchance = random.random()
			if morespecialchance <= self.PROBABILITY:
				randomspecial = random.choice(tempspeciallist)
				self.specialactions['Special Action ' + str(i)] = 'This creature may ' + str(randomspecial) + ' on an ability cooldown of ' + str(self.abilityrecharge) + ' rounds'
				i += 1
				tempspeciallist.remove(randomspecial)
			else:
				break

		return

	def generate_stats(self, AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY, STAT):
		# generate profbonus and statmods
		# note to self: need to find a better way to generate good and bad stats
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
		return

	def generate_info(self, AVG_PARTY_LEVEL, ENCOUNTER_DIFFICULTY):
		# generate basic statblock stats
		self.hp = random.randint(self.MIN, self.MAX) * AVG_PARTY_LEVEL * ENCOUNTER_DIFFICULTY
		self.DC = 8 + math.ceil(random.randint(self.MIN, self.MAX)/2) + ENCOUNTER_DIFFICULTY
		# need to change above formulae, they break down at higher levels a little bit
		self.move = random.choice([self.move + 5*ENCOUNTER_DIFFICULTY, self.move - 5*ENCOUNTER_DIFFICULTY, self.move])
		self.AC = 8 + random.randint(self.MIN, self.MAX)

		for data in DamageType:
			roll_res = random.random()
			roll_vul = random.random()
			if roll_res <= self.PROBABILITY*ENCOUNTER_DIFFICULTY:
				if "All" not in self.resistances:
					self.resistances.append(data.value)
			if roll_vul <= (self.PROBABILITY):
				self.vuls.append(data.value)

		roll_imm = random.random()
		if roll_imm <= self.PROBABILITY:
			if roll_imm <= self.PROBABILITY/2:
				self.immunities.append(random.choice(list(DamageType)).value)
			self.immunities.append(random.choice(list(DamageType)).value)

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
	print("I heard ya tryna make a creature :3")
	print()
	ENCOUNTER_DIFFICULTY = int(input("How difficult is this creature? 1 = Easy, 2 = Medium, 3 = Hard, 4 = ???: "))
	AVG_PARTY_LEVEL = int(input("Enter the avg party level, rounded up to the nearest integer: "))
	enemy = Enemy(ENCOUNTER_DIFFICULTY, AVG_PARTY_LEVEL, STAT, RANGE, AREA, SPECIAL, REACTIONS)
	print()
	print("Here is a generated stat block, feel free to modfy it and use it as a crafting constraint vs. an out of book guideline to follow:")
	print('\n\n')
	print("Hitpoints: " + str(enemy.hp))
	print("Armor Class: " + str(enemy.AC))
	print("Spell Save DC and DC for other relevant abilities: " + str(enemy.DC))
	print("For attacks and ability checks, you may use proficiency bonus of: " + str(enemy.profbonus))
	print("This creature's movement speed is: " + str(enemy.move) + " ft.")
	if enemy.spellcaster:
		print("This creature is a spellcaster... of some sort")
		#print("The max level of spell slot is: " + str(enemy.maxslotlevel))
		#print("The max number of spells this creature can cast is: " + str(enemy.numberofspells))
	else:
		print("This creature doesn't cast spells, but they can do other cool things!")
	print()
	print("This is the creature's stat mods (instead of scores):")
	for key in enemy.statmods:
		print(str(key) + ": " + str(enemy.statmods[key]))
	print()
	if enemy.resistances:
		print("This creature is resistant to: " + str(enemy.resistances))
	if enemy.vuls:
		print("This creature is vulnerable to: " + str(enemy.vuls))
	if enemy.immunities:
		print("This creature is immune to: " + str(enemy.immunities))
	print()
	print("List of creature's Actions: ")
	print("For an attack action, this creature can make a maximum of " + str(enemy.multiattack) + " attacks")
	for key in enemy.actions:
		print(str(key) + ": " + str(enemy.actions[key]))
	print()
	if enemy.reactions:
		print("List of Reactions:")
	for key in enemy.reactions:
		print(str(key) + ": " + str(enemy.reactions[key]))
	print()
	print("List of Special Actions (taken after a player turn or can be used as bonus action): ")
	for key in enemy.specialactions:
		print(str(key) + ": " + str(enemy.specialactions[key]))

	print()
	print("List of desperation actions that the creature will take when desperate:")
	for key in enemy.desperationactions:
		print(str(key) + ": " + str(enemy.desperationactions[key]))

	print()
	print("Lastly here are some random words to help you improvise:")
	tempranlist = RANDOM_WORDS
	for i in range(1, 4):
		ranword = random.choice(tempranlist)
		print(ranword)
		tempranlist.remove(ranword)

	# print(enemy.__dict__)

if __name__ == '__main__':
	main()