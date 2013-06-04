
class Poll(object):
	def __init__(self, question, options, votes = {}):
		self.question = question
		self.options = options
		self.votes = votes
		if not votes:
			for option in options:
				self.votes[option] = 0

	@staticmethod
	def parse(text):
		arr = []
		dic = {}
		optionnum, nvotes, i = 0, 0, 0
		while i < len(text):
			optionnumtext = ""
			option = ""
			numtext = ""
			if text[i] == '(':
				i += 1

				while text[i:i+3] != '###':
					option += text[i]
					i += 1
				i += 3

				while text[i] != ')':
					numtext += text[i]
					i += 1
				nvotes = int(numtext)

			arr.append(option)
			dic[option] = nvotes
			i += 1
		return Poll(arr, dic)

	def render_code(self):
		code = ""
		for option in self.options:
			code += "(%s###%d)" % (option, self.votes[option])

	def record_vote(self, index):
		if index < len(self.options):
			self.votes[self.options[index]] += 1