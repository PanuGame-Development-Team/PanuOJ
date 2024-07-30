import os
dirfs = os.listdir(".")
fname = dirfs[0].split(".")[0].strip("1234567890")
i = 0
while os.path.isfile(f"{fname}{i}.in"):
    os.system(f"mv {fname}{i}.in {i+1}.in")
    os.system(f"mv {fname}{i}.out {i+1}.ans")
    i += 1