from random import randint

class MK2(object):

	def __init__(self, port=None):
		pass

	def start(self):
		return self

	def ac_info(self):
		return dict(
			umains = 230 + float(randint(-5,5))/10,
			uinv   = 230 + float(randint(-5,5))/10,
			imains =       float(randint(0,100))/10,
			iinv   =       float(randint(0,100))/10,
		)

	def dc_info(self):
		return dict(
			ubat    = 48 + float(randint(-5,5))/10,
			ibat    =      float(randint(0,200))/10,
			icharge =      float(randint(0,200))/10,
		)

	def get_state_raw(self):
		state1 = randint(0, 16)
		if state1 >= 9:
			state1 = 9
			state2 = randint(0, 8)
		else:
			state2 = 0
		return (state1, state2)
		# return (9, randint(1, 3)) # charge bulk/absorption/float

	def led_info(self):
		return {
		  'mains'     : False,
      'absorption': False,
      'bulk'      : False,
      'float'     : True,
      'inverter'  : False,
      'overload'  : False,
      'low bat'   : False,
      'temp'      : False,
    }
