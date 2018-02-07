import os


root = "C:/PathRemapTool/Props"
file_with_issues_path = "{0}/file_with_issues_props.txt".format(root)

b_type_map = {
    'P': 'Props',
    'C': 'Chars',
    'S': 'Sets',
}
a_type_map = {
    'RG': 'Rig',
    'MDL': 'Model',
    'PVZ': 'Model',
    'PZV': 'Model',
    'HiccupirePZV': 'Model',
    'PXY': 'Model',
    'CMR': 'Model',
    'PRX': 'Model',
    'PYV': 'Model',
    'BLKLGT': 'Model',
    'LGT': 'Lgt',
    'PRD': 'Published',
    'PRDe': 'Published',
    'SHD': 'Published',
    'CMR': 'Published',
    'GEO': 'Published',
    'LKD': 'Lookdev',
    'GEOalley': 'Published'
}

def run():
    count = 0
    for each_file in os.listdir(root):
        if not os.path.isfile(root + "/" + each_file):
            continue
        if not each_file.startswith("PathRemap."):
            continue
        cur_file = os.path.join(root, each_file)
        file_str = ""
        check = False
        summary = False
        collected_lines = []
        
        with open(cur_file, 'r') as fh:
            data = fh.readlines()
        print 'processing ', cur_file
        for each in data:
            line = each.strip()
            '''This used to find all unfound paths'''
            if 'Summary:' in line:
                file_str += "="*56 + "\n"
                summary = True
                continue
            if summary:
                if 'Everything exists in the correct location' in line:
                    summary = False
                    file_str = file_str[:file_str.rfind("="*56 + "\n")]
                    collected_lines = []
                    continue
                if 'Saved' in line:
                    file_str += '\n'.join(reversed(collected_lines))
                    collected_lines = []
                    summary = False
                    file_str += "\n" + "="*56 + "\n"
                    continue
                if "Unfound path" in line:
                    path = " ".join(line.split()[3:])
                    collected_lines.append(path)
                
                if "Issues found" in line:
                    count += 1
                    path = line.split()[-1]
                    collected_lines.append('Processed File : ' + path + "\n")
                    # abspath = path_construct(os.path.basename(path))
                    # # print path
                    # if abspath:
                    #     # print abspath, ' - ', os.path.exists(abspath)
                    #     collected_lines.append(abspath  + "\n")
                    # else:
                    #     collected_lines.append('Processed : ' + path + "\n")
                
                

        with open(file_with_issues_path, 'a') as fh:
            fh.write(file_str)
        print "Write finished successfully!"
    summary = "{0}\n: Summary : \nNumber of files with issues: {1}\nFiles that crashed".format("="*50, count)
    with open(file_with_issues_path, 'a') as fh:
        fh.write(summary)



def path_construct(basename):
    base_split = basename.split("_")
    # print basename
    if len(base_split) > 4 :
        # print 'invalid path : ', basename
        return 
    try:
        pcode, b_type, a_name, a_type = base_split
    except ValueError:
        # print 'invalid path : ', basename
        return
    a_type = a_type.split(".")[0]
    if b_type in ['EP102B'] or  a_type in ['VDB', 'OverallRef']:
        return
    

    src_folder='J:/Productions/Vampirina2/AssetsRepo'
    btype_folder = b_type_map[b_type]
    atype_folder = a_type_map[a_type]
    filepath = "{root}/{btype}/{aname}/{atype}/{filename}".format(root=src_folder, 
                                                       btype=btype_folder,
                                                       aname=a_name,
                                                       atype=atype_folder,
                                                       filename=basename)
    return filepath                                                       


if __name__ == '__main__':
    run()