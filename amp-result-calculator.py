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

id_to_discipline = {
    0: "Prowadzenie:          ",
    1: "Wspinanie na czas:",
    2: "Bouldering:             ",
}

id_to_discipline_2 = {
    0: "Prowadzenie",
    1: "Wspinanie na czas",
    2: "Bouldering",
}
ix_to_discipline = {
    0: "lead",
    1: "speed",
    2: "boulder"
}

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
            
            label = QLabel(f"{id_to_discipline[i]}")
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
        self.tree.setHeaderLabels(["Zawodnik", "Konkurencja", "Wynik"])
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
            f"Wybierz plik z wynikami konkurencji {id_to_discipline_2[index]}",
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

                self.team_results[team_name]["athletes"][ix_to_discipline[ix]][athlete_name] = {"place": athlete_place, "points": athlete_points}
            
        pprint(self.team_results, indent=2, width=50, sort_dicts=False)

        
    

        
        for i, file_path in enumerate(self.file_paths):
            discipline = f"Konkurencja {i+1}"
            df = pd.read_excel(file_path)
            
            for _, row in df.iterrows():
                athlete_name = str(row.iloc[0])
                score = float(row.iloc[1])
                
                athlete = next((a for a in self.results if a['name'] == athlete_name), None)
                if athlete:
                    athlete['results'].append((discipline, score))
                else:
                    self.results.append({
                        'name': athlete_name,
                        'discipline': discipline,
                        'results': [(discipline, score)]
                    })
        
        # Sortowanie wyników
        for athlete in self.results:
            athlete['results'].sort(key=lambda x: x[1], reverse=True)
        
        self.display_results()
        
        # except Exception as e:
        #     QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas analizy:\n{str(e)}")
    
    def display_results(self):
        self.tree.clear()
        
        for athlete in sorted(self.results, key=lambda x: x['name']):
            athlete_item = QTreeWidgetItem(self.tree)
            athlete_item.setText(0, athlete['name'])
            athlete_item.setExpanded(True)
            
            for discipline, score in athlete['results']:
                result_item = QTreeWidgetItem(athlete_item)
                result_item.setText(1, discipline)
                result_item.setText(2, f"{score:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AthleteAnalyzerApp()
    window.show()
    sys.exit(app.exec())