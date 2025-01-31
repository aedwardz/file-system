from fs import FS

fs = FS()
with open('sample2.txt', 'r') as file:
    # Iterate over each line in the file
    for line in file:
        # Process the line (e.g., print it)
        # print(line.split())

        line = line.split()
        if not line:
            print()
            continue
        # print(line)

        if line[0] == "in":
            fs.__init__()
            print("System Initialized")
        if line[0] == 'cr':
            name = line[1]
            try:
                print(fs.create(name))
            except Exception as e:
                print(e)
        if line[0] == 'de':
            name = line[1]
            try:
                print(fs.destroy(name))
            except Exception as e:
                print(e)
        if line[0] == 'op':
            name = line[1]
            try:
                fs.open(name)
                print(f"File \"{name}\" opened")
            except Exception as e:
                print(e)
        if line[0] == 'cl':
            num = int(line[1])-1
            try:
                print(fs.close(num))
            except Exception as e:
                print(e)
        if line[0] == 'dr':
            try:
                fs.directory()
            except Exception as e:
                print(e)
        if line[0] == 'rd':
            arg1, arg2, arg3 = int(line[1])-1, int(line[2]), int(line[3])
            try:
                print(fs.read(arg1, arg2, arg3))
            except Exception as e:
                print(e)
        if line[0] == 'wr':
            arg1, arg2, arg3 = int(line[1])-1, int(line[2]), int(line[3])
            try:
                print(fs.write(arg1, arg2, arg3))
            except Exception as e:
                print(e)
        if line[0] == 'sk':
            i, p = int(line[1])-1, int(line[2])
            try:
                print(fs.seek(i, p))
            except Exception as e:
                print(e)
        if line[0] == 'rm':
            m, n = int(line[1]), int(line[2])
            try:
                fs.read_memory(m, n)
            except Exception as e:
                print(e)
        if line[0] == 'wm':
            m, s = int(line[1]), line[2]
            try:
                fs.write_memory(m, s)
            except Exception as e:
                print(e)





