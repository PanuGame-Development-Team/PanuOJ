import docker,os
con = docker.from_env()
# def sandbox(code,runid,name,options,time=1000,mem=64*1024*1024):
#     os.popen(f"mkdir '{runid}'").read()
#     os.popen(f"mount -t tmpfs '{runid}' ./'{runid}' -o size=64M").read()
#     os.popen(f"cp {name}/* '{runid}'").read()
#     with open(f"{runid}/{name}.cpp","w") as file:
#         file.write(code)
#     os.chdir(f"{runid}")
#     ans = do_c(options.format(name=name),name,[],time,mem)
#     os.chdir("..")
#     with open(f"{runid}.ans","a") as file:
#         file.write(f"{ans[0]}\n")
#         for i in ans[1]:
#             file.write(f"{ans[1][i][0]} {ans[1][i][1]} {ans[1][i][2]}\n")
#     os.popen(f"umount {runid}").read()
#     os.popen(f"rm -r {runid}").read()
def sandbox(code,runid,name,options,time=1000,mem=64*1024*1024):
    os.popen(f"mkdir '{runid}'").read()
    os.popen(f"cp {name}/* '{runid}'").read()
    with open(f"{runid}/{name}.cpp","w") as file:
        file.write(code)
    os.popen(f"cp judger.py {runid}").read()
    os.popen(f"cp log.py {runid}").read()
    ct = con.containers.run("psutil_gpp",f"""python3 judger.py "{options.format(name=name)}" {name}""",remove=True,volumes=[f"""{os.path.abspath(".")}/{runid}:/{runid}"""],working_dir = f"/{runid}")
    ans = ct.decode()
    with open(f"{runid}.ans","a") as file:
        file.write(ans)
    os.popen(f"rm -r {runid}").read()
