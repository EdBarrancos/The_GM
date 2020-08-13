""" 
    File: dice.py
    Author: Eduardo Barrancos
    Description: Manage the dice related funcitons
"""
import random

from dice_aux.dice import Dice
from dice_aux.error import Error
from constant_dice_main import *
from dice_aux.helful_functions import *
from quicksort import quicksort


class Roll:
    async def roll_dice(self, context, _input, helpCommand='help'):
        """ To add an Option:
            Expect a new index in the tuple
            Add a new index and the condicitons for it in the flag
            Add it to help """          
        self.context = context
        self.helpCommand = helpCommand

        dice = _input[0].lower()
        dice = dice.split('d')

        if len(dice) == 1:
            dice = dice[0]
            #Input not formated properly
            return await self.somethingWentWrong("Dice information not introduced properly.")
        else:
            i = await self.getDiceInfo(dice)
            if i == self: return self

            self.options = dice[1][i:].lower()
            for i in range(1,len(_input)):
                self.options += _input[i].lower()
        
            optionFlags = await self.getOptionsFlags()
            if optionFlags == self: return self
            # 0 -> Keep dice out of the roll
            # 1 -> Reroll values
            # 2 -> Target number for a success
            # 3 -> Target number for a failure

            roll = await self.rolling()
            roll = await quicksort(roll, 0, len(roll) - 1, comparator=lambda a,b: a > b)

            for index, option in enumerate(optionFlags):
                if option:
                    if index == 0:
                        # Keep dice out of the roll
                        roll = roll[:int(option)]
                        continue

            await self.context.send(f'{self.context.author.mention} rolled:`{roll}`')
            
            

            if await crited(roll, self.typeDice, self.modifier):
                await self.crit(roll.count(eval(f'{self.typeDice}{self.modifier}')))

            return self
    
    async def processInputDice(self, _input):
        #get the num dice
        dice = self.getDiceInfo(self, _input)
        self.numDice, self.typeDice = dice["numDice"], dice["typeDice"], dice["InputStoppingPoint"]
        #get the type dice
        
        #get the options
        
    async def getDiceInfo(self, dice):
        """ Finds the number of dice and the type. 
            Returns the position of the options"""
        if dice[0] == EMPTYSTRING:
            self.numDice = 1
        else:
            try:
                self.numDice = int(dice[0])
            except ValueError:
                return await self.somethingWentWrong("Dice information not introduced properly.")

        if self.numDice <= 0: return await self.somethingWentWrong("Dice information not introduced properly.")

        self.typeDice = EMPTYSTRING
        counter = 0
        size_dice = len(dice[1])
        while counter < size_dice and (await isNumber(dice[1][counter])):
            self.typeDice += dice[1][counter]
            counter += 1
        
        try:
            self.typeDice = int(self.typeDice)
        except ValueError:
            return await self.somethingWentWrong("Dice information not introduced properly.")
        
        if self.typeDice <= 0: return await self.somethingWentWrong("Dice information not introduced properly.")

        return counter
    

    async def crit(self, totalNumbCrits):
        """ Celebrative message for the Critical hit """
        critTimesStr = f'{totalNumbCrits} times!'
        if totalNumbCrits == 1:
            critTimesStr = EMPTYSTRING

        msg = await self.context.send(f'F*** YEAH!! {self.context.author.mention} JUST CRITED! {critTimesStr}')
        await msg.add_reaction(StarStruck)
        await msg.add_reaction(MindBlowen)
        await msg.add_reaction(Cursing)
        await msg.add_reaction(PartyTime)

        return self


    async def rolling(self):
        """ Returns a list with each individual rolls.
                self.numDice elements each from 1 to self.typeDice  """

        rolls = list()
        for _ in range(self.numDice):
            rolls.append(eval(f'{random.randint(STARTROLL, self.typeDice)}{self.modifier}'))
            await asyncio.sleep(0.02)
        return rolls


    async def getOptionsFlags(self):
        """ Return the options for this roll and checks for modifiers """

        flag = list()
        for _ in range(NumberOfOptions):
            flag.append(EMPTYSTRING)

        extractingOp = 0
        # 0 -> No op
        # 1 -> Found a op
        # 2 -> Found at least a number
        extractingMod = 0
        # 0 -> No mod
        # 1 -> Found a mod
        # 2 -> Found at least a number
        self.modifier = EMPTYSTRING

        for i in self.options:
            if extractingOp == 2:
                #Last State
                if await isNumber(i):
                    flag[index] += i
                else:
                    extractingOp = 0

            elif extractingMod == 2:
                #Last State
                if await isNumber(i):
                    self.modifier += i
                else:
                    extractingMod = 0

            if extractingOp == 0 and extractingMod == 0:
                # Idle State
                # Searching
                if i in Operators:
                    self.modifier += i
                    extractingMod = 1
                elif i in OptionsWNumber:
                    index = OptionsWNumber.index(i)
                    extractingOp = 1
                elif i in Options:
                    index = len(OptionsWNumber) + Options.index(i)
                    flag[index] = ACTIVE
                    extractingOp = 2

            elif extractingOp == 1:
                # Transition State
                if await isNumber(i):
                    if flag[index] == None: flag[index] = i
                    else: flag[index] += i
                    extractingOp = 2
                else: return await somethingWentWrong("Options wrongly formated") 

            elif extractingMod == 1:
                # Transition State
                if await isNumber(i):
                    self.modifier += i
                    extractingMod = 2
                else: return await somethingWentWrong("Options wrongly formated")
        
        if extractingOp == 1 or extractingMod == 1: return await self.somethingWentWrong("Options wrongly formated")
        return flag
    
    

async def crited(listOfRolls: list, typeDice: str, modifier: str) -> bool:
        """ In list_of_roll is there a maximum value? """
        return eval(f'{typeDice}{modifier}') in listOfRolls  