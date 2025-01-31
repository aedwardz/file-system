from fs import FS
import sys

fs = FS()
with open('FS-input-1.txt', 'r') as file, open('output.txt', 'w') as outfile:
    sys.stdout = outfile
    # Iterate over each line in the file
    for line in file:
        # Process the line (e.g., print it)
        # print(line.split())

        line = line.split()
        if not line:
            outfile.write('\n')
            continue
        # print(line)

        if line[0] == "in":
            fs.__init__()
            outfile.write("System Initialized" + '\n')
        if line[0] == 'cr':
            name = line[1]
            try:
                outfile.write(fs.create(name)+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'de':
            name = line[1]
            try:
                outfile.write(fs.destroy(name)+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'op':
            name = line[1]
            try:
                ind = fs.open(name)
                outfile.write(f"File \"{name}\" opened {ind+1}"+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'cl':
            num = int(line[1])-1
            try:
                outfile.write(fs.close(num)+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'dr':
            try:
                fs.directory()
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'rd':
            arg1, arg2, arg3 = int(line[1])-1, int(line[2]), int(line[3])
            try:
                outfile.write(fs.read(arg1, arg2, arg3)+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'wr':
            arg1, arg2, arg3 = int(line[1])-1, int(line[2]), int(line[3])
            try:
                outfile.write(fs.write(arg1, arg2, arg3)+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'sk':
            i, p = int(line[1])-1, int(line[2])
            try:
                outfile.write(fs.seek(i, p)+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'rm':
            m, n = int(line[1]), int(line[2])
            try:
                fs.read_memory(m, n)
            except Exception as e:
                outfile.write(str(e)+ '\n')
        if line[0] == 'wm':
            m, s = int(line[1]), line[2]
            try:
                outfile.write(fs.write_memory(m, s)+ '\n')
            except Exception as e:
                outfile.write(str(e)+ '\n')





