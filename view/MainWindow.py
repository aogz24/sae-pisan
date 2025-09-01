from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QMenu, QFrame, QSpacerItem,
    QAbstractItemView, QApplication, QSplitter, QScrollArea, QSizePolicy, QToolBar, QInputDialog, 
    QTextEdit, QDialog, QComboBox, QPushButton, QHBoxLayout, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QSize, QTimer 
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QPixmap, QFont
import polars as pl
from model.TableModel import TableModel
import os
from service.table.GoToRow import go_to_start_row, go_to_end_row
from service.table.GoToColumn import go_to_start_column, go_to_end_column
from view.components.MenuContext import show_context_menu
from view.components.ModelingSaeEblupAreaDialog import ModelingSaeDialog
from view.components.ModellingSaeHBDialog import ModelingSaeHBDialog
from view.components.ModelingSaeEblupUnitDialog import ModelingSaeUnitDialog
from view.components.ModellingSaeHbNormal import ModelingSaeHBNormalDialog
from view.components.ModelingSaeEblupPseudoDialog import ModelingSaePseudoDialog
from view.components.exploration.SummaryDataDialog import SummaryDataDialog
from view.components.exploration.NormalityTestDialog import NormalityTestDialog
from view.components.exploration.CorrelationMatrikDialog import CorrelationMatrixDialog
from view.components.exploration.MulticollinearityDialog import MulticollinearityDialog
from view.components.exploration.VariableSelectionDialog import VariableSelectionDialog
from view.components.graph.ScatterPlotDialog import ScatterPlotDialog
from view.components.graph.BoxPlotDialog import BoxPlotDialog
from view.components.graph.LinePlotDialog import LinePlotDialog
from view.components.graph.HistogramDialog import HistogramDialog
from view.components.AboutDialog import AboutDialog
from view.components.ComputeVariableDialog import ComputeVariableDialog
from view.components.ProjectionDialog import ProjectionDialog
from service.table.DeleteColumn import confirm_delete_selected_columns
from service.table.AddColumn import show_add_column_before_dialog, show_add_column_after_dialog
from view.components.ProjectionDialog import ProjectionDialog
from PyQt6.QtWidgets import QLabel
import json
import datetime
from service.utils.utils import display_script_and_output
from view.components.CustomToast import CustomToast
import logging
import traceback

class MainWindow(QMainWindow):
    """Main application window for SAE Pisan: Small Area Estimation Programming for Statistical Analysis.
    Attributes:
        data1 (pl.DataFrame): DataFrame for the first sheet (Data Editor).
        data2 (pl.DataFrame): DataFrame for the second sheet (Data Output).
        model1 (TableModel): Table model for the first sheet.
        model2 (TableModel): Table model for the second sheet.
        path (str): Path to the application directory.
        font_size (int): Default font size for the application.
        show_modeling_sae_dialog (ModelingSaeDialog): Dialog for SAE modeling.
        show_modeling_saeHB_dialog (ModelingSaeHBDialog): Dialog for SAE HB modeling.
        show_modeling_sae_unit_dialog (ModelingSaeUnitDialog): Dialog for SAE unit modeling.
        show_modeling_saeHB_normal_dialog (ModelingSaeHBNormalDialog): Dialog for SAE HB normal modeling.
        show_modellig_sae_pseudo_dialog (ModelingSaePseudoDialog): Dialog for SAE pseudo modeling.
        show_compute_variable_dialog (ComputeVariableDialog): Dialog for computing new variables.
        show_projection_variabel_dialog (ProjectionDialog): Dialog for variable projection.
        menu_bar (QMenuBar): Menu bar for the application.
        toolBar (QToolBar): Tool bar for the application.
        tab_widget (QTabWidget): Tab widget containing the different sheets.
        spreadsheet (QTableView): Table view for the first sheet.
        table_view2 (QTableView): Table view for the second sheet.
        scroll_area (QScrollArea): Scroll area for the output tab.
        output_layout (QVBoxLayout): Layout for displaying output in the output tab.
    Methods:
        init_ui(): Initializes the user interface.
        change_font_size(): Opens a dialog to change the font size.
        set_font_size(size): Sets the font size for the application.
        load_stylesheet_with_font_size(size): Loads the stylesheet with the specified font size.
        open_summary_data_dialog_lazy(): Lazily opens the summary data dialog.
        open_normality_test_dialog_lazy(): Lazily opens the normality test dialog.
        open_multicollinearity_dialog_lazy(): Lazily opens the multicollinearity dialog.
        open_variable_selection_dialog_lazy(): Lazily opens the variable selection dialog.
        open_scatter_plot_dialog_lazy(): Lazily opens the scatter plot dialog.
        open_correlation_matrix_dialog_lazy(): Lazily opens the correlation matrix dialog.
        open_box_plot_dialog_lazy(): Lazily opens the box plot dialog.
        open_line_plot_dialog_lazy(): Lazily opens the line plot dialog.
        open_histogram_dialog_lazy(): Lazily opens the histogram dialog.
        open_summary_data_dialog(): Opens the summary data dialog.
        open_normality_test_dialog(): Opens the normality test dialog.
        open_scatter_plot_dialog(): Opens the scatter plot dialog.
        open_line_plot_dialog(): Opens the line plot dialog.
        open_box_plot_dialog(): Opens the box plot dialog.
        open_correlation_matrix_dialog(): Opens the correlation matrix dialog.
        open_multicollinearity_dialog(): Opens the multicollinearity dialog.
        open_histogram_dialog(): Opens the histogram dialog.
        open_variable_selection_dialog(): Opens the variable selection dialog.
        show_modeling_sae_dialog_lazy(): Lazily shows the SAE modeling dialog.
        show_modeling_saeHB_dialog_lazy(): Lazily shows the SAE HB modeling dialog.
        show_modeling_sae_unit_dialog_lazy(): Lazily shows the SAE unit modeling dialog.
        show_modeling_saeHB_normal_dialog_lazy(): Lazily shows the SAE HB normal modeling dialog.
        show_modellig_sae_pseudo_dialog_lazy(): Lazily shows the SAE pseudo modeling dialog.
        show_compute_variable_dialog_lazy(): Lazily shows the compute variable dialog.
        show_projection_variabel_dialog_lazy(): Lazily shows the projection variable dialog.
        open_about_dialog(): Opens the about dialog.
        add_row(sheet_number): Adds a new row to the specified sheet.
        add_column(sheet_number): Adds a new column to the specified sheet.
        update_table(sheet_number, model): Updates the table for the specified sheet with a new model.
        keyPressEvent(event): Handles keyboard shortcuts for copy, paste, undo, and redo.
        copy_selection(): Copies the selected cells to the clipboard.
        paste_selection(): Pastes the clipboard content to the selected cells.
        undo_action(): Undoes the last action.
        redo_action(): Redoes the last undone action.
        group_by_row(selection): Groups selected indexes by row.
        show_output(title, content): Displays output in the Output tab.
        show_header_context_menu(pos): Shows the context menu for the header.
        rename_column(column_index): Renames the column at the given index.
        edit_data_type(column_index): Edits the data type of the column at the given index.
        set_path(path): Sets the path for the application.
        add_output(script_text, result_text=None, plot_paths=None, error_text=None): Adds output to the layout in the form of a card.
        remove_output(card_frame): Removes output from the layout.
        copy_output_image(card_frame): Copies the output image to the clipboard.
        show_context_menu(pos, card_frame): Shows the context menu for each output."""
    
    def __init__(self):
        """
        Initializes the MainWindow class.
        This constructor sets up the main window for the SAE Pisan application, 
        including setting the window title, initializing data frames, models, 
        and UI components.
        Attributes:
            data1 (pl.DataFrame): A DataFrame with 100 columns and 100 empty rows.
            data2 (pl.DataFrame): A DataFrame with columns "Estimated Value", 
                                  "Standar Error", and "CV", each with 100 empty rows.
            model1 (TableModel): The table model for the first data frame.
            model2 (TableModel): The table model for the second data frame.
            path (str): The path to the parent directory of the current file.
            font_size (int): The font size used in the UI.
        """
        
        super().__init__()

        self.setWindowTitle("saePisan: Small Area Estimation Programming for Statistical Analysis v1.5.4")
        columns = [f"Column {i+1}" for i in range(100)]
        self.data1 = pl.DataFrame({col: [None] * 100 for col in columns})
        self.data2 = pl.DataFrame({
            "Estimated Value": [None] * 100,
            "Standar Error": [None] * 100,
            "RSE (%)": [None] * 100
        })

        # Model untuk Sheet 2
        self.model1 = TableModel(self.data1)
        self.model2 = TableModel(self.data2)
        self.path = os.path.join(os.path.dirname(__file__), '..')
        self.font_size = 12
        self.set_font_size(self.font_size)
        self.data = []

        # Inisialisasi UI
        self.init_ui()

        # Set up autosave timer
        self.autosave_interval = 60000  # 60 seconds
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave_data)
        self.autosave_timer.start(self.autosave_interval)
        self.setup_logging()
        self.showMaximized()

    def setup_logging(self):
        """Setup logging to AppData folder"""
        try:
            # Create AppData directory for saePisan
            app_data_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
            os.makedirs(app_data_dir, exist_ok=True)
            
            # Create logs directory
            logs_dir = os.path.join(app_data_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # Setup log file with timestamp
            log_filename = f"saepisan_error_{datetime.datetime.now().strftime('%Y%m%d')}.log"
            log_path = os.path.join(logs_dir, log_filename)
            
            # Configure logging
            logging.basicConfig(
                level=logging.ERROR,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_path, encoding='utf-8'),
                    logging.StreamHandler()  # Also log to console
                ]
            )
            
            self.logger = logging.getLogger(__name__)
            self.logger.info("Logging system initialized")
            
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            # Fallback to basic logging
            logging.basicConfig(level=logging.ERROR)
            self.logger = logging.getLogger(__name__)

    def log_exception(self, exception, context="Unknown"):
        """Log exception with context information"""
        try:
            error_msg = f"""
                        Context: {context}
                        Exception Type: {type(exception).__name__}
                        Exception Message: {str(exception)}
                        Traceback:
                        {traceback.format_exc()}
                        System Info:
                        - App Version: 1.4.0
                        - Current Tab: {self.tab_widget.currentIndex() if hasattr(self, 'tab_widget') else 'Unknown'}
                        - Data1 Shape: {self.model1.get_data().shape if hasattr(self, 'model1') else 'Unknown'}
                        - Data2 Shape: {self.model2.get_data().shape if hasattr(self, 'model2') else 'Unknown'}
                        {'='*50}
                        """
            self.logger.error(error_msg)
        except Exception as log_error:
            print(f"Failed to log exception: {log_error}")

    
    def init_ui(self):
        """
        Initialize the user interface of the main window.
        This method sets up the main layout, including a splitter, tab widgets, 
        and various tabs for data editing, data output, and other functionalities. 
        It also configures the menu bar with different menus and actions, 
        and sets up the toolbar with various actions and icons.
        Tabs:
            - Data Editor: Allows editing of data in a spreadsheet format.
            - Data Output: Displays output data in a table view.
            - Output: Displays output in a scrollable area.
        Menus:
            - File: Contains actions to load and save files.
            - Exploration: Contains actions for data exploration such as summary data, normality test, correlation, etc.
            - Graph: Contains actions to generate different types of plots.
            - Model: Contains actions related to different modeling techniques.
            - Compute: Contains actions to compute new variables.
            - About: Contains information about the application.
            - Settings: Contains actions to change application settings.
        Toolbar:
            - Load File: Action to load a file.
            - Save Data: Action to save data.
            - Undo: Action to undo the last operation.
            - Redo: Action to redo the last undone operation.
            - Compute New Variable: Action to compute a new variable.
            - Setting: Action to open settings.
        Shortcuts:
            - Go to Start Row: Ctrl + Up
            - Go to End Row: Ctrl + Down
            - Go to Start Column: Ctrl + Left
            - Go to End Column: Ctrl + Right
        Layout:
            - The main layout is a vertical box layout containing the tab widget.
            - The central widget is set with this layout.
            - The main window is resized to a default size of 800x600.
        """
        
        # Membuat splitter utama untuk membagi halaman menjadi dua bagian (kiri dan kanan)
        self.splitter_main = QSplitter(Qt.Orientation.Horizontal, self)

        # Bagian kiri: QTabWidget untuk dua sheet
        self.tab_widget = QTabWidget(self.splitter_main)  # Ditambahkan ke splitter utama
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South)
        
        self.show_modeling_sae_dialog = None
        self.show_modeling_saeHB_dialog = None
        self.show_modeling_sae_unit_dialog = None
        self.show_modeling_saeHB_normal_dialog = None
        self.show_modellig_sae_pseudo_dialog = None
        self.show_compute_variable_dialog = None
        self.show_projection_variabel_dialog = None
        

        # Tab pertama (Data Editor)
        self.tab1 = QWidget()
        self.spreadsheet = QTableView(self.tab1)
        self.spreadsheet.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.spreadsheet.customContextMenuRequested.connect(lambda pos: show_context_menu(self, pos))
        self.spreadsheet.setModel(self.model1)
        self.spreadsheet.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.spreadsheet.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)
        self.spreadsheet.horizontalHeader().sectionDoubleClicked.connect(self.rename_column)
        self.spreadsheet.verticalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.spreadsheet.verticalHeader().customContextMenuRequested.connect(lambda pos: show_context_menu(self, pos))

        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(self.spreadsheet)
        self.spreadsheet.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Tab kedua (Data Output)
        self.tab2 = QWidget()
        self.table_view2 = QTableView(self.tab2)
        self.table_view2.setModel(self.model2)
        self.table_view2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        tab2_layout = QVBoxLayout(self.tab2)
        tab2_layout.addWidget(self.table_view2)

        # Tab ketiga (Output)
        self.tab3 = QWidget()
        self.scroll_area = QScrollArea(self.tab3)
        
        # Tab output
        self.output_tab = QWidget()
        self.scroll_area = QScrollArea(self.output_tab)
        self.scroll_area.setWidgetResizable(True)
        self.output_container = QWidget()
        self.output_layout = QVBoxLayout(self.output_container)
        self.output_container.setLayout(self.output_layout)
        self.scroll_area.setWidget(self.output_container)
        
        # Atur layout output
        self.output_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.output_layout.setSpacing(0)

        tab3_layout = QVBoxLayout(self.tab3)
        tab3_layout.addWidget(self.scroll_area)

        # Menambahkan tab ke QTabWidget
        self.tab_widget.addTab(self.tab1, "Data Editor")
        self.tab_widget.addTab(self.tab2, "Data Output")
        self.tab_widget.addTab(self.tab3, "Output")  # Tab baru untuk output

        # Membuat layout utama
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        

        # Widget utama dan layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Membuat menu bar
        self.menu_bar = self.menuBar()

        # Membuat menu File -> Load dan Save
        self.file_menu = self.menu_bar.addMenu("File")
        
        self.recent_data = QAction("Open Recent data", self)
        self.recent_data.setShortcut(QKeySequence("Ctrl+D"))
        self.recent_data.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'recentdata.svg')))
        self.recent_data.setStatusTip("Ctrl+D")
        
        self.load_action = QAction("Open File", self)
        self.load_action.setShortcut(QKeySequence.StandardKey.Open)
        self.load_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'open.svg')))
        self.load_action.setStatusTip("Ctrl+O")
        
        self.load_secondary_data = QAction("Open File for Secondary Data", self)
        self.load_secondary_data.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_2))
        self.load_secondary_data.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'secondary.svg')))
        self.load_secondary_data.setStatusTip("Ctrl+2")
        
        self.save_action = QAction("Save Data", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'savedata.svg')))
        self.save_action.setStatusTip("Ctrl+S")
        
        self.save_data_output_action = QAction("Save Data Output", self)
        self.save_data_output_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_data_output_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'savedataoutput.svg')))
        self.save_action.setStatusTip("Ctrl+Shift+S")
        
        self.save_output_pdf = QAction("Save Output to PDF", self)
        self.save_output_pdf.setShortcut(QKeySequence.StandardKey.Print)
        self.save_output_pdf.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'savepdf.svg')))
        self.save_output_pdf.setStatusTip("Ctrl+P")

        self.file_menu.addAction(self.recent_data)
        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.load_secondary_data)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_data_output_action)
        self.file_menu.addAction(self.save_output_pdf)

        # Menu "Exploration"
        self.menu_exploration = self.menu_bar.addMenu("Exploration")

        self.action_summary_data = QAction("Data Summary", self)
        self.action_summary_data.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'summary.svg')))
        self.action_summary_data.triggered.connect(self.open_summary_data_dialog_lazy)

        self.action_normality_test = QAction("Normality Test", self)
        self.action_normality_test.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'normality.svg')))
        self.action_normality_test.triggered.connect(self.open_normality_test_dialog_lazy)


        self.menu_exploration.addAction(self.action_summary_data)
        self.menu_exploration.addAction(self.action_normality_test)

        self.menu_premodeling = self.menu_bar.addMenu("Pre-Modeling")
        self.action_correlation = QAction("Correlation", self)
        self.action_correlation.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'correlation.svg')))
        self.action_correlation.triggered.connect(self.open_correlation_matrix_dialog_lazy)

        self.action_multicollinearity = QAction("Multicollinearity", self)
        self.action_multicollinearity.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'multicolinierity.svg')))
        self.action_multicollinearity.triggered.connect(self.open_multicollinearity_dialog_lazy)

        self.action_variable_selection = QAction("Variable Selection", self)
        self.action_variable_selection.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'varselection.svg')))
        self.action_variable_selection.triggered.connect(self.open_variable_selection_dialog_lazy)

        self.menu_premodeling.addAction(self.action_correlation)
        self.menu_premodeling.addAction(self.action_multicollinearity)
        self.menu_premodeling.addAction(self.action_variable_selection)

        # Menu "Graph"
        self.menu_graph = self.menu_bar.addMenu("Graph")

        self.action_scatter_plot = QAction("Scatter Plot", self)
        self.action_scatter_plot.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'scatterplot.svg')))
        self.action_scatter_plot.triggered.connect(self.open_scatter_plot_dialog_lazy)

        self.action_box_plot = QAction("Box Plot", self)
        self.action_box_plot.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'boxplot.svg')))
        self.action_box_plot.triggered.connect(self.open_box_plot_dialog_lazy)

        self.action_line_plot = QAction("Line Plot", self)
        self.action_line_plot.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'lineplot.svg')))
        self.action_line_plot.triggered.connect(self.open_line_plot_dialog_lazy)

        self.action_histogram = QAction("Histogram", self)
        self.action_histogram.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'histogram.svg')))
        self.action_histogram.triggered.connect(self.open_histogram_dialog_lazy)

        # Menambahkan plot-plot ke menu Graph
        self.menu_graph.addAction(self.action_scatter_plot)
        self.menu_graph.addAction(self.action_box_plot)
        self.menu_graph.addAction(self.action_line_plot)
        self.menu_graph.addAction(self.action_histogram)
        # Menu "Model"
        menu_model = self.menu_bar.addMenu("Model")

        # Submenu "Area Level"
        menu_area_level = QMenu("Area Level", self)
        menu_area_level.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'arealevel.svg')))
        action_eblup_area = QAction("EBLUP", self)
        action_eblup_area.triggered.connect(self.show_modeling_sae_dialog_lazy)
        action_hb_beta = QAction("HB Beta", self)
        action_hb_beta.triggered.connect(self.show_modeling_saeHB_dialog_lazy)
        menu_area_level.addAction(action_eblup_area)
        menu_area_level.addAction(action_hb_beta)

        # Submenu "Unit Level"
        menu_unit_level = QMenu("Unit Level", self)
        menu_unit_level.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'unitlevel.svg')))
        action_eblup_unit = QAction("EBLUP", self)
        action_eblup_unit.triggered.connect(self.show_modeling_sae_unit_dialog_lazy)
        action_hb_normal = QAction("HB Normal", self)
        action_hb_normal.triggered.connect(self.show_modeling_saeHB_normal_dialog_lazy)
        menu_unit_level.addAction(action_eblup_unit)
        menu_unit_level.addAction(action_hb_normal)

        # Submenu "Pseudo"
        menu_pseudo = QMenu("Pseudo", self)
        menu_pseudo.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'pseudo.svg')))
        action_eblup_pseudo = QAction("EBLUP", self)
        action_eblup_pseudo.triggered.connect(self.show_modellig_sae_pseudo_dialog_lazy)
        menu_pseudo.addAction(action_eblup_pseudo)

        # Submenu "Projection"
        menu_projection = QMenu("Projection", self)
        menu_projection.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'projection.svg')))
        action_projection = QAction("Projection", self)
        action_projection.triggered.connect(self.show_projection_variabel_dialog_lazy)
        menu_projection.addAction(action_projection)


        # Menambahkan submenu ke menu "Model"
        menu_model.addMenu(menu_area_level)
        menu_model.addMenu(menu_unit_level)
        menu_model.addMenu(menu_pseudo)
        menu_model.addMenu(menu_projection)



         # Menu 'Compute'
        menu_compute = self.menu_bar.addMenu("Compute")
        compute_new_var = QAction("Compute New Variable", self)
        compute_new_var.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'compute.svg')))
        compute_new_var.triggered.connect(self.show_compute_variable_dialog_lazy)
        menu_compute.addAction(compute_new_var)
        
        # Menu "About"
        menu_about = self.menu_bar.addMenu("About")
        action_about_info = QAction("About This App", self)
        action_about_info.triggered.connect(self.open_about_dialog)
        action_about_info.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.svg')))
        menu_about.addAction(action_about_info)
        
        action_header_icon_info = QAction("Header Icon Info", self)
        action_header_icon_info.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'information.svg')))
        action_header_icon_info.triggered.connect(self.show_header_icon_info)
        menu_about.addAction(action_header_icon_info)
        
        # Add R Packages Used menu
        action_r_packages_info = QAction("R Packages Used", self)
        action_r_packages_info.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'R.svg')))
        action_r_packages_info.triggered.connect(self.show_r_packages_info)
        menu_about.addAction(action_r_packages_info)
        

        # Tool Bar
        self.toolBar = QToolBar(self)
        self.toolBar.setIconSize(QSize(45, 35))
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)  # Perbaikan dilakukan di sini
        # Actions for Toolbar
        self.actionLoad_file = QAction(self)  # Menggunakan self untuk referensi instance
        icon_load = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'open.svg'))
        self.actionLoad_file.setIcon(icon_load)
        self.actionLoad_file.setText("Load File")
        self.toolBar.addAction(self.actionLoad_file)

        self.actionSave_Data = QAction(self)  # Menggunakan self untuk referensi instance
        icon_save = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'save.svg'))
        self.actionSave_Data.setIcon(icon_save)
        self.actionSave_Data.setText("Save Data")
        self.toolBar.addAction(self.actionSave_Data)

        self.actionUndo = QAction(self)
        icon_undo = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'undo.svg'))
        self.actionUndo.setIcon(icon_undo)
        self.actionUndo.setText("Undo")
        self.actionUndo.triggered.connect(self.undo_action)
        self.toolBar.addAction(self.actionUndo)

        self.actionRedo = QAction(self)
        icon_redo = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'redo.svg'))
        self.actionRedo.setIcon(icon_redo)
        self.actionRedo.setText("Redo")
        self.actionRedo.triggered.connect(self.redo_action)
        self.toolBar.addAction(self.actionRedo)
        
        self.actionCompute = QAction(self)
        icon_compute = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'compute.svg'))
        self.actionCompute.setIcon(icon_compute)
        self.actionCompute.setText("Compute New Variable")
        self.actionCompute.triggered.connect(self.show_compute_variable_dialog_lazy)
        self.toolBar.addAction(self.actionCompute)
        
        # Shortcuts for "Go to Start/End Row/Column"
        self.go_to_start_row_action = QAction(self)
        self.go_to_start_row_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Up))
        self.go_to_start_row_action.triggered.connect(lambda : go_to_start_row(self))
        self.addAction(self.go_to_start_row_action)

        self.go_to_end_row_action = QAction(self)
        self.go_to_end_row_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Down))
        self.go_to_end_row_action.triggered.connect(lambda : go_to_end_row(self))
        self.addAction(self.go_to_end_row_action)

        self.go_to_start_column_action = QAction(self)
        self.go_to_start_column_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Left))
        self.go_to_start_column_action.triggered.connect(lambda : go_to_start_column(self))
        self.addAction(self.go_to_start_column_action)

        self.go_to_end_column_action = QAction(self)
        self.go_to_end_column_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Right))
        self.go_to_end_column_action.triggered.connect(lambda : go_to_end_column(self))
        self.addAction(self.go_to_end_column_action)

        # Add spacer to push following items to the right
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolBar.addWidget(spacer)

        # Add "Setting" button to the right
        self.actionSetting = QAction(self)
        icon_setting = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'setting.svg'))
        self.actionSetting.setIcon(icon_setting)
        self.actionSetting.setText("Setting")
        self.actionSetting.triggered.connect(self.change_font_size)
        self.toolBar.addAction(self.actionSetting)
        

        # Menu "Settings"
        menu_settings = self.menu_bar.addMenu("Settings")
        action_change_font_size = QAction("Change Font Size", self)
        action_change_font_size.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'setting.svg')))
        action_change_font_size.triggered.connect(self.change_font_size)
        menu_settings.addAction(action_change_font_size)

        # Menetapkan ukuran default
        self.resize(800, 600)

    
    def change_font_size(self):
        """
        Opens a dialog to change the font size of the application.
        The dialog presents three font size options: "Small", "Medium", and "Big".
        The user can select a font size from a combo box, and the selected size
        will be applied to the application if the user confirms the selection.
        The dialog also displays a sample text ("AaBbCc") that updates in real-time
        to reflect the selected font size.
        Attributes:
            sizes (dict): A dictionary mapping font size names to their corresponding pixel values.
            items (list): A list of font size names.
            dialog (QDialog): The dialog window for selecting the font size.
            layout (QVBoxLayout): The main layout of the dialog.
            combo_box (QComboBox): The combo box for selecting the font size.
            display (QLabel): The label displaying the sample text with the selected font size.
            button_box (QHBoxLayout): The layout containing the OK and Cancel buttons.
            ok_button (QPushButton): The button to confirm the font size selection.
            cancel_button (QPushButton): The button to cancel the font size selection.
        Methods:
            update_display_font_size: Updates the sample text's font size based on the selected size in the combo box.
        """
        
        sizes = {"Small": 10, "Medium": 12, "Large": 16}
        items = list(sizes.keys())

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Font Size")
        dialog.setMinimumWidth(200)

        layout = QVBoxLayout(dialog)

        combo_box = QComboBox()
        combo_box.addItems(items)
        default_size = next(key for key, value in sizes.items() if value == self.font_size)
        combo_box.setCurrentText(default_size)
        layout.addWidget(combo_box)
        
        display = QLabel("AaBbCc")
        display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display.setStyleSheet(f"font-size: {self.font_size}px;")
        layout.addWidget(display)
    
        def update_display_font_size():
            size = combo_box.currentText()
            display.setStyleSheet(f"font-size: {sizes[size]}px;")

        combo_box.currentTextChanged.connect(update_display_font_size)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_size = combo_box.currentText()
            self.set_font_size(sizes[selected_size])
            self.font_size = sizes[selected_size]

    def set_font_size(self, size):
        """
        Sets the font size for the main window.
        Args:
            size (int): The desired font size to be set.
        This method updates the stylesheet of the main window with the specified font size.
        """
        
        stylesheet = self.load_stylesheet_with_font_size(size)
        self.setStyleSheet(stylesheet)

    def load_stylesheet_with_font_size(self, size):
        """
        Memuat stylesheet dan mengganti ukuran font global.
        """
        stylesheet_path = os.path.join(self.path, 'assets', 'style', 'style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as file:
                stylesheet = file.read()
                stylesheet = stylesheet.replace("__FONT_SIZE__", f"{size}px")
                return stylesheet
        else:
            print(f"Stylesheet tidak ditemukan di {stylesheet_path}")
            return ""
    
    def open_summary_data_dialog_lazy(self):
        """
        Lazily initializes and opens the summary data dialog.
        This method checks if the 'show_summary_data_dialog' attribute exists.
        If it does not exist, it initializes it with an instance of SummaryDataDialog.
        Then, it calls the 'open_summary_data_dialog' method to open the dialog.
        """
        
        try:
            if not hasattr(self, 'show_summary_data_dialog'):
                self.show_summary_data_dialog = SummaryDataDialog(self)
            self.open_summary_data_dialog()
        except Exception as e:
            self.log_exception(e, "Opening Summary Data Dialog")
            QMessageBox.critical(self, "Error", f"Failed to open Summary Data Dialog: {str(e)}")

    def open_normality_test_dialog_lazy(self):
        """
        Lazily initializes and opens the normality test dialog.
        This method checks if the normality test dialog has already been created.
        If not, it initializes the dialog and then opens it. If the dialog has 
        already been created, it simply opens the existing instance.
        """
        
        try:
            if not hasattr(self, 'show_normality_test_dialog'):
                self.show_normality_test_dialog = NormalityTestDialog(self)
            self.open_normality_test_dialog()
        except Exception as e:
            self.log_exception(e, "Opening Normality Test Dialog")
            QMessageBox.critical(self, "Error", f"Failed to open Normality Test Dialog: {str(e)}")

    def open_multicollinearity_dialog_lazy(self):
        """
        Lazily initializes and opens the multicollinearity dialog.
        This method checks if the 'show_multicollinearity_dialog' attribute exists.
        If it does not, it initializes it with an instance of MulticollinearityDialog.
        Then, it opens the multicollinearity dialog.
        Returns:
            None
        """
        
        if not hasattr(self, 'show_multicollinearity_dialog'):
            self.show_multicollinearity_dialog = MulticollinearityDialog(self)
        self.open_multicollinearity_dialog()

    def open_variable_selection_dialog_lazy(self):
        """
        Lazily initializes and opens the variable selection dialog.
        This method checks if the 'show_variable_selection_dialog' attribute
        exists. If it does not, it initializes it with an instance of 
        VariableSelectionDialog. Then, it calls the method to open the 
        variable selection dialog.
        """
        
        if not hasattr(self, 'show_variable_selection_dialog'):
            self.show_variable_selection_dialog = VariableSelectionDialog(self)
        self.open_variable_selection_dialog()
    
    def open_scatter_plot_dialog_lazy(self):
        """
        Lazily initializes and opens the scatter plot dialog.
        This method checks if the scatter plot dialog has already been created.
        If not, it initializes the dialog and then opens it. This ensures that
        the dialog is only created when needed, potentially saving resources.
        Attributes:
            show_scatter_plot_dialog (ScatterPlotDialog): The scatter plot dialog instance.
        """
        
        if not hasattr(self, 'show_scatter_plot_dialog'):
            self.show_scatter_plot_dialog = ScatterPlotDialog(self)
        self.open_scatter_plot_dialog()

    def open_correlation_matrix_dialog_lazy(self):
        """
        Lazily initializes and opens the correlation matrix dialog.
        This method checks if the correlation matrix dialog has already been created.
        If not, it initializes the dialog. Then, it opens the dialog.
        Attributes:
            show_correlation_matrix_dialog (CorrelationMatrixDialog): The correlation matrix dialog instance.
        """
        
        if not hasattr(self, 'show_correlation_matrix_dialog'):
            self.show_correlation_matrix_dialog = CorrelationMatrixDialog(self)
        self.open_correlation_matrix_dialog()

    def open_box_plot_dialog_lazy(self):
        """
        Lazily initializes and opens the box plot dialog.
        This method checks if the 'show_box_plot_dialog' attribute exists.
        If it does not, it initializes 'show_box_plot_dialog' with an instance
        of BoxPlotDialog. Then, it calls the method to open the box plot dialog.
        """
        
        if not hasattr(self, 'show_box_plot_dialog'):
            self.show_box_plot_dialog = BoxPlotDialog(self)
        self.open_box_plot_dialog()

    def open_line_plot_dialog_lazy(self):
        """
        Lazily initializes and opens the line plot dialog.
        This method checks if the 'show_line_plot_dialog' attribute exists.
        If it does not, it initializes 'show_line_plot_dialog' with an instance
        of LinePlotDialog. Then, it calls the method to open the line plot dialog.
        """
        
        if not hasattr(self, 'show_line_plot_dialog'):
            self.show_line_plot_dialog = LinePlotDialog(self)
        self.open_line_plot_dialog()

    def open_histogram_dialog_lazy(self):
        """
        Opens the histogram dialog lazily.
        This method checks if the histogram dialog has already been created.
        If not, it initializes the HistogramDialog and assigns it to the 
        'show_histogram_dialog' attribute. Then, it opens the histogram dialog.
        """
        
        if not hasattr(self, 'show_histogram_dialog'):
            self.show_histogram_dialog = HistogramDialog(self)
        self.open_histogram_dialog()
    
    def open_summary_data_dialog(self):
        """
        Opens the summary data dialog.
        This method sets the models for the summary data dialog and then displays the dialog.
        It uses `self.model1` and `self.model2` as the models to be set in the dialog.
        Returns:
            None
        """
        
        self.show_summary_data_dialog.set_model(self.model1, self.model2)
        self.show_summary_data_dialog.show()
        
    def open_normality_test_dialog(self):
        """
        Opens the normality test dialog.
        This method sets the models for the normality test dialog and then displays the dialog.
        It uses `self.model1` and `self.model2` as the models to be set in the dialog.
        Returns:
            None
        """
        
        self.show_normality_test_dialog.set_model( self.model1, self.model2)
        self.show_normality_test_dialog.show()

    def open_scatter_plot_dialog(self):
        """
        Opens the scatter plot dialog and sets the models for the dialog.
        This method sets the models for the scatter plot dialog using 
        `self.model1` and `self.model2`, and then displays the dialog.
        """
        
        self.show_scatter_plot_dialog.set_model(self.model1, self.model2)
        self.show_scatter_plot_dialog.show()

    def open_line_plot_dialog(self):
        """
        Opens the line plot dialog and sets the models for the dialog.
        This method sets the models for the line plot dialog using `self.model1` 
        and `self.model2`, and then displays the dialog.
        Returns:
            None
        """
        
        self.show_line_plot_dialog.set_model(self.model1, self.model2)
        self.show_line_plot_dialog.show()
    
    def open_box_plot_dialog(self):
        """
        Opens the box plot dialog and sets the models for the dialog.
        This method sets the models for the box plot dialog using `self.model1` and `self.model2`,
        and then displays the dialog.
        Returns:
            None
        """
        
        self.show_box_plot_dialog.set_model(self.model1, self.model2)
        self.show_box_plot_dialog.show()

    def open_correlation_matrix_dialog(self):
        """
        Opens the correlation matrix dialog.
        This method sets the model data for the correlation matrix dialog
        and then displays the dialog to the user.
        The models used are `self.model1` and `self.model2`.
        """
        
        self.show_correlation_matrix_dialog.set_model(self.model1, self.model2)
        self.show_correlation_matrix_dialog.show()
    
    def open_multicollinearity_dialog(self):
        """
        Opens the multicollinearity dialog and sets the models for it.
        This method sets the models for the multicollinearity dialog using
        `self.model1` and `self.model2`, and then displays the dialog.
        """
        
        self.show_multicollinearity_dialog.set_model(self.model1, self.model2)
        self.show_multicollinearity_dialog.show()
    
    def open_histogram_dialog(self):
        """
        Opens the histogram dialog and sets the models for it.
        This method sets the models for the histogram dialog using `self.model1` and `self.model2`,
        and then displays the histogram dialog.
        """
        
        self.show_histogram_dialog.set_model(self.model1, self.model2)
        self.show_histogram_dialog.show()

    def open_variable_selection_dialog(self):
        """
        Opens the variable selection dialog.
        This method sets the model for the variable selection dialog using 
        `self.model1` and `self.model2`, and then displays the dialog.
        """
        
        self.show_variable_selection_dialog.set_model(self.model1, self.model2)
        self.show_variable_selection_dialog.show()

    def show_modeling_sae_dialog_lazy(self):
        """
        Lazily initializes and displays the ModelingSaeDialog.
        If the ModelingSaeDialog has not been created yet, this method will
        instantiate it and set its model to `self.model1`. Then, it will
        display the dialog.
        Returns:
            None
        """
        
        if self.show_modeling_sae_dialog is None:
            self.show_modeling_sae_dialog = ModelingSaeDialog(self)
        self.show_modeling_sae_dialog.set_model(self.model1)
        self.show_modeling_sae_dialog.show()

    def show_modeling_saeHB_dialog_lazy(self):
        """
        Displays the ModelingSaeHBDialog lazily.
        This method initializes the ModelingSaeHBDialog if it has not been created yet,
        sets its model to `self.model1`, and then shows the dialog.
        Attributes:
            show_modeling_saeHB_dialog (ModelingSaeHBDialog): The dialog instance to be shown.
            model1: The model to be set in the dialog.
        """
        
        if self.show_modeling_saeHB_dialog is None:
            self.show_modeling_saeHB_dialog = ModelingSaeHBDialog(self)
        self.show_modeling_saeHB_dialog.set_model(self.model1)
        self.show_modeling_saeHB_dialog.show()

    def show_modeling_sae_unit_dialog_lazy(self):
        """
        Lazily initializes and displays the ModelingSaeUnitDialog.
        If the dialog has not been created yet, it initializes it with the current instance.
        Then, it sets the model for the dialog and shows it.
        Attributes:
            show_modeling_sae_unit_dialog (ModelingSaeUnitDialog): The dialog for modeling SAE units.
            model1: The model to be set in the dialog.
        """
        
        if self.show_modeling_sae_unit_dialog is None:
            self.show_modeling_sae_unit_dialog = ModelingSaeUnitDialog(self)
        self.show_modeling_sae_unit_dialog.set_model(self.model1)
        self.show_modeling_sae_unit_dialog.show()

    def show_modeling_saeHB_normal_dialog_lazy(self):
        """
        Lazily initializes and displays the ModelingSaeHBNormalDialog.
        If the dialog has not been created yet, it initializes a new instance
        of ModelingSaeHBNormalDialog and sets its model to self.model1. 
        Then, it shows the dialog.
        Attributes:
            show_modeling_saeHB_normal_dialog (ModelingSaeHBNormalDialog): 
            The dialog instance to be displayed.
            model1: The model to be set in the dialog.
        """
        
        if self.show_modeling_saeHB_normal_dialog is None:
            self.show_modeling_saeHB_normal_dialog = ModelingSaeHBNormalDialog(self)
        self.show_modeling_saeHB_normal_dialog.set_model(self.model1)
        self.show_modeling_saeHB_normal_dialog.show()

    def show_modellig_sae_pseudo_dialog_lazy(self):
        """
        Lazily initializes and displays the Modeling SAE Pseudo dialog.
        This method checks if the `show_modellig_sae_pseudo_dialog` attribute is None.
        If it is, it initializes a new instance of `ModelingSaePseudoDialog` with the current
        instance (`self`) as the parent. It then sets the model for the dialog using `self.model1`
        and displays the dialog.
        Returns:
            None
        """
        
        if self.show_modellig_sae_pseudo_dialog is None:
            self.show_modellig_sae_pseudo_dialog = ModelingSaePseudoDialog(self)
        self.show_modellig_sae_pseudo_dialog.set_model(self.model1)
        self.show_modellig_sae_pseudo_dialog.show()

    def show_compute_variable_dialog_lazy(self):
        """
        Displays the Compute Variable dialog lazily.
        This method initializes the Compute Variable dialog if it hasn't been created yet,
        sets its model to `self.model1`, and then shows the dialog.
        If `self.show_compute_variable_dialog` is already initialized, it simply updates
        the model and shows the dialog.
        Returns:
            None
        """
        
        if self.show_compute_variable_dialog is None:
            self.show_compute_variable_dialog = ComputeVariableDialog(self)
        self.show_compute_variable_dialog.set_model(self.model1)
        self.show_compute_variable_dialog.show()

    def show_projection_variabel_dialog_lazy(self):
        """
        Lazily initializes and displays the ProjectionDialog.
        This method checks if the `show_projection_variabel_dialog` attribute is None.
        If it is, it initializes it with a new instance of `ProjectionDialog`.
        It then sets the model for the dialog and checks if the prerequisites for
        showing the dialog are met. If they are, it displays the dialog.
        Attributes:
            show_projection_variabel_dialog (ProjectionDialog): The dialog to be shown.
            model1: The model to be set in the dialog.
        Returns:
            None
        """
        
        if self.show_projection_variabel_dialog is None:
            self.show_projection_variabel_dialog = ProjectionDialog(self)
        self.show_projection_variabel_dialog.set_model(self.model1)
        if self.show_projection_variabel_dialog.show_prerequisites():
            self.show_projection_variabel_dialog.show()

    def open_about_dialog(self):
        """
        Opens the About dialog window.
        This method creates an instance of the AboutDialog class, passing the
        current instance as the parent, and then executes the dialog.
        """
        
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def add_row(self, sheet_number):
        """Sinkronisasi data ketika baris baru ditambahkan di SpreadsheetWidget."""
        if sheet_number == 1:
            # Tambahkan baris baru di DataFrame data1
            new_row = pl.DataFrame({col: [""] for col in self.data1.columns})
            self.data1 = pl.concat([self.data1, new_row])
        elif sheet_number == 2:
            pass  # Tidak digunakan untuk Sheet 2
    
    def add_column(self, sheet_number):
        """Sinkronisasi data ketika kolom baru ditambahkan di SpreadsheetWidget."""
        if sheet_number == 1:
            # Tambahkan kolom baru di DataFrame data1
            new_column_name = f"Column {self.data1.shape[1] + 1}"
            new_column = pl.DataFrame({new_column_name: [""] * self.data1.shape[0]})
            self.data1 = pl.concat([self.data1, new_column], how="horizontal")
        elif sheet_number == 2:
            pass  # Tidak digunakan untuk Sheet 2
    
    def update_table(self, sheet_number, model):
        """Update the table for the specified sheet with a new model."""
        if sheet_number == 1:
            self.spreadsheet.setModel(model)
            self.model1 = model
            self.spreadsheet.resizeColumnsToContents()
            self.tab_widget.setCurrentWidget(self.tab1)
            dialogs = [
                self.show_modeling_sae_dialog,
                self.show_modeling_saeHB_dialog,
                self.show_modeling_sae_unit_dialog,
                self.show_modeling_saeHB_normal_dialog,
                self.show_modellig_sae_pseudo_dialog,
                self.show_compute_variable_dialog,
                self.show_projection_variabel_dialog,
            ]
            for dialog in dialogs:
                if dialog:
                    dialog.set_model(model)
        elif sheet_number == 2:
            self.table_view2.setModel(model)
            self.model2 = model
            self.table_view2.resizeColumnsToContents()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for copy, paste, undo, redo, and navigation."""
        
        # Handle standard shortcuts first
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
            return
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste_selection()
            return
        elif event.matches(QKeySequence.StandardKey.Undo):
            self.undo_action()
            return
        elif event.matches(QKeySequence.StandardKey.Redo):
            self.redo_action()
            return
        
        # Handle navigation shortcuts manually
        modifiers = event.modifiers()
        key = event.key()
        
        if modifiers == Qt.Modifier.CTRL:
            if key == Qt.Key.Key_Up:
                go_to_start_row(self)
                return
            elif key == Qt.Key.Key_Down:
                go_to_end_row(self)
                return
            elif key == Qt.Key.Key_Left:
                go_to_start_column(self)
                return
            elif key == Qt.Key.Key_Right:
                go_to_end_column(self)
                return
            elif key == Qt.Key.Key_D:
                # Handle Ctrl+D for recent data
                self.load_temp_data()
                return
            elif key == Qt.Key.Key_2:
                # Handle Ctrl+2 for secondary data
                if hasattr(self, 'load_secondary_data') and self.load_secondary_data.triggered:
                    self.load_secondary_data.triggered.emit()
                return
        
        # Call parent implementation for unhandled events
        super().keyPressEvent(event)

    def copy_selection(self):
        """Copy selected cells to clipboard."""
        selection = self.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            data = '\n'.join(['\t'.join([self.model1.data(index, Qt.ItemDataRole.DisplayRole) for index in row]) for row in self.group_by_row(selection)])
            clipboard = QApplication.clipboard()
            clipboard.setText(data)

    def paste_selection(self):
        """Paste clipboard content to selected cells."""
        clipboard = QApplication.clipboard()
        data = clipboard.text().split('\n')
        selection = self.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            start_row = selection[0].row()
            start_col = selection[0].column()
            for i, row in enumerate(data):
                for j, value in enumerate(row.split('\t')):
                    index = self.model1.index(start_row + i, start_col + j)
                    self.model1.setData(index, value, Qt.ItemDataRole.EditRole)

    def undo_action(self):
        """Undo the last action."""
        self.model1.undo()

    def redo_action(self):
        """Redo the last undone action."""
        self.model1.redo()

    def group_by_row(self, selection):
        """Group selected indexes by row."""
        rows = {}
        for index in selection:
            if index.row() not in rows:
                rows[index.row()] = []
            rows[index.row()].append(index)
        return [rows[row] for row in sorted(rows)]
    
    def show_output(self, title, content):
        """Display output in the Output tab"""
        label = QLabel(content)
        self.output_layout.addWidget(label)
        self.output_tab_widget.setCurrentIndex(0)

    def show_header_context_menu(self, pos):
        """Show context menu for header."""
        header = self.spreadsheet.horizontalHeader()
        logical_index = header.logicalIndexAt(pos)
        menu = QMenu(self)
        rename_action = QAction("Rename Column", self)
        rename_action.triggered.connect(lambda: self.rename_column(logical_index))
        menu.addAction(rename_action)
        
        edit_type_action = QAction("Edit Data Type", self)
        edit_type_action.triggered.connect(lambda: self.edit_data_type(logical_index))
        menu.addAction(edit_type_action)
        
        selection = self.spreadsheet.selectionModel().selectedIndexes()
        has_selection = bool(selection)
        
        delete_column_action = QAction("Delete Column", self)
        delete_column_action.triggered.connect(lambda : confirm_delete_selected_columns(self))
        delete_column_action.setEnabled(has_selection)
        menu.addAction(delete_column_action)
        
        add_column_before_action = QAction("Add Column Before", self)
        add_column_before_action.triggered.connect(lambda: show_add_column_before_dialog(self))
        add_column_before_action.setEnabled(has_selection)
        menu.addAction(add_column_before_action)
        
        add_column_after_action = QAction("Add Column After", self)
        add_column_after_action.triggered.connect(lambda: show_add_column_after_dialog(self))
        add_column_after_action.setEnabled(has_selection)
        menu.addAction(add_column_after_action)
        
        menu.exec(header.mapToGlobal(pos))

    def rename_column(self, column_index):
        """Rename the column at the given index."""
        current_name = self.model1.headerData(column_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        new_name, ok = QInputDialog.getText(self, "Rename Column", "New column name:", text=current_name)
        if ok and new_name:
            self.model1.rename_column(column_index, new_name)
            self.update_table(1, self.model1)

    def edit_data_type(self, column_index):
        """Edit the data type of the column at the given index."""
        current_type = self.model1.get_column_type(column_index)
        if current_type==pl.Utf8:
            current_type = "String"
        elif current_type==pl.Int64:
            current_type = "Integer"
        elif current_type==pl.Float64:
            current_type = "Float"
        type_list = ["String", "Integer", "Float"]
        current_index = type_list.index(current_type)
        new_type, ok = QInputDialog.getItem(self, "Edit Data Type", "Select new data type:", type_list, current=current_index)
        if ok and new_type:
            self.model1.set_column_type(column_index, new_type)
            self.update_table(1, self.model1)
    
    def set_path(self, path):
        """
        Sets the path attribute for the MainWindow instance.
        Args:
            path (str): The path to be set.
        """
        
        self.path=path
    
    def remove_output(self, card_frame):
        """Menghapus output dari layout"""
        self.output_layout.removeWidget(card_frame)
        card_frame.deleteLater()

        # Hapus spacer jika masih ada widget lain
        if self.output_layout.count() > 0:
            last_item = self.output_layout.itemAt(self.output_layout.count() - 1)
            if isinstance(last_item.spacerItem(), QSpacerItem):
                self.output_layout.removeItem(last_item)

        # Tambahkan stretch hanya jika tidak ada output tersisa
        if self.output_layout.count() == 0:
            self.output_layout.addStretch()

    def copy_output_image(self, card_frame):
        """Menyalin gambar output ke clipboard"""
        for child in card_frame.findChildren(QLabel):
            pixmap = child.pixmap()
            
            if pixmap and not pixmap.isNull():
                temp_folder = os.path.join(self.path, 'temp')
                temp_path = os.path.join(temp_folder, 'temp_image.png')

                os.makedirs(temp_folder, exist_ok=True)

                if pixmap.save(temp_path):
                    print(f"Gambar disimpan di: {temp_path}")
                    
                    clipboard = QApplication.clipboard()
                    clipboard.setPixmap(QPixmap(temp_path))

                    if os.path.exists(temp_path):  
                        os.remove(temp_path)
                break

    def show_context_menu(self, pos, card_frame):
        """Menampilkan menu klik kanan di setiap output"""
        menu = QMenu(self)
        delete_action = menu.addAction("Hapus Output")
        copy_image_action = menu.addAction("Copy Output Image")
        action = menu.exec(card_frame.mapToGlobal(pos))

        if action == delete_action:
            self.remove_output(card_frame)
        elif action == copy_image_action:
            self.copy_output_image(card_frame)

    def autosave_data(self):
        """
        Save the current state of data1, data2 (as parquet), and output (as JSON) to temporary files.
        """
        try:
            app_data_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
            os.makedirs(app_data_dir, exist_ok=True)
            temp_dir = os.path.join(app_data_dir, 'file-data')
            os.makedirs(temp_dir, exist_ok=True)

            # Save data1 and data2 as parquet
            data1_path = os.path.join(temp_dir, 'sae_pisan_data1.parquet')
            data2_path = os.path.join(temp_dir, 'sae_pisan_data2.parquet')
            self.model1.get_data().write_parquet(data1_path)
            self.model2.get_data().write_parquet(data2_path)

            # Save output as JSON
            output_path = os.path.join(temp_dir, 'sae_pisan_output.json')
            import numpy as np

            def make_json_serializable(obj):
                if isinstance(obj, dict):
                    return {k: make_json_serializable(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [make_json_serializable(v) for v in obj]
                if isinstance(obj, np.ndarray) or hasattr(obj, 'tolist'):
                    return obj.tolist()
                if isinstance(obj, (int, float, str, type(None), bool)):
                    return obj
                return str(obj)

            serializable_data = make_json_serializable(self.data)
            data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'output': serializable_data
            }
            with open(output_path, 'w') as file:
                json.dump(data, file)

            self._cleanup_unused_images(temp_dir, serializable_data)

            if self.isActiveWindow():
                self.show_toast()
        except Exception as e:
            self.log_exception(e, "Autosave Data")

    def _collect_used_images(self, outputs):
        used_images = set()
        for output in outputs:
            result = output.get("result", {})
            plot_paths = result.get("Plot")
            if isinstance(plot_paths, list):
                for p in plot_paths:
                    used_images.add(os.path.abspath(p))
            elif isinstance(plot_paths, str):
                used_images.add(os.path.abspath(plot_paths))
        return used_images

    def _cleanup_unused_images(self, temp_dir, serializable_data):
        temp_img_dir = os.path.join(temp_dir, 'temp')
        if not os.path.exists(temp_img_dir):
            return
        used_images = self._collect_used_images(serializable_data)
        used_images.update(self._collect_used_images(self.data))
        for fname in os.listdir(temp_img_dir):
            fpath = os.path.abspath(os.path.join(temp_img_dir, fname))
            if fpath not in used_images:
                try:
                    os.remove(fpath)
                except Exception:
                    pass

    def load_temp_data(self):
        """
        Load data1 and data2 from parquet, and output from JSON, if they exist.
        """
        try:
            app_path = os.path.join(os.getenv("APPDATA"), "saePisan")
            temp_dir = os.path.join(app_path, 'file-data')
            data1_path = os.path.join(temp_dir, 'sae_pisan_data1.parquet')
            data2_path = os.path.join(temp_dir, 'sae_pisan_data2.parquet')
            output_path = os.path.join(temp_dir, 'sae_pisan_output.json')
            if os.path.exists(data1_path) and os.path.exists(data2_path) and os.path.exists(output_path):
                reply = QMessageBox.question(self, 'Load Temporary Data',
                                            'Temporary data was found. Do you want to load it?',
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.data1 = pl.read_parquet(data1_path)
                    self.data2 = pl.read_parquet(data2_path)
                    self.model1.set_data(self.data1)
                    self.model2.set_data(self.data2)
                    self.update_table(1, self.model1)
                    self.update_table(2, self.model2)
                    with open(output_path, 'r') as file:
                        data = json.load(file)
                        self.set_output_data(data.get('output', []), timestamp=data.get('timestamp'))
            else:
                QMessageBox.warning(self, 'No Recent Data', 'No recent data file was found.')
        except Exception as e:
            self.log_exception(e, "Load Temporary Data")
            QMessageBox.warning(self, 'Error Loading Data',
                                f'An error occurred while loading temporary data: {e}')

    def set_output_data(parent, output_data, timestamp=None):
        """
        Menampilkan kembali output card dari data hasil get_output_data.
        """
        for output in output_data:
            r_script = output.get("r_script", "")
            results = output.get("result", "")
            for key, value in results.items():
                if isinstance(value, dict):
                    df = pl.DataFrame(value)
                    results[key] = df
                else:
                    results[key] = value
            if "Plot" in results:
                display_script_and_output(parent, r_script, results, plot_paths=results["Plot"], timestamps=timestamp)
            else:
                display_script_and_output(parent, r_script, results, plot_paths=None, timestamps=timestamp)
        
    def show_header_icon_info(self):
        """
        Show a dialog explaining the meaning of header icons in the data table.
        """
        msg = (
            "<b>Header Icon Legend:</b><br><br>"
            "<div style='display:flex; flex-direction:column; gap:8px;'>"
            "<div><img src='assets/nominal.svg' width='24' height='24' style='vertical-align:middle;'> <b>Nominal/String</b></div>"
            "<div><img src='assets/null.svg' width='24' height='24' style='vertical-align:middle;'> <b>Null/Empty</b></div>"
            "<div><img src='assets/numeric.svg' width='24' height='24' style='vertical-align:middle;'> <b>Numeric</b></div>"
            "</div><br>"
            "<div style='max-width:350px;'>"
            "These icons indicate the data type of each column in the table. "
            "Nominal/String columns are represented by the nominal icon, "
            "Null/Empty columns are represented by the null icon, and "
            "Numeric columns are represented by the numeric icon."
            "</div>"
        )
        QMessageBox.information(self, "Header Icon Info", msg)
    
    def show_r_packages_info(self):
        """
        Show a dialog listing the R packages used and their versions in a single table with 6 columns (3 pairs of Package/Version side by side).
        """
        try:
            import rpy2.robjects as ro
            packages = [
                "sae", "arrow", "sae.projection", "emdi", "xgboost", "LiblineaR",
                "kernlab", "GGally", "ggplot2", "ggcorrplot", "car", "nortest",
                "tidyr", "carData", "dplyr", "tseries", "FSelector", "rjags", "saeHB"
            ]
            versions = []
            for pkg in packages:
                try:
                    ver = ro.r(f"as.character(packageVersion('{pkg}'))")[0]
                except Exception:
                    ver = "Not Installed"
                versions.append((pkg, ver))

            # Arrange into 3 columns (each column is Package/Version pair)
            n_cols = 3
            n_rows = (len(versions) + n_cols - 1) // n_cols
            table_cells = []
            for i in range(n_rows):
                row = []
                for j in range(n_cols):
                    idx = i + j * n_rows
                    if idx < len(versions):
                        row.extend(versions[idx])
                    else:
                        row.extend(("", ""))
                table_cells.append(row)

            msg = "<b>R Packages Used:</b><br><br>"
            msg += "<table style='border-collapse:collapse;font-size:13px;'>"
            # Header
            msg += "<tr style='background-color:#f2f2f2;'>"
            for i in range(n_cols):
                msg += "<th style='border:1px solid #bbb; padding:6px 16px;'>Package</th>"
                msg += "<th style='border:1px solid #bbb; padding:6px 16px;'>Version</th>"
            msg += "</tr>"
            # Rows
            for row in table_cells:
                msg += "<tr>"
                for cell in row:
                    msg += f"<td style='border:1px solid #bbb; padding:6px 16px;'>{cell}</td>"
                msg += "</tr>"
            msg += "</table>"
        except Exception as e:
            msg = f"Could not retrieve R package versions.<br>Error: {e}"
        QMessageBox.information(self, "R Packages Used", msg)
            
    def show_toast(self):
        toast = CustomToast(
            parent=self,
            title="Saved",
            text="Data, Data Output, and Output was saved",
            duration=3000,
            position="top-right"
        )
        toast.set_border_radius(8)
        toast.show()
    
    def closeEvent(self, event):
        """Handle the close event to show a confirmation dialog."""
        
        try:
            reply = QMessageBox.question(self, 'Confirm Exit',
                                     'Are you sure you want to exit?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.autosave_data()
                import rpy2.robjects as ro
                if 'saeHB' in ro.r('loadedNamespaces()'):
                    ro.r('detach("package:saeHB", unload=TRUE)')
                if 'rjags' in ro.r('loadedNamespaces()'):
                    ro.r("unloadNamespace('rjags')")
                
                #to kill the process
                import os
                import psutil

                current_system_pid = os.getpid()

                this_system = psutil.Process(current_system_pid)
                this_system.terminate()
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            self.log_exception(e, "Close Event")
            QMessageBox.warning(self, 'Error', f'An error occurred while closing the application: {e}')

