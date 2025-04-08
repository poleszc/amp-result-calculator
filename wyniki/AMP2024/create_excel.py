# Parses the file created by copying from results pdf to actual excel file.
import pandas as pd
import sys

def speed(file_path: str, out_file_path: str):
    lines = []
    with open(file_path, mode="r+") as file:
        for line in file:
            lines.append(line.split())
    
    results = []
    for ix, line in enumerate(lines):
        if ix % 2 == 1:
            print(line)
            place = int(line[0])
            name = line[1]
            surname = line[2]
            team_name = ""
            type = ""
            for part in [line[3], lines[ix+1][0], lines[ix+1][1], lines[ix+1][2]]:
                if len(part) == 3 and part in ["UWF", "UNI", "UTE", "USP", "UME", "WSN"]:
                    type = part
                    team_name = team_name.rstrip()
                    break
                else:
                    team_name += f"{part} "

            results.append([place, name, surname, team_name, type])

    for res in results:
        print(res)

    for ix, res in enumerate(results):
        # if res[0] != ix + 1:
            # print(f"Failed: {res}, expected {ix + 1}")
        assert len(res) == 5

    data = []
    for res in results:
        data.append({
            "Imię i Nazwisko": f"{res[1]} {res[2]}",
            "Uczelnia": res[3],
            "Typ": res[4],
            "Miejsce": res[0]
        })
        
    df = pd.DataFrame(data)
    df = df.sort_values('Miejsce', ascending=True)
    df.to_excel(out_file_path, index=False, sheet_name=out_file_path.split('.')[0])


def lead_boulder(file_path: str, out_file_path: str):
    lines = []
    with open(file_path, mode="r+") as file:
         for line in file:
             lines.append(line.split())

    results = []
    for line in lines:
        if len(line) >= 6: # Valid line
            place =  int(line[0])
            name = line[1]
            surname = line[2]
        
            team_name = ""
            type = ""
            for part in line[3:]:
                if len(part) == 3 and part in ["UWF", "UNI", "UTE", "USP", "UME", "WSN"]:
                    type = part
                    team_name = team_name.rstrip()
                    break
                else:
                    team_name += f"{part} "           

            results.append([place, name, surname, team_name, type])

    
    for res in results:
        print(res)

    for ix, res in enumerate(results):
        # if res[0] != ix + 1:
            # print(f"Failed: {res}, expected {ix + 1}")
        assert len(res) == 5

    data = []
    for res in results:
        data.append({
            "Imię i nazwisko": f"{res[1]} {res[2]}",
            "Uczelnia": res[3],
            "Typ": res[4],
            "Miejsce": res[0]
        })
        
    df = pd.DataFrame(data)
    df = df.sort_values('Miejsce', ascending=True)
    df.to_excel(out_file_path, index=False, sheet_name=out_file_path.split('.')[0])
        

if __name__ == "__main__":
    if len(sys.argv) == 3:
        lead_boulder(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        speed(sys.argv[2], sys.argv[3])
    else:
        print("Usage: python create_excel [optional: speed] <file_path> <out_file_path>")
        exit()

    