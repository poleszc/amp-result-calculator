import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QScrollArea, QCheckBox, QComboBox
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
    0: "prowadzenie",
    1: "czas",
    2: "bouldering"
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
        self.number_of_counted_athletes = 3
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
        
        buttons_layout = QHBoxLayout()
        
        classification_layout = QHBoxLayout()
        self.women_checkbox = QCheckBox("Klasyfikacja kobiet (licz 2 najlepszych zawodników)")
        self.women_checkbox.stateChanged.connect(self.toggle_classification)
        classification_layout.addWidget(self.women_checkbox)
        file_layout.addLayout(classification_layout)

        analyze_btn = QPushButton("Analizuj wyniki")
        analyze_btn.clicked.connect(self.analyze_files)
        buttons_layout.addWidget(analyze_btn)
        
        file_layout.addLayout(buttons_layout)
        main_layout.addWidget(file_group)
        
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtruj typ uczelni:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Wszystkie")
        self.filter_combo.currentTextChanged.connect(self.filter_results)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Miejsce", "Uczelnia", "Typ", "Liczba Punktów"])
        self.tree.setColumnWidth(0, 200)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.tree)
        
        main_layout.addWidget(scroll_area, 1)

        bottom_layout = QHBoxLayout()
        
        export_btn = QPushButton("Eksportuj do Excel")
        export_btn.clicked.connect(self.export_to_excel)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(export_btn)
        main_layout.addLayout(bottom_layout)
        
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

    def toggle_classification(self, state):
        self.number_of_counted_athletes = 2 if state == Qt.CheckState.Checked.value else 3
    
    def filter_results(self, selected_type):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if selected_type == "Wszystkie":
                item.setHidden(False)
            else:
                item_type = item.text(2)
                item.setHidden(item_type != selected_type)

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
            print(IX_TO_DISCIPLINE[ix])
            for _, row in disc.iterrows():
                team_name = str(row["Uczelnia"])
                team_type = str(row["Typ"])
                athlete_name = str(row["Imię i Nazwisko"])
    
                # -1 for athletes which didn't compete
                athlete_place = -1
                athlete_points = -1

                if row["Miejsce"] != "DNS":
                    athlete_place = int(row["Miejsce"]) if row["Miejsce"] != "DNF" else len(speed[~speed["Miejsce"].isin(["DNS", "DNF"])])
                    # Athlete points are calculated as follows;
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
                            "prowadzenie": {},     # Athletes to points and places
                            "czas": {},    # Athletes to points and places
                            "bouldering": {}   # Athletes to points and places
                        },
                        "points": 0
                    }

                self.team_results[team_name]["athletes"][IX_TO_DISCIPLINE[ix]][athlete_name] = {"place": athlete_place, "points": athlete_points}
            

        # Calculate team points and check if teams are classified.
        for team_name, team_data in self.team_results.items():
            # Check if a team is classified:
            # At least self.number_of_counted_athletes(3 for men, 2 for women) athletes competed and finished at least 2 disciplines
            athlete_scores = {}
            for disc in ["prowadzenie", "czas", "bouldering"]:
                for ath_name, results in team_data["athletes"][disc].items():
                    if ath_name not in athlete_scores:
                        athlete_scores[ath_name] = []
                    athlete_scores[ath_name].append(results["points"])
            
            classified = False
            ok_athletes_count = 0
            for name, results in athlete_scores.items():
                if len(results) > 2:
                    ok_athletes_count += 1
            if len(athlete_scores) >= self.number_of_counted_athletes and ok_athletes_count >= self.number_of_counted_athletes:
                classified = True

            # Calculate points
            points = []
            for disc in ["prowadzenie", "czas", "bouldering"]:
                athletes = team_data["athletes"][disc]
                valid_athletes = [ath for ath in athletes.values() if ath["points"] != -1]
                top_athletes = sorted(valid_athletes, key=lambda x: x["points"], reverse=True)
                points.extend([ath["points"] for ath in top_athletes[:self.number_of_counted_athletes]])
            team_data["points"] = -1 if not classified else sum(points)

        pprint(self.team_results, indent=2, width=50, sort_dicts=False)

        self.display_results()
        
        # except Exception as e:
        #     QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas analizy:\n{str(e)}")
    
    def export_to_excel(self):
        if len(self.team_results) == 0:
            QMessageBox.warning(self, "Błąd", "Przelicz wyniki przez eksportowaniem!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz wyniki",
            f"wyniki_drużynowe_amp_{"M" if self.number_of_counted_athletes == 3 else "K"}.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # try:
        data = []
        for team_name, team_data in self.team_results.items():
            data.append({
                'Uczelnia': team_name,
                'Typ uczelni': team_data['type'],
                'Punkty': team_data['points']
            })
            
        df = pd.DataFrame(data)
        df = df.sort_values('Punkty', ascending=False)
        df.insert(0, 'Miejsce', range(1, len(df) + 1))
        df.to_excel(file_path, index=False, sheet_name=f"AMP_Klasyfikacja_Drużynowa_{"M" if self.number_of_counted_athletes == 3 else "K"}")
        
        QMessageBox.information(self, "Sukces", f"Wyniki zostały zapisane do pliku:\n{file_path}")
            
        # except Exception as e:
            # QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas eksportu:\n{str(e)}")

    def display_results(self):
        self.tree.clear()
        
        unique_types = set()
        for uni_data in self.team_results.values():
            unique_types.add(uni_data.get('type', 'Unknown'))
        
        current_filter = self.filter_combo.currentText()
        self.filter_combo.clear()
        self.filter_combo.addItem("Wszystkie")
        self.filter_combo.addItems(sorted(unique_types))
        
        index = self.filter_combo.findText(current_filter)
        if index >= 0:
            self.filter_combo.setCurrentIndex(index)

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
            
            if team['points'] == -1:
                team_item.setText(3, "N/A")
                team_item.setForeground(1, Qt.GlobalColor.red)
            else:
                team_item.setText(3, str(team['points']))
                team_item.setForeground(4, Qt.GlobalColor.darkGreen)
                        
            self.add_athlete_details(team_item, team.get('athletes', {}))
            
    def add_athlete_details(self, parent_item, athletes_data):
        details_item = QTreeWidgetItem(parent_item)
        details_item.setText(0, "Szczegóły")
        
        for discipline, athletes in athletes_data.items():
            discipline_item = QTreeWidgetItem(details_item)
            discipline_item.setText(0, f" {discipline.capitalize()}")
            
            for athlete_name, results in athletes.items():
                athlete_item = QTreeWidgetItem(discipline_item)
                athlete_item.setText(0, athlete_name)
                
                if results['points'] == -1:
                    athlete_item.setText(1, "Nie ukończył" if self.number_of_counted_athletes == 3 else "Nie ukończyła")
                    athlete_item.setForeground(1, Qt.GlobalColor.gray)
                else:
                    athlete_item.setText(1, f"Miejsce: {results['place']}")
                    athlete_item.setText(2, f"Punkty: {results['points']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AthleteAnalyzerApp()
    window.show()
    sys.exit(app.exec())