import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import pandas as pd
from pprint import pprint

ID_TO_DISCIPLINE = {
    0: "Prowadzenie:          ",
    1: "Wspinanie na czas:",
    2: "Bouldering:             ",
}

ID_TO_DISCIPLINE_2 = {
    0: "prowadzenie",
    1: "wspinanie na czas",
    2: "bouldering",
}
IX_TO_DISCIPLINE = {
    0: "lead",
    1: "speed",
    2: "boulder"
}

NUMBER_OF_COUNTED_ATHLETES = 3

class AthleteAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMP kalkulator wyników grupowych")
        self.setGeometry(100, 100, 800, 600)
        
        self.file_paths = [None, None, None]
        self.results = []
        self.max_participants = 0
        self.team_results = {}

        
        self.init_ui()
    
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png")
        logo_pixmap = logo_pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation) 
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(logo_label)
        main_layout.addSpacing(10) 

        # File picking
        file_layout = QVBoxLayout()
        file_group = QWidget()
        file_group.setLayout(file_layout)
        
        for i in range(3):
            row_layout = QHBoxLayout()
            
            label = QLabel(f"{ID_TO_DISCIPLINE[i]}")
            row_layout.addWidget(label)
            
            path_label = QLabel("Nie wybrano pliku")
            path_label.setWordWrap(True)
            row_layout.addWidget(path_label, 1)
            
            browse_btn = QPushButton("Wybierz plik")
            browse_btn.clicked.connect(lambda _, idx=i: self.select_file(idx))
            row_layout.addWidget(browse_btn)
            
            file_layout.addLayout(row_layout)
            setattr(self, f"path_label_{i}", path_label)
        
        analyze_btn = QPushButton("Analizuj wyniki")
        analyze_btn.clicked.connect(self.analyze_files)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Miejsce", "Uczelnia", "Typ", "Liczba Punktów"])
        self.tree.setColumnWidth(0, 200)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.tree)
        
        main_layout.addWidget(file_group)
        main_layout.addWidget(analyze_btn)
        main_layout.addWidget(scroll_area, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def select_file(self, index):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Wybierz plik z wynikami konkurencji {ID_TO_DISCIPLINE_2[index]}",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.file_paths[index] = file_path
            getattr(self, f"path_label_{index}").setText(file_path)
    
    def analyze_files(self):
        if None in self.file_paths:
            QMessageBox.warning(self, "Błąd", "Proszę wybrać wszystkie 3 pliki!")
            return
        
        # try:
        self.results = []
        print(self.file_paths)
        lead = pd.read_excel(self.file_paths[0])
        speed = pd.read_excel(self.file_paths[1])
        boulder = pd.read_excel(self.file_paths[2])

        print(lead.columns)
        print(len(lead))

        # Calculate the max number of participants accross all disciplines
        for disc in [lead, speed, boulder]:
            participant_count = len(disc[disc["Miejsce"] != "DNS"])
            self.max_participants = participant_count if participant_count > self.max_participants else self.max_participants
            print(participant_count)

        # Populate the team results
        for ix, disc in enumerate([lead, speed, boulder]):
            for _, row in disc.iterrows():
                team_name = str(row["Uczelnia"])
                team_type = str(row["Typ"])
                athlete_name = str(row["Imię i Nazwisko"])
    
                # -1 for athletes which didn't compete
                athlete_place = -1
                athlete_points = -1

                if row["Miejsce"] != "DNS":
                    athlete_place = int(row["Miejsce"]) if row["Miejsce"] != "DNF" else len(speed[~speed["Miejsce"].isin(["DNS", "DNF"])])
                    # Athlete points are calculated by this formula;
                    # 1 place -> n + 1 points(this is not a mistype, we add a point for winners)
                    # 2 place -> n - 1 points
                    # 3 place -> n - 2 points
                    # m place -> n - m + 1
                    athlete_points = self.max_participants - athlete_place + 1 
                    if athlete_place == 1:
                        athlete_points += 1

                if team_name not in self.team_results:
                    self.team_results[team_name] = {
                        "type": team_type,
                        "athletes": {       # Discipline to athletes
                            "lead": {},     # Athletes to points and places
                            "speed": {},    # Athletes to points and places
                            "boulder": {}   # Athletes to points and places
                        },
                        "points": 0
                    }

                self.team_results[team_name]["athletes"][IX_TO_DISCIPLINE[ix]][athlete_name] = {"place": athlete_place, "points": athlete_points}
            

        # Calculate team points and check if teams are classified.
        for team_name, team_data in self.team_results.items():
            # Check if a team is classified:
            # At least NUMBER_OF_COUNTED_ATHLETES(3 for men, 2 for women) athletes competed and finish at least 2 disciplines
            athlete_scores = {}
            for disc in ["lead", "speed", "boulder"]:
                for ath_name, results in team_data["athletes"][disc].items():
                    if ath_name not in athlete_scores:
                        athlete_scores[ath_name] = []
                    athlete_scores[ath_name].append(results["points"])
            
            classified = False
            ok_athletes_count = 0
            for name, results in athlete_scores.items():
                if len(results) > 2:
                    ok_athletes_count += 1
            if len(athlete_scores) >= NUMBER_OF_COUNTED_ATHLETES and ok_athletes_count >= NUMBER_OF_COUNTED_ATHLETES:
                classified = True

            # Calculate points
            points = []
            for disc in ["lead", "speed", "boulder"]:
                athletes = team_data["athletes"][disc]
                valid_athletes = [ath for ath in athletes.values() if ath["points"] != -1]
                top_athletes = sorted(valid_athletes, key=lambda x: x["points"], reverse=True)
                points.extend([ath["points"] for ath in top_athletes[:NUMBER_OF_COUNTED_ATHLETES]])
            team_data["points"] = -1 if not classified else sum(points)

        pprint(self.team_results, indent=2, width=50, sort_dicts=False)

        self.display_results()
        
        # except Exception as e:
        #     QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas analizy:\n{str(e)}")
    
    def display_results(self):
        self.tree.clear()
        
        # teams_data = []
        # for team_name, team_data in self.team_results.items():
        #     team_data["name"] = team_name
        #     teams_data.append(teams_data)

        teams_data = []
        for uni_name, uni_data in self.team_results.items():
            team_info = {
                'name': uni_name,
                'type': uni_data.get('type', 'Unknown'),
                'points': uni_data.get('points', -1),
                'athletes': uni_data.get('athletes', {})
            }
            teams_data.append(team_info)

        teams_data.sort(key=lambda x: x["points"], reverse=True)
        


        for position, team in enumerate(teams_data, 1):
            team_item = QTreeWidgetItem(self.tree)
            
            team_item.setText(0, str(position) if team['points'] != -1 else "-")
            team_item.setText(1, team['name'])
            team_item.setText(2, team.get('type', 'Nieznany typ uczelni'))
            
            # Punkty i status
            if team['points'] == -1:
                team_item.setText(3, "N/A")
                team_item.setForeground(1, Qt.GlobalColor.red)
            else:
                team_item.setText(3, str(team['points']))
                team_item.setForeground(4, Qt.GlobalColor.darkGreen)
            
            # Kolorowanie podium
            # if position <= 3 and team['points'] != -1:
            #     colors = [QColor(255, 215, 0), QColor(192, 192, 192), QColor(205, 127, 50)]
            #     for col in range(5):
            #         team_item.setBackground(col, colors[position-1])
            
            # Szczegóły wyników
            self.add_athlete_details(team_item, team.get('athletes', {}))
            
            # Rozwijanie tylko dla klasyfikowanych
            team_item.setExpanded(True)

    def add_athlete_details(self, parent_item, athletes_data):
        details_item = QTreeWidgetItem(parent_item)
        details_item.setText(0, "Szczegóły wyników")
        
        for discipline, athletes in athletes_data.items():
            discipline_item = QTreeWidgetItem(details_item)
            discipline_item.setText(0, f"Konkurencja: {discipline.capitalize()}")
            
            for athlete_name, results in athletes.items():
                athlete_item = QTreeWidgetItem(discipline_item)
                athlete_item.setText(0, athlete_name)
                
                if results['points'] == -1:
                    athlete_item.setText(1, "Nie ukończył")
                    athlete_item.setForeground(1, Qt.GlobalColor.gray)
                else:
                    athlete_item.setText(1, f"Miejsce: {results['place']}")
                    athlete_item.setText(2, f"Punkty: {results['points']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AthleteAnalyzerApp()
    window.show()
    sys.exit(app.exec())