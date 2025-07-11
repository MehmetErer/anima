# -*- coding: utf-8 -*-

import os
import nuke
from anima.env.base import EnvironmentBase


class Nuke(EnvironmentBase):
    """the nuke environment class
    """

    name = "nuke%s" % nuke.NUKE_VERSION_MAJOR
    extensions = ['.nk']

    def __init__(self, name='', version=None):
        """nuke specific init
        """
        super(Nuke, self).__init__(name=name, version=version)
        # and add you own modifications to __init__
        # get the root node
        self._root = self.get_root_node()

        self._main_output_node_name = "MAIN_OUTPUT"
        self._output_formats = ['exr', 'mov']

    @classmethod
    def get_root_node(cls):
        """returns the root node of the current nuke session
        """
        return nuke.toNode("root")

    def save_as(self, version, run_pre_publishers=True):
        """"the save action for nuke environment

        uses Nukes own python binding
        """

        # get the current version, and store it as the parent of the new version
        current_version = self.get_current_version()

        # first initialize the version path
        version.update_paths()

        # set the extension to '.nk'
        version.extension = self.extensions[0]

        # set created_with to let the UI show Nuke icon in versions list
        version.created_with = self.name

        # set project_directory
        self.project_directory = os.path.dirname(version.absolute_path)

        # Update color management
        self.update_color_management(version)

        # create the main write node
        self.create_main_write_nodes(version)

        # replace read and write node paths
        self.replace_external_paths()

        # create the path before saving
        try:
            os.makedirs(version.absolute_path)
        except OSError:
            # path already exists OSError
            pass

        # set frame range
        # if this is a shot related task set it to shots resolution
        is_shot_related_task = False
        shot = None
        from stalker import Shot
        for task in version.task.parents:
            if isinstance(task, Shot):
                is_shot_related_task = True
                shot = task
                break

        # set scene fps
        project = version.task.project
        self.set_fps(project.fps)

        # if version.version_number == 1 or (version.parent and version.parent.task != version.task):
        if is_shot_related_task:
            # just set if the frame range is not 1-1
            if shot.cut_in != 1 and shot.cut_out != 1:
                self.set_frame_range(
                    shot.cut_in,
                    shot.cut_out
                )
            imf = shot.image_format
        else:
            imf = project.image_format

        self.set_resolution(image_format=imf)

        nuke.scriptSaveAs(version.absolute_full_path)

        if current_version:
            # update the parent info
            version.parent = current_version

            # update database with new version info
            from stalker.db.session import DBSession
            DBSession.commit()

        return True

    def export_as(self, version):
        """the export action for nuke environment
        """
        # set the extension to '.nk'
        version.update_paths()
        version.extension = self.extensions[0]
        nuke.nodeCopy(version.absolute_full_path)
        return True

    def open(self, version, force=False, representation=None,
             reference_depth=0, skip_update_check=False):
        """the open action for nuke environment
        """
        nuke.scriptOpen(version.absolute_full_path)

        # set the project_directory
        self.project_directory = os.path.dirname(version.absolute_path)

        # TODO: file paths in different OS's should be replaced with the current one
        # Check if the file paths are starting with a string matching one of the
        # OS's project_directory path and replace them with a relative one
        # matching the current OS

        # replace paths
        self.replace_external_paths()

        # update color management settings
        self.update_color_management(version)

        # return True to specify everything was ok and an empty list
        # for the versions those needs to be updated
        from anima.env import empty_reference_resolution
        return empty_reference_resolution()

    def import_(self, version, use_namespace=True):
        """the import action for nuke environment
        """
        nuke.nodePaste(version.absolute_full_path)
        return True

    def get_current_version(self):
        """Finds the Version instance from the current open file.

        If it can't find any then returns None.

        :return: :class:`~oyProjectManager.models.version.Version`
        """
        full_path = self._root.knob('name').value()
        return self.get_version_from_full_path(full_path)

    def get_version_from_recent_files(self):
        """It will try to create a
        :class:`~oyProjectManager.models.version.Version` instance by looking at
        the recent files list.

        It will return None if it can not find one.

        :return: :class:`~oyProjectManager.models.version.Version`
        """
        # use the last file from the recent file list
        i = 1
        while True:
            try:
                full_path = nuke.recentFile(i)
            except RuntimeError:
                # no recent file anymore just return None
                return None
            i += 1

            version = self.get_version_from_full_path(full_path)
            if version is not None:
                return version

    def get_version_from_project_dir(self):
        """Tries to find a Version from the current project directory

        :return: :class:`~oyProjectManager.models.version.Version`
        """
        versions = self.get_versions_from_path(self.project_directory)
        version = None

        if versions:
            version = versions[0]

        return version

    def get_last_version(self):
        """gets the file name from nuke
        """
        version = self.get_current_version()

        # read the recent file list
        if version is None:
            version = self.get_version_from_recent_files()

        # get the latest possible Version instance by using the workspace path
        if version is None:
            version = self.get_version_from_project_dir()

        return version

    def get_frame_range(self):
        """returns the current frame range
        """
        # self._root = self.get_root_node()
        start_frame = int(self._root.knob('first_frame').value())
        end_frame = int(self._root.knob('last_frame').value())
        return start_frame, end_frame

    def set_frame_range(self, start_frame=1, end_frame=100,
                        adjust_frame_range=False):
        """sets the start and end frame range
        """
        self._root.knob('first_frame').setValue(start_frame)
        self._root.knob('last_frame').setValue(end_frame)

    def set_fps(self, fps=25):
        """sets the current fps
        """
        self._root.knob('fps').setValue(fps)

    def get_fps(self):
        """returns the current fps
        """
        return int(self._root.knob('fps').getValue())

    def set_resolution(self, image_format):
        """Sets the resolution of the current scene

        :param image_format: Stalker ImageFormat instance
        """
        # try to get the format first
        found_format = None
        for f in nuke.formats():
            if f.name() == image_format.name:
                found_format = f
                break

        if not found_format:
            # create a new format
            found_format = nuke.addFormat(
                "%s %s" % (image_format.width, image_format.height)
            )
            found_format.setName(image_format.name)

        # set the current format to that value
        root = self.get_root_node()
        root["format"].setValue("%s" % image_format.name)

    def output_node_name_generator(self, file_format):
        return '%s_%s' % (self._main_output_node_name, file_format.upper())

    def get_main_write_nodes(self):
        """Returns the main write nodes in the scene or None.
        """
        all_main_write_nodes = []
        main_saver_node_names = []
        for format in self._output_formats:
            main_saver_node_names.append(self.output_node_name_generator(format))

        for write_node in nuke.allNodes("Write"):
            if write_node.name() == self._main_output_node_name:  # rename old write node
                ext = write_node.knob('file_type').value().strip()
                for format in self._output_formats:
                    if ext == format:
                        write_node.setName(self.output_node_name_generator(format))
                        break
            if write_node.name() in main_saver_node_names:
                all_main_write_nodes.append(write_node)

        return all_main_write_nodes

    def create_main_write_nodes(self, version):
        """creates the default write nodes if there is no one created before.
        """
        # list all missing main write nodes in the current file
        main_write_node_names = []
        for format in self._output_formats:
            main_write_node_names.append(self.output_node_name_generator(format))

        main_write_nodes = self.get_main_write_nodes()

        existing_write_node_names = []
        for write_node in main_write_nodes:
            existing_write_node_names.append(write_node.name())

        # create missing main write nodes
        write_node_names_to_be_created = [x for x in main_write_node_names if x not in existing_write_node_names]
        for write_node_name in write_node_names_to_be_created:
            main_write_node = nuke.nodes.Write()
            main_write_node.setName(write_node_name)
            main_write_nodes.append(main_write_node)

        for main_write_node in main_write_nodes:
            # get the output format
            # output_format_enum = main_write_node.knob('file_type').value().strip()
            output_format_enum = main_write_node.name().split('_')[-1].lower()  # must be a better way of doing this
            if output_format_enum == '' or output_format_enum == 'exr':
                # set it to exr by default
                output_format_enum = 'exr'
                main_write_node.knob('file_type').setValue(output_format_enum)

                # set default attributes
                if int(nuke.NUKE_VERSION_MAJOR) < 13:
                    main_write_node["colorspace"].setValue(1)   # ACES 2065-1
                else:
                    main_write_node["colorspace"].setValue(6)  # ACES 2065-1
                main_write_node["datatype"].setValue(0)     # 16 bit half
                main_write_node["compression"].setValue(1)  # Zip (1 scanline)
                main_write_node["metadata"].setValue(4)  # all metadata
                main_write_node["autocrop"].setValue(1)  # autocrop
                # TODO: Tis is not generic. Fix ASAP.
                if version.task.project.name in ['Helgoland', 'Kein Tier', 'Wolf Hall', 'Castle', 'Drowak', 'Turbulence']:
                    main_write_node["compression"].setValue(3)  # PIZ Wavelet
                    main_write_node["metadata"].setValue(4)  # all metadata
                if version.task.project.name in ['Chaplin Dortlusu']:
                    main_write_node["colorspace"].setValue('Input - ARRI - V3 LogC (EI160) - Wide Gamut')
            elif output_format_enum == 'mov':
                main_write_node.knob('file_type').setValue(output_format_enum)
                main_write_node["colorspace"].setValue('Output - Rec.709')
                # TODO: Tis is not generic. Fix ASAP.
                if version.task.project.name in ['Helgoland', 'Kein Tier']:
                    main_write_node["colorspace"].setValue('ACES - ACES2065-1')
                # create and connect a transform for half res
                # TODO: half res transform node for mov format might be optional
                transform_node_name = 'Scale_mov'
                all_reformat_nodes = nuke.allNodes('Reformat')
                transform_node_exists = False
                for transform_node in all_reformat_nodes:
                    if transform_node.name() == transform_node_name \
                            and transform_node in main_write_node.dependencies():
                        transform_node_exists = True
                        break
                if transform_node_exists is False:
                    transform_node = nuke.Nodes().Reformat()
                    transform_node.setName(transform_node_name)
                    transform_node.setXYpos(main_write_node.xpos(), main_write_node.ypos() - 50)
                    transform_node['type'].setValue('scale')
                    transform_node['scale'].setValue(0.5)
                    transform_node['filter'].setValue('Lanczos4')
                    main_write_node.setInput(0, transform_node)

            # set the output path
            output_file_name = self.get_significant_name(version, include_project_code=False)

            if output_format_enum == 'mov':
                output_file_name = '%s.%s' % (output_file_name, output_format_enum)
            else:
                output_file_name = '%s.####.%s' % (output_file_name, output_format_enum)

            # check if it is a stereo comp
            # if it is enable separate view rendering

            # set the output path
            output_file_full_path = os.path.join(
                version.absolute_path,
                'Outputs',
                version.take_name,
                'v%03d' % version.version_number,
                output_format_enum,
                output_file_name
            ).replace("\\", "/")

            # create the path
            try:
                os.makedirs(
                    os.path.dirname(
                        output_file_full_path
                    )
                )
            except OSError:
                # path already exists
                pass

            # set the output file path
            main_write_node.knob("file").setValue(output_file_full_path)

    def replace_external_paths(self, mode=0):
        """make paths relative to the project dir
        """
        # convert the given path to tcl environment script
        from anima import utils

        def rep_path(path):
            return utils.relpath(self.project_directory, path, "/", "..")

        # get all read nodes
        all_nodes = nuke.allNodes()

        read_nodes = [node for node in all_nodes if node.Class() == "Read"]
        write_nodes = [node for node in all_nodes if node.Class() == "Write"]
        read_geo_nodes = [node for node in all_nodes if node.Class() == "ReadGeo"]
        read_geo2_nodes = [node for node in all_nodes if node.Class() == "ReadGeo2"]
        write_geo_nodes = [node for node in all_nodes if node.Class() == "WriteGeo"]

        def node_rep(nodes):
            """helper function to replace path values
            """
            [n["file"].setValue(
                rep_path(
                    os.path.expandvars(
                        os.path.expanduser(
                            n["file"].getValue()
                        )
                    ).replace('\\', '/')
                )
            ) for n in nodes]

        node_rep(read_nodes)
        node_rep(write_nodes)
        node_rep(read_geo_nodes)
        node_rep(read_geo2_nodes)
        node_rep(write_geo_nodes)

    @property
    def project_directory(self):
        """The project directory.

        Set it to the project root, and set all your paths relative to this
        directory.
        """
        root = self.get_root_node()

        # TODO: root node gets lost, fix it
        # there is a bug in Nuke, the root node get lost time to time find
        # the source and fix it.
        #        if root is None:
        #            # there is a bug about Nuke,
        #            # sometimes it losses the root node, while it shouldn't
        #            # I can't find the source
        #            # so instead of using the root node,
        #            # just return the os.path.dirname(version.path)
        #
        #            return os.path.dirname(self.version.path)

        return root["project_directory"].getValue()

    @project_directory.setter
    def project_directory(self, project_directory_in):

        project_directory_in = project_directory_in.replace("\\", "/")

        root = self.get_root_node()
        root["project_directory"].setValue(project_directory_in)

    def create_slate_info(self):
        """Returns info about the current shot which will contribute to the
        shot slate

        :return: string
        """

        version = self.get_current_version()
        shot = version.task

        # create a jinja2 template
        import jinja2
        template = jinja2.Template("""Project: {{shot.project.name}}
Shot: {{shot.name}}
Frame Range: {{shot.cut_in}}-{{shot.cut_out}}
Handles: +{{shot.handle_at_start}}, -{{shot.handle_at_end}}
Artist: {% for resource in shot.resources %}{{resource.name}}{%- if loop.index != 1%}, {% endif -%}{% endfor %}
Version: v{{'%03d'|format(version.version_number)}}
Status: {{version.task.status.name}}
        """)

        template_vars = {
            "shot": shot,
            "version": version
        }

        return template.render(**template_vars)

    def update_color_management(self, version):
        """updates color management
        """
        root = self.get_root_node()
        if int(nuke.NUKE_VERSION_MAJOR) < 13:
            root["colorManagement"].setValue(1)  # OCIO
            # root["OCIO_config"].setValue(6)      # Custom
            # root["OCIOConfigPath"].setValue("[getenv ANIMA_DEV_PATH]/OpenColorIO-Configs/aces_1.1/config.ocio")
            root["workingSpaceLUT"].setValue(0)  # ACES 2065-1
            root["monitorLut"].setValue(0)       # sRGB 5
            root["int8Lut"].setValue(148)        # Utility - sRGB - Texture
            root["int16Lut"].setValue(148)       # Utility - sRGB - Texture
            root["logLut"].setValue(5)           # Input - ADX - ADX10
            root["floatLut"].setValue(0)         # ACES 2065-1
        else:
            root["colorManagement"].setValue(1)  # OCIO
            root["workingSpaceLUT"].setValue(9)  # scene linear ACEScg
            root["monitorLut"].setValue(0)  # sRGB
            root["int8Lut"].setValue(6)  # Utility - sRGB - Texture
            root["int16Lut"].setValue(5)  # Utility - sRGB - Texture
            root["logLut"].setValue(3)  # Input - ADX - ADX10
            root["floatLut"].setValue(5)  # ACES 2065-1
            # TODO: Tis is not generic. Fix ASAP.
            if version.task.project.name in ['Chaplin Dortlusu']:
                root["colorManagement"].setValue(1)  # OCIO
                root["workingSpaceLUT"].setValue(2)  # ACEScg
                root["monitorLut"].setValue(0)  # sRGB
                root["int8Lut"].setValue(6)  # Utility - sRGB - Texture
                root["int16Lut"].setValue(5)  # Utility - sRGB - Texture
                root["logLut"].setValue(3)  # Input - ADX - ADX10
                root["floatLut"].setValue('Input - ARRI - V3 LogC (EI160) - Wide Gamut')
            if version.task.project.name in ['Cappy']:
                root["colorManagement"].setValue(1)  # OCIO
                root["workingSpaceLUT"].setValue(2)  # ACEScg
                root["monitorLut"].setValue(0)  # sRGB
                root["int8Lut"].setValue(6)  # Utility - sRGB - Texture
                root["int16Lut"].setValue(5)  # Utility - sRGB - Texture
                root["logLut"].setValue(3)  # Input - ADX - ADX10
                root["floatLut"].setValue('Utility - sRGB - Texture')
