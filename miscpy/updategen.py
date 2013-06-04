import random

f = open("userupdate.sql", "w")

updatetext = "UPDATE User SET age=%d, sex='%s' where userID=%d;\n"

for i in range(2000):
	userID = i+1
	age = random.randrange(1, 65)
	sex = random.choice(["Male", "Female"])
	f.write(updatetext % (age, sex, userID))
