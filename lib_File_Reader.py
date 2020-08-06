import pandas as pd
import os
class File_Reader:
	TAG = 'File_Reader: '
	def __init__(self, d, n, autoDate = False):
		self.directory = d
		self.name = n
		self.fullName = os.path.join(self.directory, self.name)
		self.dfs = {}
		self.properties = {}
		self.isDir = os.path.isdir(self.fullName)
		self.__read__(autoDate = autoDate)
		pass
	def __read__(self, autoDate):
		print(self.TAG, 'reading: ', self.fullName)
		if (self.isDir):
			for filename in os.listdir(self.fullName):
				csvName = os.path.splitext(os.path.basename(filename))[0]
				self.dfs[csvName] = pd.read_csv(os.path.join(self.fullName, filename), parse_dates=True)
				if(autoDate):
					for col in self.dfs[csvName].columns:
						if self.dfs[csvName][col].dtype == 'object':
							try:
								self.dfs[csvName][col] = pd.to_datetime(self.dfs[csvName][col])
							except (ValueError, TypeError):
								pass
				#print(self.TAG, 'loaded: ', csvName)
				#print(self.dfs[csvName])
		elif (self.name.endswith('.xlsx')):
			xl = pd.ExcelFile(self.fullName)
			for sheetName in xl.sheet_names:
				self.dfs[sheetName] = xl.parse(sheetName)
				#print(self.TAG, 'loaded: ', sheetName)
				#print(self.dfs[sheetName])
		elif (self.name.endswith('.csv')):
			self.dfs[self.name] = pd.read_csv(self.fullName, parse_dates=True)
			if(autoDate):
				for col in self.dfs[self.name].columns:
					if self.dfs[self.name][col].dtype == 'object':
						try:
							self.dfs[self.name][col] = pd.to_datetime(self.dfs[self.name][col])
						except (ValueError, TypeError):
							pass
			#print(self.TAG, 'loaded: ', self.name)				
		print(self.TAG, 'loaded')
	def getProperty(self, propertyName):
		return self.properties[propertyName]
	def setProperty(self, propertyName, propertyValue):
		self.properties[propertyName] = propertyValue
		print(self.TAG, 'set: ', ': ', propertyName)
	def getDf(self, dfName):
		return self.dfs[dfName]
	@staticmethod
	def getFileNames(d):
		files = [f for f in os.listdir(d)]
		return files