'''
MIT License

Copyright (c) 2020 Georg Thurner

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
'''
########################################################################################################################################

'''
A simple object oriented implementation of an enigma machine
'''
import string


INT_TO_LETTER = tuple(string.ascii_uppercase)
LETTER_TO_INT = { INT_TO_LETTER[i] : i for i in range(26) }

# This is not a full usefull monoalphabetical substitution class only the parts necessary for enigma
class MonoalphabetSubstitution:
	'''
	Takes a substitution alphabet in upper case as string or list and provides the following functions
	__str__: Prints the alphabet and its substitution
	substitute: takes a char as input and returns the 
	'''

	def __init__(self, substitution_alphabet):
		self.substitution_alphabet = list(substitution_alphabet)

	def __str__(self):
		return str(list(INT_TO_LETTER)) + '\n' + str(self.substitution_alphabet)

	def substitute(self, letter):
		return self.substitution_alphabet[LETTER_TO_INT[letter]]



class EnigmaReflector(MonoalphabetSubstitution):
	'''
	MonoalphabetSubstitution expanded by:
	__init__(list_of_substitutions): additionally performs check substitution
	check_substitution_alphabet(list_of_substitutions): checks if substitution alphabet fullfills 
	that for every letters substitute the letter is the substitute
	'''

	def __init__(self, substitution_alphabet):
		super().__init__(substitution_alphabet)
		if not self.check_substitution_alphabet():
			raise ValueError('Substitutionalphabet doesnt match requirements. For every letter its substitute has to have the letter as its substitute')
		

	def check_substitution_alphabet(self):
		#generator expression does not work because supper() can only fill zero forms in class scope not in generator scope
		for i in INT_TO_LETTER:
			if i != super().substitute(super().substitute(i)):
				return False
		return True
	


class EnigmaPlugboard(EnigmaReflector):
	'''
	Additionally to Enigma_Reflector the initialisation is more convinient for given a code for the plugboard. 

	changed:
	 __init__(list_of_substitutions): Takes tuples of letters in uppercase eg 'AD','BT', ... 
	and transform into substitution alphabet + checks if matches requirements
	
	new:
	replug(list_of_substitutions):  Replaces substitution alphabet with new one
	'''

	def __init__(self, *args):
		if len(args) > 13:
			raise ValueError('Dont give more than 13 tuples, every letter must occure only once')
		self.substitution_alphabet = list(INT_TO_LETTER)
		for x in args:
			self.substitution_alphabet[LETTER_TO_INT[x[0]]] = x[1]
			self.substitution_alphabet[LETTER_TO_INT[x[1]]] = x[0]
		


class EnigmaRotor(MonoalphabetSubstitution):
	'''
	EnigmaRotor inherits from MonoalphabetSubstitution
	__init__(substitution_alphabet, notch, *args): Additionally saves the notches. One notch is required further are optional
	notches: reurns notches as a list
	substitute(letter,pos): add the shift according to the position of the rotor
	substitute_invers(letter,pos): same as substitute but in inverse direction
	'''
	def __init__(self, substitution_alphabet, notch, *args):
		super().__init__(substitution_alphabet)
		self.notches = [notch] + [x for x in args]
		#To allow int as well as letters, transform everything to int from 0-25 mirrowing A-Z
		for i, x in enumerate(self.notches):
			if isinstance(x,str):
				self.notches[i] = LETTER_TO_INT[x]
			else:
				self.notches[i] = x-1

	def __str__(self):
		return super().__str__() + '\nNotches: ' + str([INT_TO_LETTER[x] for x in self.notches])

	
	def notches(self):
		return self.notches

	def substitute(self, letter, pos):
		return self.substitution_alphabet[(LETTER_TO_INT[letter] + pos) % 26]

	def substitute_inverse(self, letter, pos):
		return INT_TO_LETTER[(self.substitution_alphabet.index(letter) - pos) % 26]
	

		
class Enigma:
	'''
	Sets up a enigma machine to encrypt and decrypt texts
	__init__(reflector, plugboard_setting, rotor_1, rotor_2, rotor_3, rotor_4 = list(string.ascii_uppercase), rotor_position = [1,1,1]):
		takes all elements needed to setup an enigma objects of the required classes are needed
		Remark: EnigmaReflector and EnigmaPlugboard can be used vice versa
	reset: resets the enigma to its starting positions
	rotor_action_inway(self, letter): For internal use
	process_letter(letter): Processes a singel letter, resembeling tipping once
	encrypt(text): Encrypts a text and returns encrypted string in blocks of five letters
	decrypt(text): Selfexplaining
	replug(*args): replugs the plugboard
	'''



	def __init__(self, reflector, plugboard_setting, rotor_1, rotor_2, rotor_3, rotor_4 = list(string.ascii_uppercase), rotor_position = [1,1,1]):	

		self.reflector = reflector
		self.plugboard = plugboard
		self.rotors = [rotor_1, rotor_2, rotor_3]

		if rotor_4 != list(string.ascii_uppercase):
			self.rotors.append(rotor_4)
	
		self.rotor_position_start = []
		self.rotor_position = []
		self.set_rotor_position(rotor_position)


	def __str__(self):
		text = 'Enigma:\n\nRefelctor:\n' + self.reflector.__str__() + '\n\nPlugboard:\n' + self.plugboard.__str__()
		for i, rotor in zip(range(len(self.rotors)),self.rotors):
			text += '\n\nRotor_%d:\n'%(i) + rotor.__str__() + \
			'   Position: ' + str(self.rotor_position[i]+1) + ' (' + INT_TO_LETTER[self.rotor_position[i]] + ')'	
		return text


	def reset(self):
		self.rotor_position = list(self.rotor_position_start)

	
	def rotor_action_inway(self, letter):

		self.rotor_position[0] = (self.rotor_position[0] + 1) % 26
		
		for i, rotor, pos in zip(range(len(self.rotors)), self.rotors, self.rotor_position):
			if i != len(self.rotors)-1:
				if pos in rotor.notches:
					self.rotor_position[i+1] = (self.rotor_position[i+1] + 1) % 26
			letter = rotor.substitute(letter,pos)

		return letter


	def process_letter(self, letter):
		letter = self.plugboard.substitute(letter)
		letter = self.rotor_action_inway(letter)
		letter = self.reflector.substitute(letter)

		for rotor, pos in reversed(list(zip(self.rotors, self.rotor_position))):
			letter = rotor.substitute_inverse(letter, pos)

		letter = self.plugboard.substitute(letter)

		return letter


	def encrypt(self,text):

		text = text.replace(' ','').upper()

		result = ''

		for x in text:
			result += self.process_letter(x)

		return ' '.join([result[i:i+5] for i in range(0, len(result), 5)])
			
			
	def decrypt(self,text):
		self.reset()
		return self.encrypt(text).replace(' ','')

	def replug(self, *args):
		self.reset()
		self.plugboard = EnigmaPlugboard(*args)

	def set_rotor_position(self, rotor_position):
		self.rotor_position_start = rotor_position
		
		for i, x in enumerate(rotor_position):
			if isinstance(x,str):
				self.rotor_position_start[i] = LETTER_TO_INT[x]
			else:
				self.rotor_position_start[i] = x-1

		self.rotor_position = list(self.rotor_position_start)


	
	

rotor_I = EnigmaRotor('EKMFLGDQVZNTOWYHXUSPAIBRCJ', 17)
rotor_II = EnigmaRotor('AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E')
rotor_III = EnigmaRotor('BDFHJLCPRTXVZNYEIWGAKMUSQO', 22)
rotor_IV = EnigmaRotor('ESOVPZJAYQUIRHXLNFTGKDCMWB', 'J')
rotor_V = EnigmaRotor('VZBRGITYUPSDNHLXAWMJQOFECK', 'V')
rotor_VI = EnigmaRotor('JPGVOUMFYQBENHZRDKASXLICTW', 'Z', 'M')
rotor_VII = EnigmaRotor('NZJHGRCXMYSWBOUFAIVLPEKQDT', 26, 13)
rotor_VIII = EnigmaRotor('FKQHTLXOCBJSPDZRAMEWNIUYGV', 13, 26)	

ukw_A = EnigmaReflector('EJMZALYXVBWFCRQUONTSPIKHGD')
ukw_B = EnigmaReflector('YRUHQSLDPXNGOKMIEBFZCWVJAT')
ukw_C = EnigmaReflector('FVPJIAOYEDRZXWGCTKUQSBNMHL')

plugboard = EnigmaPlugboard('AG', 'TF', 'HK')

enigma = Enigma(ukw_B, plugboard, rotor_I, rotor_II, rotor_III, rotor_position = ['D','A','Z'])
text = 'This is a string for testing the encryption and decryption capability of the enigma code'
test = enigma.encrypt(text)

print(text)
print(test)
print(enigma.decrypt(test))

enigma.replug('AN', 'HP', 'OL', 'RM')
enigma.set_rotor_position([1,4,22])
test = enigma.encrypt(text)

print('\n' + text)
print(test)
print(enigma.decrypt(test))

enigma.set_rotor_position([1,4,22])
print('\n')
print(enigma)

