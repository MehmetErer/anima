# -*- coding: utf-8 -*-

from anima.ui.base import AnimaDialogBase, ui_caller
from anima.ui.lib import QtCore, QtWidgets


def UI(app_in=None, executor=None, **kwargs):
    """
    :param app_in: A Qt Application instance, which you can pass to let the UI
      be attached to the given applications event process.

    :param executor: Instead of calling app.exec_ the UI will call this given
      function. It also passes the created app instance to this executor.

    """
    return ui_caller(app_in, executor, MainDialog, **kwargs)


class MainDialog(QtWidgets.QDialog, AnimaDialogBase):
    """Conformer MainDialog
    """

    def __init__(self, *args, **kwargs):
        super(MainDialog, self).__init__(*args, **kwargs)
        self.vertical_layout = None
        self._setup_ui()

    def _setup_ui(self):
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        ConformerUI(self.vertical_layout)
        self.setWindowTitle('Conformer')
        self.resize(500, 100)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)


class ConformerUI(object):
    """The main class that creates the UI widgets
    """

    def __init__(self, layout):
        import os
        import tempfile
        from anima.env import blackmagic
        from anima.utils import do_db_setup

        self.main_layout = layout
        self.resolve = None
        self.resolve_project = None
        self.connect_to_resolve()

        self.parent_widget = None
        self.active_projects_only_check_box = None
        self.project_combo_box = None
        self.seq_combo_box = None
        self.scene_combo_box = None
        self.shot_in_combo_box = None
        self.shot_out_label = None
        self.shot_out_combo_box = None
        self.width_line = None
        self.height_line = None
        self.fps_line = None
        self.filter_statuses_check_box = None
        self.wip_check_box = None
        self.hrev_check_box = None
        self.prev_check_box = None
        self.completed_check_box = None
        self.task_name_combo_box = None
        self.ext_name_combo_box = None
        self.plus_plates_check_box = None
        self.plus_refs_check_box = None
        self.record_in_check_box = None
        self.slated_check_box = None
        self.use_current_timeline = None
        self.conform_button = None
        self.start_date = None
        self.updated_shot_list = None
        self.status_button = None
        self.conform_updates_button = None

        xml_path = tempfile.gettempdir()
        xml_file_name = 'conformer___temp__1.8_fcpxml.fcpxml'
        xml_file_path = os.path.join(xml_path, xml_file_name)
        self.xml_path = xml_file_path

        do_db_setup()

        self._setup_ui()
        self._set_defaults()

    def _setup_ui(self):
        """setups UI
        """
        from functools import partial
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.parent_widget = self.main_layout.parent()

        resolve_project_label = QtWidgets.QLabel(self.parent_widget)
        resolve_project_label.setText(
            '%s - [%s fps] / Resolve' % (
                self.resolve_project.GetName(),
                self.resolve_project.GetSetting('timelineFrameRate'))
        )
        resolve_project_label.setStyleSheet(_fromUtf8("color: rgb(71, 143, 202);\n""font: 12pt;"))
        self.main_layout.addWidget(resolve_project_label)

        from anima.ui.utils import create_separator
        self.main_layout.addWidget(create_separator(self.parent_widget))

        h_layout1 = QtWidgets.QHBoxLayout()

        stalker_project_label = QtWidgets.QLabel(self.parent_widget)
        stalker_project_label.setText('Stalker Project:')
        stalker_project_label.setFixedWidth(100)
        h_layout1.addWidget(stalker_project_label)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        # Project Combo Box
        from anima.ui.widgets.project import ProjectComboBox
        self.project_combo_box = ProjectComboBox(self.parent_widget)
        self.project_combo_box.show_active_projects = True
        self.project_combo_box.setSizePolicy(size_policy)
        self.project_combo_box.currentIndexChanged.connect(partial(self.project_combo_box_changed))
        h_layout1.addWidget(self.project_combo_box)

        self.active_projects_only_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.active_projects_only_check_box.setText("Active Projects Only")
        self.active_projects_only_check_box.setChecked(True)
        self.active_projects_only_check_box.setToolTip("Show active Projects only!")
        self.active_projects_only_check_box.stateChanged.connect(partial(self.active_projects_only_check_box_callback))
        h_layout1.addWidget(self.active_projects_only_check_box)

        # h_layout1.setStretch(0, 1)
        # h_layout1.setStretch(1, 0)

        self.main_layout.addLayout(h_layout1)

        h_layout2 = QtWidgets.QHBoxLayout()

        stalker_seq_label = QtWidgets.QLabel(self.parent_widget)
        stalker_seq_label.setText('Stalker Seq:')
        stalker_seq_label.setFixedWidth(100)
        h_layout2.addWidget(stalker_seq_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        from anima.ui.widgets.sequence import SequenceComboBox
        # self.seq_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.seq_combo_box = SequenceComboBox(self.parent_widget)
        self.seq_combo_box.setSizePolicy(size_policy)
        self.seq_combo_box.currentIndexChanged.connect(partial(self.seq_combo_box_changed))
        h_layout2.addWidget(self.seq_combo_box)

        self.main_layout.addLayout(h_layout2)

        h_layout3 = QtWidgets.QHBoxLayout()

        stalker_scene_label = QtWidgets.QLabel(self.parent_widget)
        stalker_scene_label.setText('Stalker Scene:')
        stalker_scene_label.setFixedWidth(100)
        h_layout3.addWidget(stalker_scene_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.scene_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.scene_combo_box.setSizePolicy(size_policy)
        self.scene_combo_box.currentIndexChanged.connect(partial(self.scene_combo_box_changed))
        h_layout3.addWidget(self.scene_combo_box)

        self.main_layout.addLayout(h_layout3)

        h_layout_shots = QtWidgets.QHBoxLayout()

        shot_in_label = QtWidgets.QLabel(self.parent_widget)
        shot_in_label.setText('Shot In:')
        shot_in_label.setFixedWidth(50)
        h_layout_shots.addWidget(shot_in_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.shot_in_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.shot_in_combo_box.setSizePolicy(size_policy)
        self.shot_in_combo_box.currentIndexChanged.connect(partial(self.shot_in_combo_box_changed))
        h_layout_shots.addWidget(self.shot_in_combo_box)

        self.shot_out_label = QtWidgets.QLabel(self.parent_widget)
        self.shot_out_label.setText('Shot Out:')
        h_layout_shots.addWidget(self.shot_out_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.shot_out_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.shot_out_combo_box.setSizePolicy(size_policy)
        self.shot_out_combo_box.currentIndexChanged.connect(partial(self.shot_out_combo_box_changed))
        h_layout_shots.addWidget(self.shot_out_combo_box)

        self.main_layout.addLayout(h_layout_shots)

        h_layout4 = QtWidgets.QHBoxLayout()

        width_label = QtWidgets.QLabel(self.parent_widget)
        width_label.setText('Width:')
        width_label.setFixedWidth(50)
        h_layout4.addWidget(width_label)

        self.width_line = QtWidgets.QLineEdit(self.parent_widget)
        self.width_line.setText('-')
        self.width_line.setEnabled(0)
        h_layout4.addWidget(self.width_line)

        height_label = QtWidgets.QLabel(self.parent_widget)
        height_label.setText('Height:')
        height_label.setFixedWidth(50)
        h_layout4.addWidget(height_label)

        self.height_line = QtWidgets.QLineEdit(self.parent_widget)
        self.height_line.setText('-')
        self.height_line.setEnabled(0)
        h_layout4.addWidget(self.height_line)

        fps_label = QtWidgets.QLabel(self.parent_widget)
        fps_label.setText('Fps:')
        h_layout4.addWidget(fps_label)

        self.fps_line = QtWidgets.QLineEdit(self.parent_widget)
        self.fps_line.setText('-')
        self.fps_line.setEnabled(0)
        h_layout4.addWidget(self.fps_line)

        self.main_layout.addLayout(h_layout4)

        h_layout4a = QtWidgets.QHBoxLayout()

        self.filter_statuses_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.filter_statuses_check_box.setText('Filter Statuses')
        self.filter_statuses_check_box.stateChanged.connect(partial(self.filter_statuses_check_box_changed))
        h_layout4a.addWidget(self.filter_statuses_check_box)

        self.wip_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.wip_check_box.setText('WIP')
        h_layout4a.addWidget(self.wip_check_box)

        self.hrev_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.hrev_check_box.setText('HREV')
        h_layout4a.addWidget(self.hrev_check_box)

        self.prev_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.prev_check_box.setText('PREV')
        h_layout4a.addWidget(self.prev_check_box)

        self.completed_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.completed_check_box.setText('CMLT')
        h_layout4a.addWidget(self.completed_check_box)

        self.main_layout.addLayout(h_layout4a)

        h_layout4b = QtWidgets.QHBoxLayout()

        self.filter_user_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.filter_user_check_box.setText('+ Filter User')
        self.filter_user_check_box.stateChanged.connect(partial(self.filter_user_check_box_changed))
        h_layout4b.addWidget(self.filter_user_check_box)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.user_name_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.user_name_combo_box.setSizePolicy(size_policy)
        h_layout4b.addWidget(self.user_name_combo_box)

        self.main_layout.addLayout(h_layout4b)

        h_layout4c = QtWidgets.QHBoxLayout()

        self.just_import_as_media_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.just_import_as_media_check_box.setText('Just Import to Media Library')
        self.just_import_as_media_check_box.stateChanged.connect(partial(self.just_import_as_media_check_box_changed))
        h_layout4c.addWidget(self.just_import_as_media_check_box)

        self.keep_ext_in_clip_names_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.keep_ext_in_clip_names_check_box.setText('Keep Extension in Clip Names')
        h_layout4c.addWidget(self.keep_ext_in_clip_names_check_box)

        self.no_cleanups_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.no_cleanups_check_box.setText('No Cleanups')
        h_layout4c.addWidget(self.no_cleanups_check_box)

        self.main_layout.addLayout(h_layout4c)

        h_layout5 = QtWidgets.QHBoxLayout()

        task_name_label = QtWidgets.QLabel(self.parent_widget)
        task_name_label.setText('Task Name:')
        h_layout5.addWidget(task_name_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.task_name_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.task_name_combo_box.setSizePolicy(size_policy)
        self.task_name_combo_box.currentIndexChanged.connect(partial(self.task_name_combo_box_changed))
        h_layout5.addWidget(self.task_name_combo_box)

        ext_name_label = QtWidgets.QLabel(self.parent_widget)
        ext_name_label.setText('Extension:')
        h_layout5.addWidget(ext_name_label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.ext_name_combo_box = QtWidgets.QComboBox(self.parent_widget)
        self.ext_name_combo_box.setSizePolicy(size_policy)
        self.ext_name_combo_box.currentIndexChanged.connect(partial(self.ext_name_combo_box_changed))
        h_layout5.addWidget(self.ext_name_combo_box)

        self.plus_plates_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.plus_plates_check_box.setText('+ Plates')
        self.plus_plates_check_box.stateChanged.connect(partial(self.plus_plates_check_box_changed))
        h_layout5.addWidget(self.plus_plates_check_box)

        self.plus_refs_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.plus_refs_check_box.setText('+ References')
        self.plus_refs_check_box.stateChanged.connect(partial(self.plus_refs_check_box_changed))
        h_layout5.addWidget(self.plus_refs_check_box)

        self.main_layout.addLayout(h_layout5)

        h_layout6 = QtWidgets.QHBoxLayout()

        self.record_in_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.record_in_check_box.setText('Record In')
        self.record_in_check_box.stateChanged.connect(partial(self.record_in_check_box_changed))
        h_layout6.addWidget(self.record_in_check_box)

        self.slated_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.slated_check_box.setText('Include Slates')
        self.slated_check_box.stateChanged.connect(partial(self.slated_check_box_changed))
        h_layout6.addWidget(self.slated_check_box)

        self.use_current_timeline = QtWidgets.QCheckBox(self.parent_widget)
        self.use_current_timeline.setText('Use Current Timeline')
        h_layout6.addWidget(self.use_current_timeline)

        self.exclude_clips_in_sel_clips_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.exclude_clips_in_sel_clips_check_box.setText('Exclude Clips in Selected Bin')
        h_layout6.addWidget(self.exclude_clips_in_sel_clips_check_box)

        self.main_layout.addLayout(h_layout6)

        self.conform_button = QtWidgets.QPushButton(self.parent_widget)
        self.conform_button.setText('CONFORM ALL')
        self.conform_button.clicked.connect(partial(self.conform))
        self.main_layout.addWidget(self.conform_button)

        h_layout6a = QtWidgets.QHBoxLayout()

        self.sg_location_check_box = QtWidgets.QCheckBox(self.parent_widget)
        self.sg_location_check_box.setText('ShotGrid Check')
        self.sg_location_check_box.stateChanged.connect(partial(self.sg_location_check_box_changed))
        h_layout6a.addWidget(self.sg_location_check_box)

        self.location_line_edit = QtWidgets.QLineEdit(self.parent_widget)
        self.location_line_edit.setText('Copy Paste SG Folder Location here...')
        h_layout6a.addWidget(self.location_line_edit)

        self.sg_check_button = QtWidgets.QPushButton(self.parent_widget)
        self.sg_check_button.setText('<< Check Only')
        self.sg_check_button.clicked.connect(partial(self.sg_check))
        h_layout6a.addWidget(self.sg_check_button)

        self.main_layout.addLayout(h_layout6a)

        self.main_layout.addWidget(create_separator(self.parent_widget))

        h_layout6 = QtWidgets.QHBoxLayout()

        date_label = QtWidgets.QLabel(self.parent_widget)
        date_label.setText('check From:')
        date_label.setAlignment(QtCore.Qt.AlignCenter)
        h_layout6.addWidget(date_label)

        self.start_date = QtWidgets.QDateEdit(self.parent_widget)
        self.start_date.setDate(QtCore.QDate.currentDate())  # setDate(QtCore.QDate(2021, 1, 1))
        self.start_date.setCurrentSection(QtWidgets.QDateTimeEdit.MonthSection)
        self.start_date.setCalendarPopup(True)
        h_layout6.addWidget(self.start_date)

        now_label = QtWidgets.QLabel(self.parent_widget)
        now_label.setText(':until Now')
        now_label.setAlignment(QtCore.Qt.AlignCenter)
        h_layout6.addWidget(now_label)

        self.main_layout.addLayout(h_layout6)

        self.updated_shot_list = QtWidgets.QListWidget(self.parent_widget)
        self.updated_shot_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.main_layout.addWidget(self.updated_shot_list)

        self.status_button = QtWidgets.QPushButton(self.parent_widget)
        self.status_button.setText('LIST UPDATED SHOTS')
        self.status_button.clicked.connect(partial(self.list_shot_update_status))
        self.main_layout.addWidget(self.status_button)

        self.conform_updates_button = QtWidgets.QPushButton(self.parent_widget)
        self.conform_updates_button.setText('CONFORM UPDATED SHOTS ONLY')
        self.conform_updates_button.clicked.connect(partial(self.conform_updated_shots))
        self.main_layout.addWidget(self.conform_updates_button)

        self.main_layout.addWidget(create_separator(self.parent_widget))

        info_label = QtWidgets.QLabel(self.parent_widget)
        info_label.setText('check Console for Progress Info...')
        self.main_layout.addWidget(info_label)

    def _set_defaults(self):
        """sets defaults for UI
        """
        self.seq_combo_box.clear()
        self.seq_combo_box.setEnabled(0)

        self.scene_combo_box.clear()
        self.scene_combo_box.setEnabled(0)

        self.shot_in_combo_box.clear()
        self.shot_in_combo_box.setEnabled(0)

        self.shot_out_combo_box.clear()
        self.shot_out_combo_box.setEnabled(0)

        self.task_name_combo_box.addItem('Comp', -1)
        self.task_name_combo_box.addItem('Plate', 0)
        self.task_name_combo_box.addItem('Zero', 1)

        self.ext_name_combo_box.addItem('exr', -1)
        self.ext_name_combo_box.addItem('png', 0)
        self.ext_name_combo_box.addItem('tga', 1)
        self.ext_name_combo_box.addItem('mov', 2)
        self.ext_name_combo_box.addItem('mp4', 3)

        self.wip_check_box.setEnabled(0)
        self.hrev_check_box.setEnabled(0)
        self.prev_check_box.setChecked(1)
        self.prev_check_box.setEnabled(0)
        self.completed_check_box.setChecked(1)
        self.completed_check_box.setEnabled(0)

        self.location_line_edit.setEnabled(0)
        self.sg_check_button.setEnabled(0)

    def connect_to_resolve(self):
        """connects to resolve
        """
        from anima.env import blackmagic
        self.resolve = blackmagic.get_resolve()
        self.resolve_project = self.resolve.GetProjectManager().GetCurrentProject()

    def active_projects_only_check_box_callback(self, state):
        """
        :return:
        """
        self.project_combo_box.show_active_projects = state

    # TODO: seeing stalker ids in UI might be confusing... keep id data hidden
    def add_data_as_text_to_ui(self, name, task_id):
        """returns a predefined text to combo boxes for this UI
        """
        return '%s - [%s]' % (name, task_id)

    def get_id_from_data_text(self, text):
        """separates id from combo box texts added with add_data_as_text_to_ui() for this UI
        """
        task_id = None
        try:
            task_id = text.split(' - [')[1].strip(']')
        except IndexError:
            pass
        return task_id

    def project_combo_box_changed(self, *args):
        """runs when the project_combo_box is changed
        """
        self.updated_shot_list.clear()
        stalker_project = self.project_combo_box.get_current_project()
        self.seq_combo_box.project = stalker_project

        if not stalker_project:
            self.seq_combo_box.setEnabled(0)
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(0)
            self.shot_in_combo_box.clear()
            self.shot_in_combo_box.setEnabled(0)
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            self.seq_combo_box.setEnabled(1)
            self.seq_combo_box.insertItem(0, 'ALL', None)
            self.seq_combo_box.setCurrentIndex(0)

            self.fps_line.setText('%s' % stalker_project.fps)
            self.width_line.setText('%s' % stalker_project.image_format.width)
            self.height_line.setText('%s' % stalker_project.image_format.height)

    def seq_combo_box_changed(self, *args):
        """runs when the seq_combo_box is changed
        """
        self.updated_shot_list.clear()
        # fill scene_combo_box with scenes only if a sequence is selected

        stalker_seq = self.seq_combo_box.get_current_sequence()
        if not stalker_seq:
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(0)
            self.shot_in_combo_box.clear()
            self.shot_in_combo_box.setEnabled(0)
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            self.scene_combo_box.clear()
            self.scene_combo_box.setEnabled(1)
            self.scene_combo_box.addItem('ALL', None)
            # assume that scenes are 1st level children of sequences (default in Anima Pipeline Structure)
            from stalker import Task, Type
            scene_type = Type.query.filter(Type.name == 'Scene').first()
            all_scenes = Task.query \
                .filter(Task.parent == stalker_seq) \
                .filter(Task.type == scene_type) \
                .order_by(Task.name) \
                .all()
            for task in all_scenes:
                self.scene_combo_box.addItem(task.name, task)

    def scene_combo_box_changed(self, *args):
        """runs when the scene_combo_box is changed
        """
        self.updated_shot_list.clear()
        project = self.project_combo_box.get_current_project()

        if project:
            scene = self.scene_combo_box.itemData(self.scene_combo_box.currentIndex())
            if not scene:
                self.shot_in_combo_box.clear()
                self.shot_in_combo_box.setEnabled(0)
                self.shot_out_combo_box.clear()
                self.shot_out_combo_box.setEnabled(0)

                # Set properties from Project instance
                self.fps_line.setText('%s' % project.fps)
                self.width_line.setText('%s' % project.image_format.width)
                self.height_line.setText('%s' % project.image_format.height)
            else:
                from stalker import Task, Shot, Sequence
                # shots under different scenes might have various res, fps properties under same seq or project
                # set properties from first shot under Scene (assume all shots under scene have the same res,fps)
                for t in scene.walk_hierarchy():
                    if isinstance(t, Shot):
                        self.fps_line.setText('%s' % t.fps)
                        self.width_line.setText('%s' % t.image_format.width)
                        self.height_line.setText('%s' % t.image_format.height)
                        break

                # fill shot_in_combo_box with shots
                self.shot_in_combo_box.clear()
                self.shot_in_combo_box.setEnabled(1)
                self.shot_in_combo_box.addItem('ALL', None)

                seq = self.seq_combo_box.get_current_sequence()
                shots = Shot.query.filter(Shot.sequences.contains(seq)).order_by(Shot.name).all()
                for shot in shots:
                    if scene in shot.parents:
                        self.shot_in_combo_box.addItem(shot.name, shot)

    def shot_in_combo_box_changed(self, *args):
        """runs when the shot_in_combo_box is changed
        """
        # fills shot_out_combo_box with shots
        self.updated_shot_list.clear()
        shot_in = self.shot_in_combo_box.itemData(self.shot_in_combo_box.currentIndex())
        if not shot_in:
            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(0)
        else:
            shot_in_num = int(shot_in.name.split('_')[-1])
            seq = self.seq_combo_box.itemData(self.seq_combo_box.currentIndex())
            scene = self.scene_combo_box.itemData(self.scene_combo_box.currentIndex())

            self.shot_out_combo_box.clear()
            self.shot_out_combo_box.setEnabled(1)
            from stalker import Shot
            shots = Shot.query.filter(Shot.sequences.contains(seq)).order_by(Shot.name).all()
            for shot in shots:
                if scene in shot.parents and int(shot.name.split('_')[-1]) >= shot_in_num:
                    self.shot_out_combo_box.addItem(shot.name, shot)

    def shot_out_combo_box_changed(self, *args):
        """runs when the shot_out_combo_box is changed
        """
        self.updated_shot_list.clear()

    def task_name_combo_box_changed(self, *args):
        """runs when the task_name_combo_box is changed
        """
        task_in_text = self.task_name_combo_box.currentText()
        if task_in_text == 'Comp':
            self.plus_refs_check_box.setChecked(0)
            self.plus_refs_check_box.setEnabled(1)
            self.plus_plates_check_box.setChecked(0)
            self.plus_plates_check_box.setEnabled(1)
        else:
            self.plus_refs_check_box.setChecked(0)
            self.plus_refs_check_box.setEnabled(0)
            self.plus_plates_check_box.setChecked(0)
            self.plus_plates_check_box.setEnabled(0)

    def ext_name_combo_box_changed(self, *args):
        """runs when the ext_name_combo_box is changed
        """
        ext_in_text = self.ext_name_combo_box.currentText()
        if ext_in_text == 'mov' or ext_in_text == 'mp4':
            self.plus_refs_check_box.setChecked(0)
            self.plus_refs_check_box.setEnabled(1)
        else:
            self.plus_refs_check_box.setChecked(0)
            self.plus_refs_check_box.setEnabled(0)

    def filter_statuses_check_box_changed(self, state):
        """runs when the filter_status_check_box is changed
        """
        if state == 0:
            self.wip_check_box.setEnabled(0)
            self.hrev_check_box.setEnabled(0)
            self.prev_check_box.setEnabled(0)
            self.completed_check_box.setEnabled(0)
        else:
            self.wip_check_box.setEnabled(1)
            self.hrev_check_box.setEnabled(1)
            self.prev_check_box.setEnabled(1)
            self.completed_check_box.setEnabled(1)

    def filter_user_check_box_changed(self, state):
        """runs when the filter_user_check_box is changed
        """
        if state == 0:
            self.user_name_combo_box.clear()
            self.user_name_combo_box.setEnabled(0)
        else:
            self.user_name_combo_box.clear()
            stalker_project = self.project_combo_box.get_current_project()
            if not stalker_project:
                self.filter_user_check_box.click()
                QtWidgets.QMessageBox.critical(
                    self.parent_widget,
                    'Error',
                    'Please Select a Stalker Project.'
                )
                return
            for user in stalker_project.users:
                self.user_name_combo_box.addItem(user.name, user)
            self.user_name_combo_box.setEnabled(1)

    def just_import_as_media_check_box_changed(self, state):
        """runs when the just_import_as_media_check_box is changed
        """
        if state == 0:
            self.record_in_check_box.setEnabled(1)
            self.slated_check_box.setEnabled(1)
            self.use_current_timeline.setEnabled(1)
            self.keep_ext_in_clip_names_check_box.setChecked(0)
            self.keep_ext_in_clip_names_check_box.setEnabled(1)
        else:
            self.record_in_check_box.setEnabled(0)
            self.slated_check_box.setEnabled(0)
            self.use_current_timeline.setEnabled(0)
            self.keep_ext_in_clip_names_check_box.setChecked(1)
            self.keep_ext_in_clip_names_check_box.setEnabled(0)

    def plus_plates_check_box_changed(self, state):
        """runs when the plus_plates_check_box is changed
        """
        if state != 0:
            self.slated_check_box.setChecked(0)
            self.slated_check_box.setEnabled(0)
            self.use_current_timeline.setChecked(0)
            self.use_current_timeline.setEnabled(0)
            # self.ext_name_combo_box.setCurrentIndex(0)
            # self.ext_name_combo_box.setEnabled(0)
        else:
            if not self.plus_refs_check_box.isChecked():
                self.slated_check_box.setEnabled(1)
                self.use_current_timeline.setEnabled(1)
                self.ext_name_combo_box.setEnabled(1)

    def plus_refs_check_box_changed(self, state):
        """runs when the plus_refs_check_box is changed
        """
        if state != 0:
            self.slated_check_box.setChecked(0)
            self.slated_check_box.setEnabled(0)
            self.use_current_timeline.setChecked(0)
            self.use_current_timeline.setEnabled(0)
            # self.ext_name_combo_box.setCurrentIndex(0)
            # self.ext_name_combo_box.setEnabled(0)
        else:
            if not self.plus_plates_check_box.isChecked():
                self.slated_check_box.setEnabled(1)
                self.use_current_timeline.setEnabled(1)
                self.ext_name_combo_box.setEnabled(1)

    def slated_check_box_changed(self, state):
        """runs when the slated_check_box is changed
        """
        if state != 0:
            self.record_in_check_box.setChecked(0)
            self.record_in_check_box.setEnabled(0)
        else:
            self.record_in_check_box.setEnabled(1)

    def record_in_check_box_changed(self, state):
        """runs when the slated_check_box is changed
        """
        if state != 0:
            self.slated_check_box.setChecked(0)
            self.slated_check_box.setEnabled(0)
        else:
            self.slated_check_box.setEnabled(1)

    def sg_location_check_box_changed(self, state):
        """runs when the sg_location_check_box is changed
        """
        if state != 0:
            self.location_line_edit.setEnabled(1)
            self.sg_check_button.setEnabled(1)
        else:
            self.location_line_edit.setEnabled(0)
            self.sg_check_button.setEnabled(0)

    def validate_shot_name(self, file_name):
        """validates given name within stalker standard shot instance naming convention
        :param clip_name:
        :return: str
        """
        import os
        import re

        shot_name = None
        parts = file_name.split("_")

        if len(parts) >= 4:
            project_code_regex = re.compile("[A-Z]+")
            episode_code_regex = re.compile("[A-Z0-9]+")
            scene_code_regex = re.compile("[A-Z0-9]+")
            shot_code_regex = re.compile("[0-9]+")
            project_code, episode_code, scene_code, shot_code = parts[0:4]

            if re.match(project_code_regex, project_code) \
                    and re.match(episode_code_regex, episode_code) \
                    and re.match(scene_code_regex, scene_code) \
                    and re.match(shot_code_regex, shot_code):
                shot_name = "_".join(parts[0:4])

        return shot_name

    def get_sg_data(self, sg_dir):
        """queries file paths of .mov files from specified root folder if validated
        :param str sg_dir: root directory path
        :return: list of file paths
        """
        import os

        sg_data = []
        if os.path.isdir(sg_dir):
            for root, dirs, files in os.walk(sg_dir):
                for f in files:
                    base_name = os.path.basename(os.path.splitext(f)[0])
                    if f.endswith('.mov') and self.validate_shot_name(base_name):
                        sg_path = os.path.normpath(os.path.join(root, f))
                        sg_info = [os.path.basename(sg_path).split('.')[0], sg_path] #  [nice_name_version, abs_path]
                        sg_data.append(sg_info)
        else:
            raise RuntimeError('No Such Directory! -> %s' % sg_dir)

        return sg_data

    def sg_check(self):
        """prints a report to console for files uploaded to shotgrid from specified folder
        """
        import os
        import re

        sg_dir = self.location_line_edit.text()
        sg_data = self.get_sg_data(sg_dir)

        if sg_data:
            print('============== SHOT GRID CHECK ===============')
            for sg_info in sg_data:
                print('%s -> %s' % (sg_info[0], sg_info[1]))
            print('==============================================')
        else:
            print('No SG Data found!')

    def get_shots_from_ui(self):
        """returns Stalker Shot instances as a list based on selection from UI
        """
        # return if a project is not selected from ui
        stalker_project = self.project_combo_box.get_current_project()
        if not stalker_project:
            QtWidgets.QMessageBox.critical(
                self.parent_widget,
                'Error',
                'Please Select a Stalker Project.'
            )
            return

        shots = []

        if self.seq_combo_box.currentText() == 'ALL':
            for sequence in stalker_project.sequences:
                shots += sequence.shots
        else:
            stalker_seq = self.seq_combo_box.get_current_sequence()
            if self.scene_combo_box.currentText() == 'ALL':
                shots += stalker_seq.shots
            else:
                stalker_scene = self.scene_combo_box.itemData(self.scene_combo_box.currentIndex())
                if self.shot_in_combo_box.currentText() == 'ALL':
                    for shot in stalker_seq.shots:
                        if stalker_scene in shot.parents:  # assume that a shot is always a parent of it's scene
                            shots.append(shot)
                else:
                    shot_in = self.shot_in_combo_box.itemData(self.shot_in_combo_box.currentIndex())
                    shot_out = self.shot_out_combo_box.itemData(self.shot_out_combo_box.currentIndex())
                    if shot_in and shot_out:
                        shot_in_num = int(shot_in.name.split('_')[-1])
                        shot_out_num = int(shot_out.name.split('_')[-1])
                        for shot in stalker_seq.shots:
                            shot_num = int(shot.name.split('_')[-1])
                            if stalker_scene in shot.parents \
                                    and shot_in_num <= shot_num <= shot_out_num \
                                    and shot not in shots:
                                shots.append(shot)

        if self.filter_user_check_box.isChecked():
            from stalker import User

            user_shots = []
            user_text = self.user_name_combo_box.currentText()
            user = User.query.filter_by(name=user_text).first()
            for shot in shots:
                for t in shot.children:
                    if t.is_leaf and user in t.resources and shot not in user_shots:
                        user_shots.append(shot)
                        break

            if user_shots:
                shots = user_shots

        if not shots:
            QtWidgets.QMessageBox.critical(
                self.parent_widget,
                'Error',
                'No Valid Shots found!.'
            )

        return shots

    def get_valid_statuses_from_ui(self):
        """returns valid statuses from ui
        """
        valid_status_names = []

        if self.wip_check_box.isChecked():
            valid_status_names.append('Work In Progress')
        if self.hrev_check_box.isChecked():
            valid_status_names.append('Has Revision')
        if self.prev_check_box.isChecked():
            valid_status_names.append('Pending Review')
        if self.completed_check_box.isChecked():
            valid_status_names.append('Completed')

        return valid_status_names

    def get_latest_output_path(self, shot, task_name, ext='exr', return_raw_values=False):
        """returns the Output/Main outputs path for resolve from a given Shot stalker instance
        """
        import os
        import glob
        import re
        from anima.env import base
        from stalker import Task, Version

        if task_name == 'Reference':
            ref_path = '%s/References/%s.%s' % (shot.absolute_path, shot.name, ext)
            if os.path.exists(ref_path):
                return ref_path
            else:
                return None

        task = Task.query.filter(Task.parent == shot).filter(Task.name == task_name).first()
        if not task and task_name == 'Comp':  # try Cleanup task
            task = Task.query.filter(Task.parent == shot).filter(Task.name == 'Cleanup').first()
        if not task:
            return None

        if self.filter_statuses_check_box.isChecked():
            if task_name not in ['Plate', 'Reference']:  # do not check status for plates, references
                valid_status_names = self.get_valid_statuses_from_ui()
                if task.status.name not in valid_status_names:
                    return None
                else:
                    print('%s -> %s -> %s' % (shot.name, task.name, task.status.name))

        task_path = task.absolute_path
        output_path = os.path.join(task_path, 'Outputs', 'Main')

        resolve_path = None
        resolve_raw_path = None
        start_frame = None
        end_frame = None
        file_paths = None

        latest_task_name = None
        latest_version_name = None
        found_version_name = None

        latest_version = None
        try:
            latest_version = Version.query.filter(Version.task == task).filter(Version.take_name == 'Main') \
                .order_by(Version.version_number.desc())[0]
        except IndexError:
            pass

        file_paths = None

        def get_file_paths(op, ext, ltn):  # output_path, ext, latest_task_name
            import glob

            paths = glob.glob("%s/*/%s/*%s.*.%s" % (op, ext, ltn, ext))
            if not paths:  # try outputs with no version folders
                paths = glob.glob("%s/%s/*%s.*.%s" % (op, ext, ltn, ext))
            if not paths:  # try video files (mov, mp4)
                paths = glob.glob("%s/*/%s/*%s.%s" % (op, ext, ltn, ext))

            return paths

        if latest_version:
            latest_version_name = base.EnvironmentBase.get_significant_name(latest_version,
                                                                            include_project_code=False)
            latest_v = True
            for latest_task_version in Version.query.filter(Version.task == task).filter(Version.take_name == 'Main') \
                    .order_by(Version.version_number.desc()):
                latest_task_name = base.EnvironmentBase.get_significant_name(latest_task_version,
                                                                             include_project_code=False)

                file_paths = get_file_paths(op=output_path, ext=ext, ltn=latest_task_name)

                if file_paths:
                    if latest_v is False:
                        found_version_name = latest_task_name
                    break
                latest_v = False
        else: # try to get latest version paths manually for projects that use unsupported software
            v_nice_name = '%s_%s_Main' % (shot.name, task.name)
            all_paths = glob.glob("%s/*/%s/*" % (output_path, ext))

            base_names = []
            versions = []
            for path in all_paths:
                base_name = os.path.basename(path).split('.')[0]
                if base_name not in base_names \
                        and base_name.startswith(v_nice_name) \
                        and base_name.split('_')[-1][0] == 'v' \
                        and base_name.split('_')[-1][-1:].isdigit():
                    base_names.append(base_name)
            for base_name in base_names:
                try:
                    version_str = base_name.split('_')[-1]
                    versions.append(int(version_str[-1:]))
                except (ValueError, IndexError):
                    pass

            if versions:
                latest_task_name = '%s_v%s' % (v_nice_name, str(max(versions)).rjust(3, '0'))
                file_paths = get_file_paths(op=output_path, ext=ext, ltn=latest_task_name)

        if latest_version_name and found_version_name:
            print("%s NOT FOUND! -> %s 's output will be used." % (latest_version_name, found_version_name))

        # try to find path manually for plate tasks as they might not have default naming conventions or versions
        if not resolve_path and task_name == 'Plate':
            version_numbers = []
            main_dir = os.path.join(shot.absolute_path, 'Plate', 'Outputs', 'Main')
            if os.path.isdir(main_dir):
                dir_names = glob.glob('%s/*' % main_dir)
                for dir_name in dir_names:
                    if os.path.isdir(dir_name) and os.path.basename(dir_name)[0] == 'v' \
                            and os.path.basename(dir_name)[1:].isdigit() and len(os.path.basename(dir_name)) == 4:
                        version_numbers.append(int(os.path.basename(dir_name)[1:]))
            if version_numbers:
                latest_version_number = max(version_numbers)
                latest_version_folder_name = 'v%s' % str(latest_version_number).rjust(3, '0')
                plate_path = os.path.join(main_dir, latest_version_folder_name, ext)
                plate_path = os.path.normpath(plate_path).replace('\\', '/')

                file_paths = glob.glob('%s/*.%s' % (plate_path, ext))

        if file_paths:
            regex = r'\d+$|#+$'
            dir_base = file_paths[0].split('.')[0]
            frames = []
            pads = []
            for f in file_paths:
                pad = re.findall(regex, os.path.splitext(f)[0])[0]
                if len(pad) not in pads:  # handle padding mismatch
                    pads.append(len(pad))
                frame = int(pad)
                frames.append(frame)
            start = str(min(frames)).rjust(min(pads), '0')
            end = str(max(frames)).rjust(max(pads), '0')
            resolve_path = '%s.[%s-%s].%s' % (dir_base, start, end, ext)
            resolve_raw_path = '%s.%s.%s' % (dir_base, '%0{digits}d'.format(digits=len(start)), ext)
            if ext in ['mov', 'mp4']:
                first_dir_base = os.path.splitext(file_paths[0])[0]
                last_dir_base = os.path.splitext(file_paths[-1])[0]
                if len(first_dir_base.split('.')) > 1:
                    resolve_path = '%s.%s.%s' % (dir_base, str(re.findall(regex, last_dir_base)[0]), ext)
                    resolve_raw_path = '%s.%s.%s' % (dir_base, str(re.findall(regex, last_dir_base)[0]), ext)
                else:
                    resolve_path = '%s.%s' % (dir_base, ext)
                    resolve_raw_path = '%s.%s' % (dir_base, ext)
            resolve_path = os.path.normpath(resolve_path).replace('\\', '/')
            start_frame = int(start)
            end_frame = int(end)

        if return_raw_values:
            return [resolve_raw_path, start_frame, end_frame]
        else:
            return resolve_path

    def create_resolve_timeline_from_clips(self, timeline_name, clip_paths):
        """creates timeline in resolve from given clip paths
        """
        print('---------Started creating Timeline----------')
        media_pool = self.resolve_project.GetMediaPool()
        media_storage = self.resolve.GetMediaStorage()

        clips = media_storage.AddItemListToMediaPool(clip_paths)
        media_pool.CreateTimelineFromClips(timeline_name, clips)
        print('---------Finished creating Timeline----------')

    # TODO: getting timecode from image must be done with proper exif library that supports any platform
    def get_timecode_from_image(self, fps, img_path):
        """queries timecode metadata from given image
        """
        import os
        import subprocess
        import timecode

        frame_number = 0

        info = {}
        process = subprocess.Popen(['exiftool', img_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   universal_newlines=True)

        for tag in process.stdout:
            line = tag.strip().split(':')
            info[line[0].strip()] = line[-1].strip()

        try:
            tc_exif = info['Time Code'].split(' ')[0]
            t = timecode.Timecode('%s' % fps, start_timecode=int(tc_exif))
            frame_number = t.frame_number
        except BaseException:
            pass

        print('[%s] frame number returned from [%s]' % (frame_number, os.path.basename(img_path)))

        return frame_number

    # TODO: XML creation must be done better with Anima pipeline's xml class
    def clip_paths_to_xml(self, clip_path_list, record_in_list, xml_file_full_path):
        """creates fcpxml1.8 compatible xml file from given Resolve image sequence paths
        """
        import math
        import os
        timeline_name = self.generate_timeline_name()
        extension = self.ext_name_combo_box.currentText()
        fps = self.fps_line.text()
        # for some reason fcpxml does not like float fps like 24.0
        # if the decimal is .0 than fps must be integer 24 so...
        if float(fps) / math.trunc(float(fps)) == 1.0:
            fps = '%s' % math.trunc(float(fps))

        with open(xml_file_full_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE fcpxml>\n')
            f.write('<fcpxml version="1.8">\n')
            f.write('    <resources>\n')
            f.write('        <format '
                    'id="r0" '
                    'frameDuration="1/%ss"/>\n' % fps)
            ind = 0
            seq_frames = 0
            tc_frame_numbers = []
            rc_ins = []
            for clip_path in clip_path_list:
                ind += 1
                first_frame = int(clip_path.split('.')[-2].split('-')[0].strip('['))
                last_frame = int(clip_path.split('.')[-2].split('-')[1].strip(']'))
                total_frames = (last_frame - first_frame) + 1
                seq_frames += total_frames
                str_first_frame = clip_path.split('.')[-2].split('-')[0].strip('[')
                first_image_path = '%s.%s.%s' % ('.'.join(clip_path.split('.')[:-2]), str_first_frame, extension)

                rc_in = None
                if self.record_in_check_box.isChecked():
                    for record_in_data in record_in_list:
                        if record_in_data[0] == clip_path:
                            rc_in = record_in_data[1]
                            break
                    rc_ins.append(rc_in)

                st = self.get_timecode_from_image(fps, first_image_path)
                tc_frame_numbers.append(st)

                f.write('        <asset src="file://localhost/%s" '
                        'duration="%s/%ss" '
                        'hasVideo="1" '
                        'id="r%s" '
                        'format="r0" '
                        'name="%s" '
                        'start="%s/%ss"/>\n' % (clip_path, str(total_frames), fps, str(ind),
                                                os.path.basename(clip_path), str(st), fps))
            f.write('    </resources>\n')
            f.write('    <library>\n')
            f.write('        <event name="%s">\n' % timeline_name)
            f.write('            <project name="%s">\n' % timeline_name)
            f.write('                <sequence duration="%s/%ss" tcFormat="NDF" '
                    'format="r0" tcStart="0/1s">\n' % (str(seq_frames), fps))
            f.write('                    <spine>\n')
            ind = 0
            offset_frame = 0
            for clip_path in clip_path_list:
                ind += 1
                first_frame = int(clip_path.split('.')[-2].split('-')[0].strip('['))
                last_frame = int(clip_path.split('.')[-2].split('-')[1].strip(']'))
                total_frames = (last_frame - first_frame) + 1
                if self.record_in_check_box.isChecked():
                    offset_frame = rc_ins[ind - 1]
                st = tc_frame_numbers[ind - 1]
                if self.slated_check_box.isChecked():
                    if not self.record_in_check_box.isChecked():
                        f.write('                        <asset-clip offset="%s/%ss" duration="%s/%ss" '
                                'tcFormat="NDF" enabled="1" format="r0" ref="r%s" '
                                'name="%s" start="%s/%ss">\n' % (str(offset_frame), fps, '1', fps,
                                                                 str(ind), os.path.basename(clip_path), str(st), fps))
                        f.write('                            <adjust-transform position="0 0" '
                                'anchor="0 0" scale="1 1"/>\n')
                        f.write('                        </asset-clip>\n')
                        offset_frame += 1
                    else:
                        slate_frame = offset_frame - 1
                        f.write('                        <asset-clip offset="%s/%ss" duration="%s/%ss" '
                                'tcFormat="NDF" enabled="1" format="r0" ref="r%s" '
                                'name="%s" start="%s/%ss">\n' % (str(slate_frame), fps, '1', fps,
                                                                 str(ind), os.path.basename(clip_path), str(st), fps))
                        f.write('                            <adjust-transform position="0 0" '
                                'anchor="0 0" scale="1 1"/>\n')
                        f.write('                        </asset-clip>\n')
                f.write('                        <asset-clip offset="%s/%ss" duration="%s/%ss" '
                        'tcFormat="NDF" enabled="1" format="r0" ref="r%s" '
                        'name="%s" start="%s/%ss">\n' % (str(offset_frame), fps, str(total_frames), fps,
                                                         str(ind), os.path.basename(clip_path), str(st), fps))
                f.write('                            <adjust-transform position="0 0" '
                        'anchor="0 0" scale="1 1"/>\n')
                f.write('                        </asset-clip>\n')
                if not self.record_in_check_box.isChecked():
                    offset_frame += total_frames
            f.write('                    </spine>\n')
            f.write('                </sequence>\n')
            f.write('            </project>\n')
            f.write('        </event>\n')
            f.write('    </library>\n')
            f.write('</fcpxml>')

    def generate_timeline_name(self):
        """Generates a timeline name according to the UI input
        """
        import datetime
        today = datetime.datetime.today()
        now = '%s%s%s_%s%s%s' % (today.year,
                                 str(today.month).rjust(2, '0'),
                                 str(today.day).rjust(2, '0'),
                                 str(today.hour).rjust(2, '0'),
                                 str(today.minute).rjust(2, '0'),
                                 str(today.second).rjust(2, '0'))
        proj_name = self.project_combo_box.currentText()
        seq_name = self.seq_combo_box.currentText()
        scn_name = self.scene_combo_box.currentText()
        timeline_name = '%s_%s_%s_%s' % (proj_name, seq_name, scn_name, now)
        return timeline_name

    def conform_shots(self, shots):
        """conforms given Stalker Shot instances from UI to a Timeline for Resolve
        """
        if shots:
            t_name = self.task_name_combo_box.currentText()
            extension = self.ext_name_combo_box.currentText()
            record_in_list = []
            clip_path_list = []
            plate_path_list = []
            plate_not_found_list = []
            plate_range_mismatch_list = []
            ref_path_list = []
            ref_not_found_list = []
            none_path_list = []
            for shot in shots:
                print('Checking Shot... - %s' % shot.name)

                clip_path = self.get_latest_output_path(shot, t_name, ext=extension)
                if t_name == 'Comp' and clip_path is None \
                        and not self.no_cleanups_check_box.isChecked():  # look for Cleanup task
                    clip_path = self.get_latest_output_path(shot, 'Cleanup', ext=extension)

                if clip_path:
                    clip_path_list.append(clip_path)
                elif clip_path is None:
                    none_path_list.append('%s -> No Outputs/Main found.' % shot.name)

                if t_name == 'Comp' and clip_path and self.plus_plates_check_box.isChecked():
                    plate_path = self.get_latest_output_path(shot, 'Plate', ext=extension)
                    if plate_path:
                        plate_path_list.append(plate_path)
                    elif clip_path:  # add comp or cleanup clip to match timelines
                        plate_path_list.append(clip_path)
                        plate_not_found_list.append(clip_path)

                if t_name == 'Comp' and clip_path and self.plus_refs_check_box.isChecked():
                    ref_path = self.get_latest_output_path(shot, 'Reference', ext=extension)
                    if ref_path:
                        ref_path_list.append(ref_path)
                    elif clip_path:  # add comp or cleanup clip to match timelines
                        ref_path_list.append(clip_path)
                        ref_not_found_list.append(clip_path)

                if self.record_in_check_box.isChecked():
                    rc_in = shot.record_in
                    if not rc_in:
                        raise RuntimeError('%s -> No record in data! Turn off Record In check box.' % shot.name)
                    record_in_list.append([clip_path, rc_in])

            clip_path_list.sort()
            record_in_list.sort()
            none_path_list.sort()
            plate_path_list.sort()
            plate_not_found_list.sort()
            plate_range_mismatch_list.sort()
            ref_path_list.sort()
            ref_not_found_list.sort()

            if plate_path_list and self.plus_plates_check_box.isChecked():
                if len(clip_path_list) != len(plate_path_list):
                    print('--------------------------------------------------------------------------')
                    print('ERROR: Comp / Plate mismatch! Contact Supervisor.')
                    print('--------------------------------------------------------------------------')
                    raise RuntimeError('Comp / Plate mismatch! Contact Supervisor.')

                for i in range(0, len(clip_path_list)):
                    try:
                        import os
                        clip_range = os.path.basename(clip_path_list[i]).split('.')[1]
                        plate_range = os.path.basename(plate_path_list[i]).split('.')[1]
                        print('Clip: %s -> Plate: %s' % (clip_range, plate_range))
                        if clip_range != plate_range:
                            plate_range_mismatch_list.append(clip_path_list[i])
                    except IndexError:
                        pass

            if ref_path_list and self.plus_ref_check_box.isChecked():
                if len(clip_path_list) != len(ref_path_list):
                    print('--------------------------------------------------------------------------')
                    print('ERROR: Comp / Reference mismatch! Contact Supervisor.')
                    print('--------------------------------------------------------------------------')
                    raise RuntimeError('Comp / Reference mismatch! Contact Supervisor.')

            print('--------------------------------------------------------------------------')
            for i in range(0, len(clip_path_list)):
                if plate_path_list and self.plus_plates_check_box.isChecked():
                    print('%s  +  %s' % (clip_path_list[i], plate_path_list[i]))
                elif ref_path_list and self.plus_ref_check_box.isChecked():
                    print('%s  +  %s' % (clip_path_list[i], ref_path_list[i]))
                else:
                    print(clip_path_list[i])
            print('--------------------------------------------------------------------------')
            if none_path_list:
                for none_path in none_path_list:
                    print(none_path)
                print('--------------------------------------------------------------------------')
            if plate_not_found_list:
                print('--------------------------PLATES NOT FOUND--------------------------------')
                for p_path in plate_not_found_list:
                    print(p_path)
                print('--------------------------------------------------------------------------')
            if plate_range_mismatch_list:
                print('-----------------------PLATES RANGE MISMATCH------------------------------')
                for p_path in plate_range_mismatch_list:
                    print(p_path)
                print('--------------------------------------------------------------------------')
            if ref_not_found_list:
                print('--------------------------REFS NOT FOUND--------------------------------')
                for p_path in ref_not_found_list:
                    print(p_path)
                print('--------------------------------------------------------------------------')

            if clip_path_list:
                self.clip_paths_to_xml(clip_path_list, record_in_list, self.xml_path)
                print('XML CREATED----------------------------')

                self.connect_to_resolve()
                media_pool = self.resolve_project.GetMediaPool()
                media_pool.ImportTimelineFromFile(self.xml_path)
                print("Importing XML to Timeline!")
                print('XML IMPORTED to Resolve')
                if plate_path_list and self.plus_plates_check_box.isChecked():
                    print('CREATING + PLATES XML... Please Wait... ----------------------------')
                    self.clip_paths_to_xml(plate_path_list, record_in_list, self.xml_path)
                    print('+ PLATES XML CREATED----------------------------')
                    media_pool = self.resolve_project.GetMediaPool()
                    media_pool.ImportTimelineFromFile(self.xml_path)
                    print('+ PLATES XML IMPORTED to Resolve')
                if ref_path_list and self.plus_ref_check_box.isChecked():
                    print('CREATING + REFS XML... Please Wait... ----------------------------')
                    self.clip_paths_to_xml(ref_path_list, record_in_list, self.xml_path)
                    print('+ REFS XML CREATED----------------------------')
                    media_pool = self.resolve_project.GetMediaPool()
                    media_pool.ImportTimelineFromFile(self.xml_path)
                    print('+ REFS XML IMPORTED to Resolve')
                # Fix shot clip names
                if not self.keep_ext_in_clip_names_check_box.isChecked():
                    from anima.env.resolve.shot_tools import ShotManager
                    sm = ShotManager()
                    sm.fix_shot_clip_names()

            else:
                print('No Outputs found with given specs!')

            # self.create_resolve_timeline_from_clips(timeline_name, clip_path_list)

    def conform_shots_new(self, shots, include_slates=False, use_current_timeline=False, sg_check=False):
        """conforms given Stalker Shot instances from UI to a Timeline for Resolve
        """
        if shots:
            t_name = self.task_name_combo_box.currentText()
            extension = self.ext_name_combo_box.currentText()
            record_in_list = []
            clip_path_list = []
            plate_path_list = []
            plate_not_found_list = []
            plate_range_mismatch_list = []
            ref_path_list = []
            ref_not_found_list = []
            none_path_list = []
            for shot in shots:
                clip_info = None
                start_index = None
                end_index = None

                print('Checking Shot... - %s' % shot.name)

                result = self.get_latest_output_path(
                    shot, t_name, ext=extension, return_raw_values=True
                )

                status = None
                if result:
                    clip_info = result[0]
                    start_index = result[1]
                    end_index = result[2]
                    # add status to result for colorizing clips based on status
                    if self.filter_statuses_check_box.isChecked():
                        for task in shot.children:
                            if task.name == t_name:
                                status = task.status.name
                                break
                    result.append(status)
                if t_name == 'Comp' and clip_info is None \
                        and not self.no_cleanups_check_box.isChecked():  # look for Cleanup task
                    result = self.get_latest_output_path(
                        shot, 'Cleanup', ext=extension, return_raw_values=True
                    )
                    print('clean: %s' % str(result))
                    if result:
                        clip_info = result[0]
                        start_index = result[1]
                        end_index = result[2]
                        # add status to result for colorizing clips based on status
                        if self.filter_statuses_check_box.isChecked():
                            for task in shot.children:
                                if task.name == 'Cleanup':
                                    status = task.status.name
                                    break
                        result.append(status)

                if clip_info and result not in clip_path_list:
                    clip_path_list.append(result)
                elif clip_info is None:
                    st = 'NULL'
                    rs = 'NULL'
                    if shot:
                        for task in shot.children:
                            if task.name == t_name:
                                try:
                                    st = task.status.name
                                    rs = task.resources[0].name
                                    break
                                except IndexError:
                                    pass
                    none_path_list.append('%s -> No Outputs/Main found. - [%s] - %s' % (shot.name, st, rs))

                if t_name == 'Comp' and clip_info and self.plus_plates_check_box.isChecked():
                    plate_path, p_start_frame, p_end_frame = self.get_latest_output_path(
                        shot, 'Plate', ext=extension, return_raw_values=True
                    )
                    if plate_path:
                        if [plate_path, p_start_frame, p_end_frame] not in plate_path_list:
                            plate_path_list.append([plate_path, p_start_frame, p_end_frame])
                    elif clip_info:  # add comp or cleanup clip to match timelines
                        if [clip_info, start_index, end_index] not in plate_path_list:
                            plate_path_list.append([clip_info, start_index, end_index])
                            if clip_info not in plate_not_found_list:
                                plate_not_found_list.append(clip_info)

                if t_name == 'Comp' and clip_info and self.plus_refs_check_box.isChecked():
                    ref_path = self.get_latest_output_path(shot, 'Reference', ext=extension)
                    if ref_path:
                        if ref_path not in ref_path_list:
                            ref_path_list.append(ref_path)
                    elif clip_info:  # add comp or cleanup clip to match timelines
                        if clip_info not in ref_path_list:
                            ref_path_list.append(clip_info)
                            if clip_info not in ref_not_found_list:
                                ref_not_found_list.append(clip_info)

                if self.record_in_check_box.isChecked():
                    rc_in = shot.record_in
                    if not rc_in:
                        raise RuntimeError('%s -> No record in data! Turn off Record In check box.' % shot.name)
                    record_in_list.append([clip_info, start_index, end_index, status, rc_in])

            clip_path_list.sort()
            record_in_list.sort()
            none_path_list.sort()
            plate_path_list.sort()
            plate_not_found_list.sort()
            plate_range_mismatch_list.sort()
            ref_path_list.sort()
            ref_not_found_list.sort()

            existing_clip_names = []
            if self.exclude_clips_in_sel_clips_check_box.isChecked():
                import os
                current_folder = self.resolve_project.GetMediaPool().GetCurrentFolder()
                folders = [current_folder]
                for folder in folders:
                    sub_folders = []
                    for sub_folder in folder.GetSubFolderList():
                        if sub_folder not in sub_folders:
                            sub_folders.append(sub_folder)
                    for sub_folder in sub_folders:
                        if sub_folder not in folders:
                            folders.append(sub_folder)
                existing_clips = []
                for folder in folders:
                    sub_existing_clips = folder.GetClipList()
                    for sub_existing_clip in sub_existing_clips:
                        if sub_existing_clip not in existing_clips:
                            existing_clips.append(sub_existing_clip)
                for existing_clip in existing_clips:
                    clip_name = existing_clip.GetName().split('.')[0]
                    if clip_name not in existing_clip_names:
                        existing_clip_names.append(clip_name)

                remove_clip_info = []
                remove_plate_info = []
                remove_ref_info = []
                for clip_info in clip_path_list:
                    clip_path = os.path.normpath(clip_info[0])
                    clip_name = os.path.basename(clip_path).split('.')[0]
                    if clip_name in existing_clip_names:
                        remove_clip_info.append(clip_info)
                        if self.plus_plates_check_box.isChecked():
                            # TODO: this only works in default File Structure. It must be more generic.
                            shot_code = '_'.join(os.path.basename(clip_path).split('_')[:4])
                            for plate_clip_info in plate_path_list:
                                if os.path.basename(plate_clip_info[0]).startswith(shot_code):
                                    remove_plate_info.append(plate_clip_info)
                                    # assume that plates only have 1 version so break the loop
                                    break
                        if self.plus_refs_check_box.isChecked():
                            # TODO: this only works in default File Structure. It must be more generic.
                            shot_code = '_'.join(os.path.basename(clip_path).split('_')[:4])
                            for ref_clip_info in ref_path_list:
                                if os.path.basename(ref_clip_info).startswith(shot_code):
                                    remove_ref_info.append(ref_clip_info)
                                    break
                for remove_clip in remove_clip_info:
                    clip_path_list.remove(remove_clip)
                    print("clip already exists: %s  -> REMOVED" % os.path.basename(remove_clip[0]))
                for remove_clip in remove_plate_info:
                    plate_path_list.remove(remove_clip)
                    print("clip already exists: %s  -> REMOVED" % os.path.basename(remove_clip[0]))
                for remove_clip in remove_ref_info:
                    ref_path_list.remove(remove_clip)
                    print("clip already exists: %s  -> REMOVED" % os.path.basename(remove_clip[0]))

            if self.sg_location_check_box.isChecked():
                import os
                remove_sg_clip_info = []
                remove_sg_plate_info = []
                remove_sg_ref_info = []
                sg_data = self.get_sg_data(self.location_line_edit.text())
                for clip_info in clip_path_list:
                    clip_path = os.path.normpath(clip_info[0])
                    clip_version_name = os.path.basename(clip_path).split('.')[0]
                    for sg_info in sg_data:
                        if sg_info[0] == clip_version_name:
                            remove_sg_clip_info.append(clip_info)
                            print("clip already submitted: %s  -> REMOVED for SHOTGRID" % clip_version_name)
                            if self.plus_plates_check_box.isChecked():
                                # TODO: Fix DRY. This only works in default File Structure. It must be more generic.
                                shot_code = '_'.join(os.path.basename(clip_path).split('_')[:4])
                                for plate_clip_info in plate_path_list:
                                    if os.path.basename(plate_clip_info[0]).startswith(shot_code):
                                        remove_sg_plate_info.append(plate_clip_info)
                                        # assume that plates only have 1 version so break the loop
                                        break
                            if self.plus_refs_check_box.isChecked():
                                # TODO: Fix DRY. This only works in default File Structure. It must be more generic.
                                shot_code = '_'.join(os.path.basename(clip_path).split('_')[:4])
                                for ref_clip_info in ref_path_list:
                                    if os.path.basename(ref_clip_info).startswith(shot_code):
                                        remove_sg_ref_info.append(ref_clip_info)
                                        break
                            break
                for remove_sg_clip in remove_sg_clip_info:
                    clip_path_list.remove(remove_sg_clip)
                for remove_plate_clip in remove_sg_plate_info:
                    plate_path_list.remove(remove_plate_clip)
                    plate_base_name = os.path.basename(remove_plate_clip[0])
                    print("plate also removed: %s  -> REMOVED for SHOTGRID" % plate_base_name)
                for remove_ref_clip in remove_sg_ref_info:
                    ref_path_list.remove(remove_ref_clip)
                    print("reference also removed: %s  -> REMOVED for SHOTGRID" % remove_ref_clip)

            if plate_path_list and self.plus_plates_check_box.isChecked():
                if len(clip_path_list) != len(plate_path_list):
                    print('--------------------------------------------------------------------------')
                    print('ERROR: Comp / Plate mismatch! | %i / %i |Contact Supervisor.'
                          % (len(clip_path_list), len(plate_path_list)))
                    print('--------------------------------------------------------------------------')
                    print(clip_path_list)
                    print('--------------------------------------------------------------------------')
                    print(plate_path_list)
                    raise RuntimeError('Comp / Plate mismatch! | %i / %i | Contact Supervisor.'
                                       % (len(clip_path_list), len(plate_path_list)))

                for i in range(0, len(clip_path_list)):
                    try:
                        import os
                        clip_range = [clip_path_list[i][1], clip_path_list[i][2]]
                        plate_range = [plate_path_list[i][1], plate_path_list[i][2]]
                        print('Clip: %s -> Plate: %s' % (clip_range, plate_range))
                        if clip_range != plate_range:
                            plate_range_mismatch_list.append(clip_path_list[i])
                    except IndexError:
                        pass

            if ref_path_list and self.plus_refs_check_box.isChecked():
                if len(clip_path_list) != len(ref_path_list):
                    print('--------------------------------------------------------------------------')
                    print('ERROR: Comp / Reference mismatch! | %i / %i |Contact Supervisor.'
                          % (len(clip_path_list), len(ref_path_list)))
                    print('--------------------------------------------------------------------------')
                    print(clip_path_list)
                    print('--------------------------------------------------------------------------')
                    print(ref_path_list)
                    raise RuntimeError('Comp / Reference mismatch! | %i / %i | Contact Supervisor.'
                                       % (len(clip_path_list), len(ref_path_list)))

            print('--------------------------------------------------------------------------')
            for i in range(0, len(clip_path_list)):
                if plate_path_list and self.plus_plates_check_box.isChecked():
                    print('%s  +  %s' % (clip_path_list[i][0], plate_path_list[i][0]))
                elif ref_path_list and self.plus_refs_check_box.isChecked():
                    print('%s  +  %s' % (clip_path_list[i][0], ref_path_list[i]))
                else:
                    print(clip_path_list[i][0])
            print('--------------------------------------------------------------------------')
            if none_path_list:
                print('------------------------------------------------------OUTPUT NOT FOUND'
                      '---------------------------------------------------------------------')
                for none_path in none_path_list:
                    print(none_path)
                print('-----------------------------------------------------------------------'
                      '--------------------------------------------------------------------')
            if plate_not_found_list:
                print('--------------------------PLATES NOT FOUND--------------------------------')
                for p_path in plate_not_found_list:
                    print(p_path)
                print('--------------------------------------------------------------------------')
            if plate_range_mismatch_list:
                print('-----------------------PLATES RANGE MISMATCH------------------------------')
                for p_path in plate_range_mismatch_list:
                    print(p_path)
                print('--------------------------------------------------------------------------')

            if clip_path_list:
                self.connect_to_resolve()
                media_pool = self.resolve_project.GetMediaPool()

                if not self.just_import_as_media_check_box.isChecked():
                    if not use_current_timeline:
                        timeline_name = self.generate_timeline_name()
                        print("Creating new timeline with name: %s" % timeline_name)
                        timeline = media_pool.CreateEmptyTimeline(timeline_name)
                    else:
                        print("Using current timeline!")

                for clip_info in clip_path_list:
                    clip_path = clip_info[0]
                    start_index = clip_info[1]
                    end_index = clip_info[2]
                    status_name = clip_info[3]
                    print("clip_path  : %s" % clip_path)
                    print("start frame: %s" % start_index)
                    print("end frame  : %s" % end_index)

                    if extension in ['mov', 'mp4']:
                        media_pool_item = media_pool.ImportMedia([clip_path])[0]
                    else:
                        media_pool_item = media_pool.ImportMedia([
                            {
                                "FilePath": clip_path,
                                "StartIndex": start_index,
                                "EndIndex": end_index
                            }
                        ])[0]

                    if not self.just_import_as_media_check_box.isChecked():
                        if include_slates:
                            # include one frame for the slates
                            sub_clip = {
                                "mediaPoolItem": media_pool_item,
                                "startFrame": 0,
                                "endFrame": 0
                            }
                            slate_clip = media_pool.AppendToTimeline([sub_clip])[0]
                            slate_clip.SetClipColor("Orange")

                        if extension in ['mov', 'mp4']:
                            media_pool.AppendToTimeline(media_pool_item)
                        else:
                            media_pool.AppendToTimeline([media_pool_item])

                    # colorize clips based on stalker statuses in UI
                    if status_name == 'Work In Progress':
                        media_pool_item.SetClipColor("Yellow")
                    elif status_name == 'Has Revision':
                        media_pool_item.SetClipColor("Purple")
                    elif status_name == 'Pending Review':
                        media_pool_item.SetClipColor("Teal")
                    elif status_name == 'Completed':
                        media_pool_item.SetClipColor("Green")

                # Fix shot clip names
                if not self.keep_ext_in_clip_names_check_box.isChecked():
                    from anima.env.resolve.shot_tools import ShotManager
                    sm = ShotManager()
                    sm.fix_shot_clip_names()

                # create a new timeline for plates if specified
                if plate_path_list and self.plus_plates_check_box.isChecked():
                    timeline_name = '%s_Plates' % self.generate_timeline_name()
                    print("Creating new timeline with name: %s" % timeline_name)
                    timeline = media_pool.CreateEmptyTimeline(timeline_name)

                    for clip_info in plate_path_list:
                        clip_path = clip_info[0]
                        start_index = clip_info[1]
                        end_index = clip_info[2]
                        if extension in ['mov', 'mp4']:
                            media_pool_item = media_pool.ImportMedia([clip_path])[0]
                            media_pool.AppendToTimeline(media_pool_item)
                        else:
                            media_pool_item = media_pool.ImportMedia([
                                {
                                    "FilePath": clip_path,
                                    "StartIndex": start_index,
                                    "EndIndex": end_index
                                }
                            ])[0]
                            media_pool.AppendToTimeline([media_pool_item])

                # create a new timeline for references if specified
                if ref_path_list and self.plus_refs_check_box.isChecked():
                    timeline_name = '%s_References' % self.generate_timeline_name()
                    print("Creating new timeline with name: %s" % timeline_name)
                    timeline = media_pool.CreateEmptyTimeline(timeline_name)

                    for clip_info in ref_path_list:
                        media_pool_item = media_pool.ImportMedia([clip_info])[0]
                        media_pool.AppendToTimeline(media_pool_item)

            else:
                print('No Outputs found with given specs!')

            # self.create_resolve_timeline_from_clips(timeline_name, clip_path_list)

    def list_shot_update_status(self):
        """checks if shot outputs are updated based on version path modification date
        """
        import os
        import glob
        import time
        import datetime

        start_date = self.start_date.date()
        query_date = datetime.datetime(start_date.year(), start_date.month(), start_date.day())

        shots = self.get_shots_from_ui()

        self.updated_shot_list.clear()

        if shots:
            update_list = []
            t_name = self.task_name_combo_box.currentText()
            from stalker import Task, Version
            for shot in shots:
                print('Checking Shot... - %s' % shot.name)
                task = Task.query.filter(Task.parent == shot).filter(Task.name == t_name).first()
                if not task and t_name == 'Comp':  # try Cleanup task
                    task = Task.query.filter(Task.parent == shot).filter(Task.name == 'Cleanup').first()

                has_valid_status = True
                if self.filter_statuses_check_box.isChecked():
                    if t_name != 'Plate':  # do not check status for plates
                        try:
                            valid_status_names = self.get_valid_statuses_from_ui()
                            if task.status.name not in valid_status_names:
                                print('%s -> %s' % (shot.name, task.status.name))
                                has_valid_status = False
                        except AttributeError:
                            pass

                if has_valid_status is True:
                    if not task:
                        continue

                    if task.versions:
                        last_version = Version.query.filter(Version.task == task).filter(Version.take_name == 'Main') \
                            .order_by(Version.version_number.desc()).first()
                    else:
                        continue

                    try:
                        raw_seconds = os.path.getmtime(last_version.absolute_full_path)

                        local_time = time.localtime(raw_seconds)
                        modification_date = datetime.datetime(local_time.tm_year,
                                                              local_time.tm_mon,
                                                              local_time.tm_mday)

                        if modification_date >= query_date:
                            item_label = '%s - %s : %s > %s' % (
                                task.parent.name,
                                task.name,
                                str(modification_date).split(' ')[0],
                                last_version.updated_by.name
                            )
                            item_data = [item_label, shot.id]

                    except BaseException:
                        continue

            if update_list:
                update_list.sort(key=lambda x: x[0])
                print("update_list: %s" % update_list)
                for item in update_list:
                    self.updated_shot_list.addItem(self.add_data_as_text_to_ui(item[0], item[1]))
            else:
                self.updated_shot_list.addItem('No Updated Shots found after specified date / ui specs.')

    def conform(self):
        """conforms given Stalker Shot instances to a Timeline in Resolve
        """
        shots = self.get_shots_from_ui()
        include_slates = self.slated_check_box.isChecked()
        record_in = self.record_in_check_box.isChecked()
        use_current_timeline = self.use_current_timeline.isChecked()
        sg_check = self.sg_location_check_box.isChecked()
        if record_in:
            self.conform_shots(shots)
        else:
            self.conform_shots_new(shots,
                                   include_slates=include_slates,
                                   use_current_timeline=use_current_timeline,
                                   sg_check=sg_check)

    def conform_updated_shots(self):
        """conforms only updated shots from listWidget in UI
        """
        from stalker import Shot

        shots = []
        include_slates = self.slated_check_box.isChecked()
        record_in = self.record_in_check_box.isChecked()
        use_current_timeline = self.use_current_timeline.isChecked()
        sg_check = self.sg_location_check_box.isChecked()
        for i in range(0, self.updated_shot_list.count()):
            item = self.updated_shot_list.item(i)
            shot_id = self.get_id_from_data_text(item.text())
            shot = Shot.query.get(shot_id)
            if shot:
                shots.append(shot)

        if self.filter_user_check_box.isChecked():
            from stalker import User

            user_shots = []
            user_text = self.user_name_combo_box.currentText()
            user = User.query.filter_by(name=user_text).first()
            for shot in shots:
                for t in shot.children:
                    if t.is_leaf and user in t.resources and shot not in user_shots:
                        user_shots.append(shot)
                        break

            if user_shots:
                shots = user_shots

        if record_in:
            self.conform_shots(shots)
        else:
            self.conform_shots_new(shots,
                                   include_slates=include_slates,
                                   use_current_timeline=use_current_timeline,
                                   sg_check=sg_check)
